---
name: dashboard-querying
description: Data fetching strategy for dashboards - API endpoint testing, dynamic vs static data, authentication handling. Referenced by dashboard-builder skill. Do not use directly - use dashboard-builder instead.
---

# Dashboard Querying

Determine how to fetch data for dashboards: dynamic API or static embedding.

## Decision Workflow

```
1. Test API endpoint availability
   │
   ├── HTTP 200 → Use Dynamic Fetching
   │
   └── Error (4xx/5xx/timeout) → Use Static Data
```

## Testing the API

Before generating the dashboard, test if the API is accessible:

```bash
curl -s -o /dev/null -w "%{http_code}" \
  "${BROWSER_API_URL}/api/workspace/${HEXA_WORKSPACE}/database/${WORKSPACE_DATABASE_DB_NAME}/table/{table_name}/"
```

If the response is `200`, use dynamic fetching. Otherwise, embed static data.

## API Endpoint Format

**URL Pattern:**
```
${BROWSER_API_URL}/api/workspace/${HEXA_WORKSPACE}/database/${WORKSPACE_DATABASE_DB_NAME}/table/{table_name}/
```

Replace `{table_name}` with the actual table name.

**Query Parameters:**
- `limit` - Number of rows to return (default: 10000)
- `offset` - Starting row for pagination

## Dynamic Fetching (API Works)

### Fetch Function

```javascript
const API_BASE = '${BROWSER_API_URL}';
const WORKSPACE = '${HEXA_WORKSPACE}';
const DATABASE = '${WORKSPACE_DATABASE_DB_NAME}';

async function fetchTableData(tableName, limit = 10000) {
    const url = `${API_BASE}/api/workspace/${WORKSPACE}/database/${DATABASE}/table/${tableName}/?limit=${limit}`;

    try {
        const response = await fetch(url, {
            credentials: 'include'  // Use cookies for authentication
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const json = await response.json();
        return json.data;  // Array of row objects
    } catch (error) {
        console.error('Failed to fetch data:', error);
        return null;
    }
}
```

### API Response Structure

```json
{
    "data": [
        {"col1": "value1", "col2": "value2"},
        {"col1": "value3", "col2": "value4"}
    ],
    "table": "table_name",
    "workspace": "${HEXA_WORKSPACE}",
    "database": "${WORKSPACE_DATABASE_DB_NAME}"
}
```

Access the data array: `response.data`

### Authentication

**Use cookie-based authentication:**
```javascript
fetch(url, {
    credentials: 'include'  // Required - sends session cookies
});
```

**Do NOT use:**
- Token headers
- Authorization headers
- API keys

### Multiple Tables

```javascript
async function loadDashboardData() {
    const [salesData, regionData, productData] = await Promise.all([
        fetchTableData('sales'),
        fetchTableData('regions'),
        fetchTableData('products')
    ]);

    return { salesData, regionData, productData };
}
```

### Error Handling

```javascript
async function fetchWithFallback(tableName, fallbackData) {
    const data = await fetchTableData(tableName);
    if (data === null) {
        console.warn(`Using fallback data for ${tableName}`);
        return fallbackData;
    }
    return data;
}
```

## Static Data (API Unavailable)

When the API is not accessible from the browser, embed data directly in the HTML.

### Embedding Static Data

```html
<script>
// Static data embedded at build time
const DASHBOARD_DATA = {
    sales: [
        {"date": "2024-01", "amount": 15000, "region": "North"},
        {"date": "2024-02", "amount": 18500, "region": "South"},
        // ... more rows
    ],
    regions: [
        {"name": "North", "lat": 45.5, "lon": -73.5},
        {"name": "South", "lat": 25.7, "lon": -80.2}
    ]
};

// Use the same interface as dynamic fetching
function getData(tableName) {
    return DASHBOARD_DATA[tableName] || [];
}
</script>
```

### When to Use Static

- API returns non-200 status
- CORS issues prevent browser access
- Data doesn't change frequently
- Offline dashboard needed
- Performance-critical (no network latency)

### Generating Static Data

To generate static data for embedding:

1. Query the database directly (using MCP tools)
2. Format as JSON
3. Embed in the HTML `<script>` tag
4. Keep data size reasonable (<1MB for good performance)

## Loading States

### Show Loading Indicator

```javascript
async function initDashboard() {
    // Show loading
    document.getElementById('loading').classList.remove('hidden');

    try {
        const data = await fetchTableData('my_table');
        renderCharts(data);
    } catch (error) {
        showError('Failed to load data');
    } finally {
        // Hide loading
        document.getElementById('loading').classList.add('hidden');
    }
}
```

### Loading HTML

```html
<div id="loading" class="fixed inset-0 bg-white/80 flex items-center justify-center z-50">
    <div class="text-center">
        <div class="animate-spin w-10 h-10 border-4 border-[#ED4B82] border-t-transparent rounded-full mx-auto mb-4"></div>
        <p class="text-[#1E3A5F]">Loading dashboard...</p>
    </div>
</div>
```

## Data Transformation

### Common Aggregations

```javascript
// Group by category
function groupBy(data, key) {
    return data.reduce((acc, row) => {
        const group = row[key];
        if (!acc[group]) acc[group] = [];
        acc[group].push(row);
        return acc;
    }, {});
}

// Sum values
function sumBy(data, valueKey) {
    return data.reduce((sum, row) => sum + (row[valueKey] || 0), 0);
}

// Prepare for ECharts series
function toChartSeries(data, categoryKey, valueKey) {
    const grouped = groupBy(data, categoryKey);
    return Object.entries(grouped).map(([name, rows]) => ({
        name,
        value: sumBy(rows, valueKey)
    }));
}
```

### Date Handling

```javascript
// Parse and format dates
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short'
    });
}

// Sort by date
data.sort((a, b) => new Date(a.date) - new Date(b.date));
```

## Limit Recommendation

**Always set limit to 10000** for initial fetch:

```javascript
fetchTableData('large_table', 10000)
```

For very large datasets, consider:
- Server-side aggregation
- Pagination with user controls
- Summary statistics only

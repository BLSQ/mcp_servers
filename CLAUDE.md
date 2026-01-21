**DO NOT** try to write files directly to /home/jovyan/workspace - use the dashboards subdirectory instead.

## Workspace Configuration (USE THESE EXACT VALUES)

These are the actual values for this workspace - use them directly in your code:

- **Workspace slug**: `test`
- **Database name**: `lk96bwqzm1jz2mpk`
- **API base URL**: `http://localhost:8001`
- **Dashboards directory**: `/home/jovyan/workspace/dashboards`

## Dashboard Creation Guidelines

When creating HTML dashboards:
- Use ECharts JS for charts
- Use gridstack library (charts must be movable and resizable by the user on the frontend)
- Use Tailwind CSS for responsive design
- Fetch data from the OpenHEXA database API
- **Save all files to: /home/jovyan/workspace/dashboards/**
  
## Chart Sizing Guidelines

- Use gridstack's responsive grid system to auto-size charts
- Consider the number of charts and screen real estate
- For 1-2 charts: use full width or half width each
- For 3-4 charts: use a 2x2 grid layout
- For 5+ charts: use a responsive grid that adapts to content
- Set minimum heights to ensure charts are readable (at least 300px)
- Use \`autoResize: true\` in ECharts options so charts adapt to container size
- Add window resize handlers to redraw charts when window size changes

  ### HTML Structure:                                                                                                                                                 
  - Use grid-stack-item class on widget containers (not gs-item)                                                                                            
  - Use grid-stack-item-content class for the inner content wrapper                                                                                         
  - Add gs-min-h and gs-min-w attributes to prevent charts from becoming too small (minimum 3 recommended)                                                  
  - Place a drag handle element (like card title) inside each widget                                                                                                                                                                                                                                                          
  ### GridStack Initialization:                                                                                                                                       
  - Always set float: true to enable free positioning of widgets                                                                                            
  - Configure draggable.handle to specify which element triggers dragging (e.g., .card-title)                                                               
  - Configure resizable.handles to enable resize from edges and corners                                                                                                                                                                                                                                                 
  ### Resize Handling:                                                                                                                                                
  - Use ResizeObserver to detect container size changes and trigger chart resize                                                                            
  - Listen to GridStack events (resizestop, change, dragstop) and call chart resize after each                                                              
  - Use setTimeout with small delay (50ms) before resizing to let DOM settle                                                                                        
  ### Visual Feedback:                                                                                                                                                
  - Style resize handles to be visible (border lines on corners/edges)                                                                                      
  - Add cursor: move to drag handles                                                                                                                        
  - Consider adding a drag indicator icon (like ⋮⋮) on draggable elements                                                                                    
  - Add hover effects on resize handles for better discoverability                                                                                          
  - Include a hint text telling users they can drag and resize charts 
## API Endpoint Format

**Use this exact URL pattern** (with the actual values already filled in):

```
http://localhost:8001/api/workspace/test/database/lk96bwqzm1jz2mpk/table/{table_name}/
```

Replace `{table_name}` with the actual table name from the database.

### API ENDPOINT PATTERN:
**Example fetch code:**
Always set by default limit to 10000.
```javascript
// Fetch data from OpenHEXA API
const API_BASE = '$BROWSER_API_URL';
const WORKSPACE = '$HEXA_WORKSPACE';
const DATABASE = '${WORKSPACE_DATABASE_DB_NAME:-$HEXA_WORKSPACE}';

async function fetchTableData(tableName) {
    const url = \\\`\\\${API_BASE}/api/workspace/\\\${WORKSPACE}/database/\\\${DATABASE}/table/\\\${tableName}/?limit=10000\\\`;
    const response = await fetch(url, {
        credentials: 'include'  // Use cookies for authentication
    });
    const json = await response.json();
    // Access the data array from the response
    return json.data;  // Returns array of row objects [{col1: val1, col2: val2, ...}, ...]
}

```

The API returns JSON with this structure:
```json
{
    "data": [
        {"col1": "value1", "col2": "value2", ..., "colN": "valueN"},
        {"col1": "value1", "col2": "value2", ..., "colN": "valueN"},
        ...
    ],
    "table": "table_name",
    "workspace": "$HEXA_WORKSPACE",
    "database": "${WORKSPACE_DATABASE_DB_NAME:-$HEXA_WORKSPACE}"
}
```
 


## Important Notes

- Use `credentials: 'include'` for cookie-based authentication (no TOKEN header needed)
- Always set the limit to 10000
- The API returns JSON data that you can use directly in ECharts
- If creating map visualizations, check for lat/lon/geolocation columns
- For world maps, use: "https://cdn.jsdelivr.net/npm/echarts-map@3.0.1/json/world.json"
- Think about useful filters for the dashboard
- Verify HTML syntax before saving

## Example Tasks

- "List all datasets in my workspace"
- "Show me the tables in my database"
- "Create a dashboard showing data from the {table_name} table"
- "Query the database for recent records"

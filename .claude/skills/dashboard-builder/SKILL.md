---
name: dashboard-builder
description: Orchestrator for creating interactive HTML dashboards in OpenHexa. Use when users ask to create a dashboard, build a dashboard, make a visualization dashboard, display data in charts, or create visual reports. This skill coordinates the technical stack, data querying, maps, and branding skills to produce complete, professional dashboards.
---

# Dashboard Builder

Create interactive HTML dashboards for OpenHexa workspaces.

## Workflow

Follow these steps in order when creating a dashboard:

1. **Read branding guidelines** → Load `openhexa-branding` skill for colors and theme
2. **Read technical stack** → Load `dashboard-technical-stack` skill for GridStack/ECharts/Tailwind setup
3. **Determine data source** → Load `dashboard-querying` skill to test API and decide dynamic vs static
4. **If maps needed** → Load `dashboard-maps` skill for geographic visualizations
5. **Generate dashboard** → Write the complete HTML file

## Workspace Configuration

Use these environment variables in generated code:

| Variable | Usage |
|----------|-------|
| `${HEXA_WORKSPACE}` | Workspace slug for API calls |
| `${WORKSPACE_DATABASE_DB_NAME}` | Database name for API calls |
| `${BROWSER_API_URL}` | Base URL for API endpoints |
| `${DASHBOARDS_DIR}` | Directory to save dashboard files |

## File Output Location

**Always save dashboard files to:**
```
${DASHBOARDS_DIR}/
```

## Dashboard Creation Checklist

Before generating, ensure:

- [ ] Branding colors applied (read `openhexa-branding`)
- [ ] GridStack configured for drag/resize (read `dashboard-technical-stack`)
- [ ] ECharts properly sized and responsive (read `dashboard-technical-stack`)
- [ ] Data fetching method determined (read `dashboard-querying`)
- [ ] Maps configured if geographic data present (read `dashboard-maps`)
- [ ] File saved to correct location (`${DASHBOARDS_DIR}`)
- [ ] HTML syntax verified

## Quick Reference

### Required Libraries (CDN)

```html
<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- GridStack -->
<link href="https://cdn.jsdelivr.net/npm/gridstack@10/dist/gridstack.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/gridstack@10/dist/gridstack-all.min.js"></script>

<!-- ECharts -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
```

### Minimal Dashboard Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Title</title>
    <!-- Include CDN libraries here -->
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header with branding -->
    <header class="bg-[#1E3A5F] text-white py-4 px-6">
        <h1 class="text-xl font-semibold">Dashboard Title</h1>
    </header>

    <!-- GridStack container -->
    <div class="grid-stack p-4">
        <!-- Widgets added here -->
    </div>

    <!-- Footer -->
    <footer class="bg-[#FDF2F8] py-4 px-6 text-sm text-[#1E3A5F]">
        Generated with OpenHexa
    </footer>

    <script>
        // Initialize GridStack and charts
    </script>
</body>
</html>
```

## Example Tasks

- "Create a dashboard showing data from the {table_name} table"
- "Build a dashboard with charts for sales data"
- "Make a visualization dashboard for health indicators"
- "Create a map dashboard showing regional data"

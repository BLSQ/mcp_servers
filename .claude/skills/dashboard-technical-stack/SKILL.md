---
name: dashboard-technical-stack
description: Technical implementation guide for dashboard components including GridStack (drag/resize), ECharts (charts), and Tailwind CSS (styling). Referenced by dashboard-builder skill. Do not use directly - use dashboard-builder instead.
---

# Dashboard Technical Stack

Technical specifications for GridStack, ECharts, and Tailwind CSS integration.

## GridStack Configuration

### Initialization

```javascript
const grid = GridStack.init({
    float: true,                    // Enable free positioning
    cellHeight: 80,                 // Height of each grid cell in pixels
    draggable: {
        handle: '.card-title'       // Only drag from title element
    },
    resizable: {
        handles: 'se,sw,ne,nw,e,w,n,s'  // All edges and corners
    }
});
```

### Adding Widgets

```javascript
grid.addWidget({
    w: 6,           // Width in grid units (12 = full width)
    h: 4,           // Height in grid units
    minW: 3,        // Minimum width (prevent too small)
    minH: 3,        // Minimum height (prevent too small)
    content: `
        <div class="grid-stack-item-content">
            <div class="card-title">Chart Title ⋮⋮</div>
            <div class="chart-wrapper">
                <div id="chart1" class="chart-container"></div>
            </div>
        </div>
    `
});
```

### Layout Recommendations

| Charts | Layout | Widget Size |
|--------|--------|-------------|
| 1-2 | Full or half width | w: 12 or w: 6, h: 5 |
| 3-4 | 2x2 grid | w: 6, h: 4 |
| 5+ | Distribute evenly | w: 4-6, h: 3-4 |

Minimum widget height: 3-4 grid units to ensure readability.

## CSS Structure (Critical)

### Required Styles

```css
/* GridStack item content - flex container */
.grid-stack-item-content {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: white;
    border-radius: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    overflow: hidden;
}

/* Drag handle styling */
.card-title {
    padding: 0.75rem 1rem;
    font-weight: 600;
    color: #1E3A5F;
    cursor: move;
    border-bottom: 1px solid #f3f4f6;
    flex-shrink: 0;
}

/* Chart wrapper - takes remaining space */
.chart-wrapper {
    flex: 1;
    min-height: 0;
    position: relative;
    padding: 0.5rem;
}

/* ECharts container - absolute positioning required */
.chart-container {
    position: absolute;
    top: 0.5rem;
    left: 0.5rem;
    right: 0.5rem;
    bottom: 0.5rem;
}

/* Resize handle visibility */
.grid-stack-item:hover .ui-resizable-handle {
    opacity: 1;
}

.ui-resizable-handle {
    opacity: 0;
    transition: opacity 0.2s;
}
```

### Why Absolute Positioning?

Percentage heights (`height: 100%`) don't work reliably in dynamically-sized flex containers. Use absolute positioning on the ECharts div to ensure it fills the available space.

## ECharts Integration

### Chart Initialization

```javascript
function initChart(containerId, option) {
    const container = document.getElementById(containerId);
    const chart = echarts.init(container);
    chart.setOption(option);

    // Store reference for resize handling
    container._echartInstance = chart;

    // ResizeObserver for automatic resizing
    const observer = new ResizeObserver(() => {
        setTimeout(() => chart.resize(), 50);
    });
    observer.observe(container);

    return chart;
}
```

### Theme Configuration (OpenHexa Branding)

```javascript
const chartOption = {
    color: ['#ED4B82', '#4361EE', '#F472B6', '#6366F1', '#1E3A5F'],
    backgroundColor: 'transparent',
    textStyle: {
        color: '#1E3A5F',
        fontFamily: 'Inter, system-ui, sans-serif'
    },
    title: {
        textStyle: { color: '#1E3A5F', fontSize: 16, fontWeight: 600 }
    },
    tooltip: {
        backgroundColor: '#FFFFFF',
        borderColor: '#ED4B82',
        textStyle: { color: '#1E3A5F' }
    },
    legend: {
        textStyle: { color: '#1E3A5F' }
    },
    xAxis: {
        axisLine: { lineStyle: { color: '#E5E7EB' } },
        axisLabel: { color: '#1E3A5F' },
        splitLine: { lineStyle: { color: '#F3F4F6' } }
    },
    yAxis: {
        axisLine: { lineStyle: { color: '#E5E7EB' } },
        axisLabel: { color: '#1E3A5F' },
        splitLine: { lineStyle: { color: '#F3F4F6' } }
    }
};
```

## Resize Handling

### GridStack Events

```javascript
// Resize all charts after GridStack operations
function resizeAllCharts() {
    document.querySelectorAll('.chart-container').forEach(container => {
        if (container._echartInstance) {
            setTimeout(() => container._echartInstance.resize(), 100);
        }
    });
}

// Listen to GridStack events
grid.on('resizestop', resizeAllCharts);
grid.on('dragstop', resizeAllCharts);
grid.on('change', resizeAllCharts);

// Window resize
window.addEventListener('resize', resizeAllCharts);
```

### Delay Reasoning

Use `setTimeout` with 100ms delay before calling `chart.resize()` to let the DOM settle after GridStack operations.

## Visual Feedback

### Drag Indicator

Add a visual hint that elements are draggable:

```html
<div class="card-title">
    <span class="drag-indicator">⋮⋮</span> Chart Title
</div>
```

```css
.drag-indicator {
    opacity: 0.5;
    margin-right: 0.5rem;
    font-size: 0.75rem;
}
```

### User Hint

Add a hint text in the header or as a tooltip:

```html
<p class="text-sm text-gray-500">Drag titles to move • Drag corners to resize</p>
```

## Tailwind CSS Usage

### Responsive Classes

```html
<!-- Container with responsive padding -->
<div class="p-2 md:p-4 lg:p-6">

<!-- Hide on mobile -->
<div class="hidden md:block">

<!-- Responsive text -->
<h1 class="text-lg md:text-xl lg:text-2xl">
```

### Brand Colors (from openhexa-branding)

```html
<!-- Primary pink -->
<button class="bg-[#ED4B82] hover:bg-[#BE185D] text-white">

<!-- Primary blue -->
<a class="text-[#4361EE] hover:text-[#3730A3]">

<!-- Dark blue text -->
<p class="text-[#1E3A5F]">

<!-- Light pink background -->
<div class="bg-[#FDF2F8]">
```

## Complete Widget HTML Template

```html
<div class="grid-stack-item" gs-w="6" gs-h="4" gs-min-w="3" gs-min-h="3">
    <div class="grid-stack-item-content">
        <div class="card-title flex items-center justify-between">
            <span><span class="drag-indicator opacity-50 mr-2">⋮⋮</span>Chart Title</span>
        </div>
        <div class="chart-wrapper">
            <div id="chart1" class="chart-container"></div>
        </div>
    </div>
</div>
```

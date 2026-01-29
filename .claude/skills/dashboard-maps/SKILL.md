---
name: dashboard-maps
description: Guide for creating map visualizations in dashboards. Covers geographic data detection, shape-based maps (polygons/GeoJSON), point-based maps (lat/lon coordinates), and world map backgrounds. Referenced by dashboard-builder skill. Do not use directly - use dashboard-builder instead.
---

# Dashboard Maps

Create geographic visualizations with ECharts maps.

## Detecting Geographic Data

### Column Name Patterns

Search for columns matching these patterns:

| Type | Column Names |
|------|--------------|
| Latitude | `lat`, `latitude`, `y`, `lat_coord`, `geo_lat` |
| Longitude | `lon`, `lng`, `longitude`, `x`, `lon_coord`, `geo_lon` |
| Combined | `geolocation`, `coordinates`, `geo`, `location`, `geometry` |
| Shapes | `polygon`, `shape`, `boundary`, `geojson`, `geometry` |
| Region | `region`, `district`, `country`, `province`, `admin_level` |

### Inspecting Data Values

After fetching sample data, check the actual values:

```javascript
// Check if values look like coordinates
const sample = data[0];
const hasLatLon = (
    (typeof sample.lat === 'number' && Math.abs(sample.lat) <= 90) &&
    (typeof sample.lon === 'number' && Math.abs(sample.lon) <= 180)
);

// Check if values are GeoJSON or WKT
const hasShapes = (
    typeof sample.geometry === 'string' &&
    (sample.geometry.startsWith('{') || sample.geometry.startsWith('POLYGON'))
);
```

## Map Type Decision

```
Geographic data detected?
├── YES: Contains shapes (polygons/GeoJSON)?
│   ├── YES → Use Shape-Based Map (choropleth)
│   └── NO: Contains lat/lon points?
│       ├── YES → Use Point-Based Map with world background
│       └── NO → Cannot create map
└── NO → Cannot create map
```

## Shape-Based Maps (Choropleth)

Use when data contains polygon geometries (boundaries, regions).

### GeoJSON Registration

```javascript
// Register custom GeoJSON
echarts.registerMap('customMap', geoJsonData);

const option = {
    geo: {
        map: 'customMap',
        roam: true,  // Enable zoom/pan
        itemStyle: {
            areaColor: '#FDF2F8',
            borderColor: '#ED4B82'
        },
        emphasis: {
            itemStyle: {
                areaColor: '#F472B6'
            }
        }
    },
    series: [{
        type: 'map',
        map: 'customMap',
        data: [
            { name: 'Region A', value: 100 },
            { name: 'Region B', value: 200 }
        ]
    }]
};
```

### Converting Data to GeoJSON

If shapes are in WKT format or separate columns:

```javascript
function toGeoJSON(data) {
    return {
        type: 'FeatureCollection',
        features: data.map(row => ({
            type: 'Feature',
            properties: {
                name: row.name,
                value: row.value
            },
            geometry: typeof row.geometry === 'string'
                ? JSON.parse(row.geometry)
                : row.geometry
        }))
    };
}
```

## Point-Based Maps

Use when data contains latitude/longitude coordinates without shapes.

### World Map Background

Load the world map GeoJSON:

```javascript
// Fetch world map
const worldMap = await fetch('https://cdn.jsdelivr.net/npm/echarts-map@3.0.1/json/world.json')
    .then(r => r.json());
echarts.registerMap('world', worldMap);
```

### Scatter Map Configuration

```javascript
const option = {
    geo: {
        map: 'world',
        roam: true,
        itemStyle: {
            areaColor: '#F3F4F6',
            borderColor: '#E5E7EB'
        },
        emphasis: {
            itemStyle: {
                areaColor: '#FDF2F8'
            }
        }
    },
    series: [{
        type: 'scatter',
        coordinateSystem: 'geo',
        data: data.map(row => ({
            name: row.name,
            value: [row.lon, row.lat, row.value],  // [longitude, latitude, value]
            itemStyle: {
                color: '#ED4B82'
            }
        })),
        symbolSize: function(val) {
            return Math.max(6, Math.min(30, val[2] / 10));  // Size based on value
        },
        encode: {
            value: 2
        }
    }],
    tooltip: {
        formatter: function(params) {
            return `${params.name}<br/>Value: ${params.value[2]}`;
        }
    }
};
```

### Effectscatter for Animated Points

```javascript
series: [{
    type: 'effectScatter',
    coordinateSystem: 'geo',
    data: pointData,
    symbolSize: 10,
    rippleEffect: {
        brushType: 'stroke',
        scale: 3
    },
    itemStyle: {
        color: '#ED4B82'
    }
}]
```

## Visual Mapping (Colors by Value)

```javascript
visualMap: {
    min: 0,
    max: 1000,
    left: 'left',
    top: 'bottom',
    text: ['High', 'Low'],
    calculable: true,
    inRange: {
        color: ['#FDF2F8', '#F472B6', '#ED4B82', '#BE185D']  // Light to dark pink
    }
}
```

## Map Controls

### Zoom and Pan

```javascript
geo: {
    roam: true,           // Enable both zoom and pan
    // OR
    roam: 'move',         // Pan only
    // OR
    roam: 'scale',        // Zoom only

    scaleLimit: {
        min: 0.5,
        max: 10
    },
    center: [0, 20],      // Initial center [lon, lat]
    zoom: 1.5             // Initial zoom level
}
```

### Reset View Button

```html
<button onclick="resetMapView()" class="bg-[#4361EE] text-white px-3 py-1 rounded">
    Reset View
</button>

<script>
function resetMapView() {
    chart.setOption({
        geo: { center: [0, 20], zoom: 1.5 }
    });
}
</script>
```

## Complete Map Example

```javascript
async function createMap(containerId, data) {
    // Load world map background
    const worldGeo = await fetch('https://cdn.jsdelivr.net/npm/echarts-map@3.0.1/json/world.json')
        .then(r => r.json());
    echarts.registerMap('world', worldGeo);

    const chart = echarts.init(document.getElementById(containerId));

    chart.setOption({
        backgroundColor: 'transparent',
        geo: {
            map: 'world',
            roam: true,
            itemStyle: {
                areaColor: '#F3F4F6',
                borderColor: '#E5E7EB'
            }
        },
        tooltip: {
            trigger: 'item'
        },
        visualMap: {
            min: 0,
            max: Math.max(...data.map(d => d.value)),
            inRange: { color: ['#FDF2F8', '#ED4B82'] },
            calculable: true
        },
        series: [{
            type: 'scatter',
            coordinateSystem: 'geo',
            data: data.map(d => ({
                name: d.name,
                value: [d.lon, d.lat, d.value]
            })),
            symbolSize: val => Math.sqrt(val[2]) * 2,
            itemStyle: { color: '#ED4B82' }
        }]
    });

    return chart;
}
```

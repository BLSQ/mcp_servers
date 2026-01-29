---
name: openhexa-branding
description: Brand guidelines for OpenHexa and Bluesquare visual identity. Use when creating dashboards, reports, HTML pages, charts, or any visual output that should follow OpenHexa/Bluesquare brand colors and styling. Provides a consistent 5-color palette (pink, blue, white, light pink, dark blue), logo assets, and styling guidelines for ECharts, Tailwind, and general web development.
---

# OpenHexa Branding Guidelines

Apply these guidelines to ensure visual consistency across dashboards, reports, and generated documents.

## Color Palette

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Primary Pink** | `#ED4B82` | rgb(237, 75, 130) | Headers, primary buttons, highlights, chart accent 1 |
| **Primary Blue** | `#4361EE` | rgb(67, 97, 238) | Links, secondary buttons, chart accent 2, icons |
| **White** | `#FFFFFF` | rgb(255, 255, 255) | Backgrounds, text on dark, card backgrounds |
| **Light Pink** | `#FDF2F8` | rgb(253, 242, 248) | Subtle backgrounds, hover states, alternating rows |
| **Dark Blue** | `#1E3A5F` | rgb(30, 58, 95) | Body text, headings, dark backgrounds, footers |

### Extended Chart Palette

For charts requiring more than 2 colors, use this sequence:

```javascript
const chartColors = [
  '#ED4B82',  // Primary Pink
  '#4361EE',  // Primary Blue
  '#F472B6',  // Medium Pink
  '#6366F1',  // Indigo
  '#1E3A5F',  // Dark Blue
  '#F9A8D4',  // Light Pink accent
  '#818CF8',  // Light Indigo
  '#BE185D',  // Deep Pink
];
```

## Logo Assets

Logos are available in `assets/`:

- `logo-openhexa.png` - OpenHexa logo (pink hexagon)
- `bluesquare-logo.svg` - Bluesquare logo (blue with white text)

### Logo Usage in HTML

```html
<!-- OpenHexa logo in header -->
<img src="assets/logo-openhexa.png" alt="OpenHexa" style="height: 40px;">

<!-- Bluesquare logo in footer -->
<img src="assets/bluesquare-logo.svg" alt="Bluesquare" style="height: 24px;">
```

### Logo as Base64 (for standalone HTML)

When creating standalone HTML files, embed logos as base64 to avoid external dependencies. Read the logo files and convert them inline.

## ECharts Configuration

### Default Theme Options

```javascript
const openHexaTheme = {
  color: ['#ED4B82', '#4361EE', '#F472B6', '#6366F1', '#1E3A5F'],
  backgroundColor: '#FFFFFF',
  textStyle: {
    color: '#1E3A5F',
    fontFamily: 'Inter, system-ui, sans-serif'
  },
  title: {
    textStyle: {
      color: '#1E3A5F',
      fontSize: 18,
      fontWeight: 600
    }
  },
  legend: {
    textStyle: {
      color: '#1E3A5F'
    }
  },
  tooltip: {
    backgroundColor: '#FFFFFF',
    borderColor: '#ED4B82',
    textStyle: {
      color: '#1E3A5F'
    }
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

### Applying Theme to Charts

```javascript
// Register and use the theme
echarts.registerTheme('openhexa', openHexaTheme);
const chart = echarts.init(container, 'openhexa');
```

## Tailwind CSS Classes

### Custom Color Configuration

Add to Tailwind config or use inline styles:

```javascript
// tailwind.config.js extension
colors: {
  'oh-pink': '#ED4B82',
  'oh-blue': '#4361EE',
  'oh-dark': '#1E3A5F',
  'oh-light': '#FDF2F8',
}
```

### Common Utility Classes

```html
<!-- Primary button -->
<button class="bg-[#ED4B82] hover:bg-[#BE185D] text-white px-4 py-2 rounded-lg">
  Action
</button>

<!-- Secondary button -->
<button class="bg-[#4361EE] hover:bg-[#3730A3] text-white px-4 py-2 rounded-lg">
  Secondary
</button>

<!-- Card with brand styling -->
<div class="bg-white border border-[#FDF2F8] rounded-xl shadow-sm p-6">
  <h2 class="text-[#1E3A5F] text-xl font-semibold">Card Title</h2>
</div>

<!-- Header bar -->
<header class="bg-[#1E3A5F] text-white py-4 px-6">
  <h1 class="text-xl font-bold">Dashboard Title</h1>
</header>
```

## Dashboard Layout Template

### Standard Header with Logos

```html
<header class="bg-[#1E3A5F] text-white py-4 px-6 flex items-center justify-between">
  <div class="flex items-center gap-4">
    <img src="logo-openhexa.png" alt="OpenHexa" class="h-8">
    <h1 class="text-xl font-semibold">Dashboard Title</h1>
  </div>
  <div class="flex items-center gap-2 text-sm opacity-80">
    <span>Powered by</span>
    <img src="bluesquare-logo.svg" alt="Bluesquare" class="h-5">
  </div>
</header>
```

### Standard Footer

```html
<footer class="bg-[#FDF2F8] border-t border-[#ED4B82]/20 py-4 px-6 mt-auto">
  <div class="flex items-center justify-between text-sm text-[#1E3A5F]">
    <span>Generated with OpenHexa</span>
    <div class="flex items-center gap-2">
      <span>Built by</span>
      <img src="bluesquare-logo.svg" alt="Bluesquare" class="h-4">
    </div>
  </div>
</footer>
```

## Typography

### Font Stack

```css
font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Text Hierarchy

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| H1 | 24px / 1.5rem | 700 | #1E3A5F |
| H2 | 20px / 1.25rem | 600 | #1E3A5F |
| H3 | 16px / 1rem | 600 | #1E3A5F |
| Body | 14px / 0.875rem | 400 | #1E3A5F |
| Caption | 12px / 0.75rem | 400 | #6B7280 |

## KPI Cards

```html
<div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
  <div class="text-sm text-gray-500 mb-1">Total Records</div>
  <div class="text-3xl font-bold text-[#1E3A5F]">12,345</div>
  <div class="text-sm text-[#ED4B82] mt-2">+12% from last month</div>
</div>
```

## Quick Reference

### CSS Variables (for standalone HTML)

```css
:root {
  --oh-pink: #ED4B82;
  --oh-blue: #4361EE;
  --oh-white: #FFFFFF;
  --oh-light: #FDF2F8;
  --oh-dark: #1E3A5F;
  --oh-pink-medium: #F472B6;
  --oh-indigo: #6366F1;
}
```

### Gradient Options

```css
/* Pink gradient (OpenHexa style) */
background: linear-gradient(135deg, #ED4B82 0%, #F472B6 100%);

/* Blue gradient (Bluesquare style) */
background: linear-gradient(135deg, #4361EE 0%, #6366F1 100%);

/* Combined brand gradient */
background: linear-gradient(135deg, #ED4B82 0%, #4361EE 100%);
```

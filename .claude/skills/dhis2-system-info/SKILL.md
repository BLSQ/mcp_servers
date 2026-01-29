---
name: dhis2-system-info
description: Get DHIS2 system information including version, database details, and server configuration. Use for version checks or server capabilities. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 System Info

Get system information, version details, and server configuration from DHIS2.

## Overview

The system info endpoints provide:
- DHIS2 version and build information
- Database type and version
- Server configuration and capabilities
- System settings and flags

## Setup

```python
from openhexa.sdk import workspace
from openhexa.toolbox.dhis2 import DHIS2

# Get DHIS2 connection
dhis2_connection = workspace.dhis2_connection("connection_identifier")
dhis = DHIS2(dhis2_connection, cache_dir=f"{workspace.files_path}/.cache")
```

## Get System Info

```python
def get_system_info(dhis) -> dict:
    """Get complete system information."""
    return dhis.api.get("system/info")

# Usage
info = get_system_info(dhis)

# Key fields
print(f"DHIS2 Version: {info.get('version')}")
print(f"Revision: {info.get('revision')}")
print(f"Build Time: {info.get('buildTime')}")
print(f"Database: {info.get('databaseInfo', {}).get('name')}")
print(f"Server Date: {info.get('serverDate')}")
```

## Common System Info Fields

| Field | Description | Example |
|-------|-------------|---------|
| `version` | DHIS2 version | `2.40.2` |
| `revision` | Build revision | `abc1234` |
| `buildTime` | When built | `2024-01-15T10:30:00.000` |
| `serverDate` | Current server time | `2024-06-15T14:30:00.000` |
| `calendar` | Calendar system | `iso8601`, `ethiopian` |
| `dateFormat` | Date format | `yyyy-MM-dd` |
| `contextPath` | Server context path | `/dhis` |
| `systemId` | Unique system ID | `OU-abc123` |

### Database Info

```python
db_info = info.get("databaseInfo", {})
print(f"DB Name: {db_info.get('name')}")           # e.g., "PostgreSQL"
print(f"DB User: {db_info.get('user')}")           # e.g., "dhis"
print(f"DB URL: {db_info.get('url')}")             # Connection URL
print(f"Spatial Support: {db_info.get('spatialSupport')}")  # True/False
```

## Check Version Compatibility

```python
def check_version(dhis, min_version: str = "2.38") -> bool:
    """Check if DHIS2 version meets minimum requirement."""
    info = dhis.api.get("system/info")
    version = info.get("version", "0.0.0")

    # Parse version (handle formats like "2.40.2" or "2.40.2-SNAPSHOT")
    version_parts = version.split("-")[0].split(".")
    min_parts = min_version.split(".")

    for i in range(min(len(version_parts), len(min_parts))):
        v = int(version_parts[i])
        m = int(min_parts[i])
        if v > m:
            return True
        elif v < m:
            return False

    return True

# Usage
if check_version(dhis, "2.40"):
    print("DHIS2 version is 2.40 or higher")
    # Use newer API features
else:
    print("DHIS2 version is below 2.40")
    # Use legacy API endpoints
```

## Get System Settings

```python
def get_system_settings(dhis, keys: list = None) -> dict:
    """Get system settings."""
    if keys:
        params = {"key": keys}
        return dhis.api.get("systemSettings", params=params)
    return dhis.api.get("systemSettings")

# Get all settings
settings = get_system_settings(dhis)

# Get specific settings
settings = get_system_settings(dhis, keys=[
    "keyAnalyticsMaxLimit",
    "keyDatabaseServerCpus",
    "keySystemNotificationsEmail"
])
```

### Common System Settings

| Key | Description |
|-----|-------------|
| `keyAnalyticsMaxLimit` | Max rows in analytics queries |
| `keyDatabaseServerCpus` | Number of CPUs for analytics |
| `keyIgnoreAnalyticsApprovalYearThreshold` | Approval threshold |
| `keyGoogleAnalyticsUA` | Google Analytics ID |
| `keyStyle` | System UI style |
| `keyFlag` | Country flag |
| `keyApplicationTitle` | Application title |
| `keyEmailHostName` | SMTP host |

## Get Server Capabilities

```python
def get_server_capabilities(dhis) -> dict:
    """Analyze server capabilities based on system info."""
    info = dhis.api.get("system/info")

    return {
        "version": info.get("version"),
        "is_v40_plus": check_version(dhis, "2.40"),
        "is_v38_plus": check_version(dhis, "2.38"),
        "has_tracker_api": check_version(dhis, "2.38"),  # New tracker API
        "has_spatial": info.get("databaseInfo", {}).get("spatialSupport", False),
        "calendar": info.get("calendar"),
        "date_format": info.get("dateFormat"),
        "system_id": info.get("systemId")
    }

# Usage
caps = get_server_capabilities(dhis)
if caps["has_tracker_api"]:
    # Use /api/tracker endpoints
    pass
else:
    # Use legacy /api/trackedEntityInstances endpoints
    pass
```

## Check Analytics Tables Status

```python
def get_analytics_status(dhis) -> dict:
    """Get analytics tables generation status."""
    try:
        status = dhis.api.get("resourceTables/analytics")
        return status
    except:
        return {"status": "unknown"}

# Usage
analytics_status = get_analytics_status(dhis)
print(f"Last analytics update: {analytics_status.get('lastUpdated')}")
```

## Get Server Time

```python
def get_server_time(dhis) -> str:
    """Get current server date/time."""
    info = dhis.api.get("system/info")
    return info.get("serverDate")

# Useful for scheduling and time-based queries
server_time = get_server_time(dhis)
```

## Complete System Report

```python
def generate_system_report(dhis) -> dict:
    """Generate a comprehensive system report."""
    info = get_system_info(dhis)
    settings = get_system_settings(dhis)

    return {
        "instance": {
            "version": info.get("version"),
            "revision": info.get("revision"),
            "build_time": info.get("buildTime"),
            "system_id": info.get("systemId"),
            "context_path": info.get("contextPath")
        },
        "database": {
            "type": info.get("databaseInfo", {}).get("name"),
            "user": info.get("databaseInfo", {}).get("user"),
            "spatial_support": info.get("databaseInfo", {}).get("spatialSupport")
        },
        "localization": {
            "calendar": info.get("calendar"),
            "date_format": info.get("dateFormat")
        },
        "server": {
            "current_time": info.get("serverDate"),
            "java_version": info.get("javaVersion"),
            "os_name": info.get("osName"),
            "os_version": info.get("osArchitecture")
        },
        "settings": {
            "analytics_max_limit": settings.get("keyAnalyticsMaxLimit"),
            "application_title": settings.get("keyApplicationTitle")
        }
    }
```

## Use Cases

| Scenario | What to Check |
|----------|---------------|
| API compatibility | `version`, `check_version()` |
| Spatial queries | `databaseInfo.spatialSupport` |
| Multi-calendar support | `calendar` |
| Data freshness | `serverDate`, analytics status |
| Troubleshooting | Full system report |

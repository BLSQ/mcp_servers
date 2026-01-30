---
name: dhis2-users
description: Get DHIS2 user information including current user details, user lists, and user groups. Use for permissions, org unit access, or user administration. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Users

Access user information, permissions, and organizational access from DHIS2.

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

## Overview

The user endpoints provide:
- Current authenticated user information (`/api/me`)
- User listing and search (`/api/users`)
- User groups and memberships (`/api/userGroups`)
- Organization unit access scope

## Get Current User Info

```python
def get_current_user(dhis, fields: str = "*") -> dict:
    """Get information about the authenticated user."""
    return dhis.api.get("me", params={"fields": fields})

# Basic info
user = get_current_user(dhis)
print(f"Username: {user.get('username')}")
print(f"Name: {user.get('displayName')}")
print(f"Email: {user.get('email')}")

# With specific fields
user = get_current_user(dhis, fields="id,username,displayName,email,organisationUnits[id,name]")
```

## Get User's Organization Units

```python
def get_user_org_units(dhis) -> dict:
    """Get org units the current user has access to."""
    user = dhis.api.get(
        "me",
        params={
            "fields": "organisationUnits[id,name,level],dataViewOrganisationUnits[id,name,level],teiSearchOrganisationUnits[id,name,level]"
        }
    )

    return {
        "data_capture": user.get("organisationUnits", []),
        "data_view": user.get("dataViewOrganisationUnits", []),
        "tei_search": user.get("teiSearchOrganisationUnits", [])
    }

# Usage
org_units = get_user_org_units(dhis)
print(f"Can capture data at: {len(org_units['data_capture'])} org units")
print(f"Can view data at: {len(org_units['data_view'])} org units")
```

## Get User Authorities (Permissions)

```python
def get_user_authorities(dhis) -> list:
    """Get authorities/permissions for current user."""
    user = dhis.api.get("me", params={"fields": "authorities"})
    return user.get("authorities", [])

def check_user_authority(dhis, authority: str) -> bool:
    """Check if user has a specific authority."""
    authorities = get_user_authorities(dhis)
    return authority in authorities or "ALL" in authorities

# Usage
authorities = get_user_authorities(dhis)
print(f"User has {len(authorities)} authorities")

# Check specific permission
if check_user_authority(dhis, "F_EXPORT_DATA"):
    print("User can export data")
```

### Common Authorities

| Authority | Description |
|-----------|-------------|
| `ALL` | Superuser - all permissions |
| `F_EXPORT_DATA` | Export data values |
| `F_VIEW_UNAPPROVED_DATA` | View unapproved data |
| `F_APPROVE_DATA` | Approve data |
| `F_TRACKED_ENTITY_INSTANCE_SEARCH` | Search tracked entities |
| `F_METADATA_EXPORT` | Export metadata |

## List Users

```python
def get_users(dhis, query: str = None, org_unit: str = None, page_size: int = 50) -> list:
    """Get list of users with optional filtering."""
    params = {
        "fields": "id,username,displayName,email,lastLogin,disabled,organisationUnits[id,name]",
        "pageSize": page_size
    }

    if query:
        params["query"] = query
    if org_unit:
        params["ou"] = org_unit

    all_users = []
    page = 1

    while True:
        params["page"] = page
        response = dhis.api.get("users", params=params)

        users = response.get("users", [])
        if not users:
            break

        all_users.extend(users)

        if len(users) < page_size:
            break
        page += 1

    return all_users

# Get all users
users = get_users(dhis)

# Search users
users = get_users(dhis, query="john")

# Users in specific org unit
users = get_users(dhis, org_unit="ImspTQPwCqd")
```

## Get User Groups

```python
def get_user_groups(dhis, fields: str = "id,name,displayName,users::size") -> list:
    """Get all user groups."""
    response = dhis.api.get(
        "userGroups",
        params={"fields": fields, "paging": "false"}
    )
    return response.get("userGroups", [])

def get_user_group_members(dhis, group_id: str) -> list:
    """Get members of a user group."""
    response = dhis.api.get(
        f"userGroups/{group_id}",
        params={"fields": "users[id,username,displayName,email]"}
    )
    return response.get("users", [])

# List all groups
groups = get_user_groups(dhis)
for group in groups:
    print(f"{group['name']}: {group.get('users', 0)} members")

# Get group members
members = get_user_group_members(dhis, "wl5cDMuUhmF")
```

## Get Current User's Groups

```python
def get_my_user_groups(dhis) -> list:
    """Get user groups the current user belongs to."""
    user = dhis.api.get("me", params={"fields": "userGroups[id,name,displayName]"})
    return user.get("userGroups", [])

# Usage
my_groups = get_my_user_groups(dhis)
print(f"Member of {len(my_groups)} groups:")
for group in my_groups:
    print(f"  - {group['name']}")
```

## Check Data Access Scope

```python
def get_data_access_scope(dhis) -> dict:
    """Analyze the current user's data access scope."""
    user = dhis.api.get(
        "me",
        params={
            "fields": "id,username,organisationUnits[id,name,level,path],dataViewOrganisationUnits[id,name,level,path],userRoles[id,name],authorities"
        }
    )

    capture_ous = user.get("organisationUnits", [])
    view_ous = user.get("dataViewOrganisationUnits", [])

    # Determine lowest level accessible
    capture_levels = [ou.get("level", 0) for ou in capture_ous]
    view_levels = [ou.get("level", 0) for ou in view_ous]

    return {
        "username": user.get("username"),
        "data_capture_org_units": len(capture_ous),
        "data_view_org_units": len(view_ous),
        "capture_level_range": (min(capture_levels) if capture_levels else None,
                                max(capture_levels) if capture_levels else None),
        "view_level_range": (min(view_levels) if view_levels else None,
                            max(view_levels) if view_levels else None),
        "user_roles": [r.get("name") for r in user.get("userRoles", [])],
        "is_superuser": "ALL" in user.get("authorities", [])
    }

# Usage
scope = get_data_access_scope(dhis)
print(f"User: {scope['username']}")
print(f"Superuser: {scope['is_superuser']}")
print(f"Can capture data at {scope['data_capture_org_units']} org units")
```

## Get User Activity

```python
def get_user_activity(dhis, user_id: str = None) -> dict:
    """Get user's last login and activity info."""
    if user_id:
        user = dhis.api.get(f"users/{user_id}", params={"fields": "id,username,lastLogin,created"})
    else:
        user = dhis.api.get("me", params={"fields": "id,username,lastLogin,created"})

    return {
        "username": user.get("username"),
        "last_login": user.get("lastLogin"),
        "created": user.get("created")
    }
```

## Users Report (DataFrame)

```python
import pandas as pd

def users_to_df(users: list) -> pd.DataFrame:
    """Convert users list to DataFrame."""
    rows = []
    for user in users:
        rows.append({
            "id": user.get("id"),
            "username": user.get("username"),
            "displayName": user.get("displayName"),
            "email": user.get("email"),
            "lastLogin": user.get("lastLogin"),
            "disabled": user.get("disabled", False),
            "orgUnits": len(user.get("organisationUnits", []))
        })
    return pd.DataFrame(rows)

# Generate user report
users = get_users(dhis)
df = users_to_df(users)
print(f"Total users: {len(df)}")
print(f"Active users: {len(df[~df['disabled']])}")
print(f"Users never logged in: {len(df[df['lastLogin'].isna()])}")
```

## Use Cases

| Scenario | Endpoint/Function |
|----------|-------------------|
| Check my permissions | `get_user_authorities()` |
| What data can I see | `get_user_org_units()` |
| List all users | `get_users()` |
| Find inactive users | `users_to_df()` + filter |
| Audit user access | `get_data_access_scope()` |
| Check group membership | `get_my_user_groups()` |

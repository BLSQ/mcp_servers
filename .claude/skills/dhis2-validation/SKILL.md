---
name: dhis2-validation
description: Run data quality checks and validation rules in DHIS2. Use for validation rules, violations, or data quality analysis. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Validation

Run data quality checks and validation rules in DHIS2.

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

## Overview

The validation endpoints provide:
- **Validation Rules**: Define data quality checks (e.g., "A < B", "Total = Sum of parts")
- **Validation Analysis**: Run rules against data
- **Validation Results**: Historical violations stored in the system
- **Data Quality Reports**: Aggregate validation status

## Get Validation Rules

```python
def get_validation_rules(dhis, fields: str = None) -> list:
    """Get all validation rules."""
    default_fields = "id,name,description,importance,operator,leftSide[expression,description],rightSide[expression,description]"

    response = dhis.api.get(
        "validationRules",
        params={
            "fields": fields or default_fields,
            "paging": "false"
        }
    )
    return response.get("validationRules", [])

# Usage
rules = get_validation_rules(dhis)
print(f"Total validation rules: {len(rules)}")

for rule in rules[:5]:
    print(f"- {rule['name']} ({rule.get('importance', 'MEDIUM')})")
```

### Validation Rule Structure

| Field | Description |
|-------|-------------|
| `name` | Rule display name |
| `description` | What the rule checks |
| `importance` | `HIGH`, `MEDIUM`, `LOW` |
| `operator` | `equal_to`, `not_equal_to`, `greater_than`, `less_than`, etc. |
| `leftSide` | Left expression (data elements/indicators) |
| `rightSide` | Right expression (value/calculation) |
| `periodType` | Applicable period type |

## Get Validation Rule Groups

```python
def get_validation_rule_groups(dhis) -> list:
    """Get validation rule groups."""
    response = dhis.api.get(
        "validationRuleGroups",
        params={
            "fields": "id,name,description,validationRules[id,name]",
            "paging": "false"
        }
    )
    return response.get("validationRuleGroups", [])

# Usage
groups = get_validation_rule_groups(dhis)
for group in groups:
    print(f"{group['name']}: {len(group.get('validationRules', []))} rules")
```

## Run Validation Analysis

```python
def run_validation(
    dhis,
    start_date: str,
    end_date: str,
    org_unit: str,
    validation_rule_group: str = None,
    send_notifications: bool = False
) -> dict:
    """Run validation analysis and get violations."""
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "ou": org_unit,
        "notification": str(send_notifications).lower()
    }

    if validation_rule_group:
        params["vrg"] = validation_rule_group

    response = dhis.api.get("validation/dataAnalysis", params=params)
    return response

# Run validation for a period
violations = run_validation(
    dhis,
    start_date="2024-01-01",
    end_date="2024-03-31",
    org_unit="ImspTQPwCqd"
)

print(f"Found {len(violations)} validation violations")
```

## Validate a Dataset

```python
def validate_dataset(
    dhis,
    dataset_id: str,
    period: str,
    org_unit: str
) -> dict:
    """Validate data for a specific dataset, period, and org unit."""
    response = dhis.api.get(
        f"validation/dataSet/{dataset_id}",
        params={
            "pe": period,
            "ou": org_unit
        }
    )
    return response

# Usage
result = validate_dataset(
    dhis,
    dataset_id="BfMAe6Itzgt",
    period="202401",
    org_unit="ImspTQPwCqd"
)

# Check violations
if result.get("validationRuleViolations"):
    for v in result["validationRuleViolations"]:
        print(f"Rule: {v.get('validationRule', {}).get('name')}")
        print(f"  Left: {v.get('leftsideValue')} {v.get('operator')} Right: {v.get('rightsideValue')}")
```

## Get Historical Validation Results

```python
def get_validation_results(
    dhis,
    org_unit: str = None,
    start_date: str = None,
    end_date: str = None,
    validation_rule: str = None
) -> list:
    """Get stored validation results (violations)."""
    params = {
        "fields": "validationRule[id,name,importance],organisationUnit[id,name],period[id,name],leftsideValue,rightsideValue,created",
        "paging": "false"
    }

    if org_unit:
        params["ou"] = org_unit
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    if validation_rule:
        params["vr"] = validation_rule

    response = dhis.api.get("validationResults", params=params)
    return response.get("validationResults", [])

# Get recent violations
results = get_validation_results(
    dhis,
    org_unit="ImspTQPwCqd",
    start_date="2024-01-01",
    end_date="2024-06-30"
)
```

## Convert Violations to DataFrame

```python
import pandas as pd

def violations_to_df(violations: list) -> pd.DataFrame:
    """Convert validation violations to DataFrame."""
    rows = []
    for v in violations:
        rows.append({
            "rule_id": v.get("validationRule", {}).get("id"),
            "rule_name": v.get("validationRule", {}).get("name"),
            "importance": v.get("validationRule", {}).get("importance"),
            "org_unit_id": v.get("organisationUnit", {}).get("id"),
            "org_unit_name": v.get("organisationUnit", {}).get("name"),
            "period": v.get("period", {}).get("id"),
            "left_value": v.get("leftsideValue"),
            "right_value": v.get("rightsideValue"),
            "created": v.get("created")
        })
    return pd.DataFrame(rows)

# Usage
df = violations_to_df(results)
print(f"Total violations: {len(df)}")
print(f"\nViolations by importance:")
print(df.groupby("importance").size())
print(f"\nViolations by rule:")
print(df.groupby("rule_name").size().sort_values(ascending=False).head(10))
```

## Validation Summary Report

```python
def generate_validation_summary(dhis, org_unit: str, periods: list) -> dict:
    """Generate a validation summary for multiple periods."""
    all_violations = []

    for period in periods:
        try:
            # Try to get results for this period
            violations = run_validation(
                dhis,
                start_date=period,
                end_date=period,
                org_unit=org_unit
            )
            for v in violations:
                v["period"] = period
                all_violations.append(v)
        except Exception as e:
            print(f"Error for period {period}: {e}")

    df = violations_to_df(all_violations) if all_violations else pd.DataFrame()

    return {
        "total_violations": len(df),
        "by_importance": df.groupby("importance").size().to_dict() if len(df) > 0 else {},
        "by_period": df.groupby("period").size().to_dict() if len(df) > 0 else {},
        "by_rule": df.groupby("rule_name").size().to_dict() if len(df) > 0 else {},
        "details": df
    }
```

## Check Specific Validation Rule

```python
def get_rule_violations(dhis, rule_id: str, org_unit: str, periods: list) -> pd.DataFrame:
    """Get violations for a specific validation rule."""
    all_violations = []

    for period in periods:
        results = get_validation_results(
            dhis,
            org_unit=org_unit,
            validation_rule=rule_id,
            start_date=period,
            end_date=period
        )
        all_violations.extend(results)

    return violations_to_df(all_violations)

# Usage
rule_violations = get_rule_violations(
    dhis,
    rule_id="kKXOVY4qPyK",
    org_unit="ImspTQPwCqd",
    periods=["202401", "202402", "202403"]
)
```

## Validation Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `equal_to` | Left = Right | Total = Sum of parts |
| `not_equal_to` | Left ≠ Right | A ≠ B |
| `greater_than` | Left > Right | Stock > 0 |
| `greater_than_or_equal_to` | Left ≥ Right | Births ≥ Live births |
| `less_than` | Left < Right | Deaths < Population |
| `less_than_or_equal_to` | Left ≤ Right | Attended ≤ Registered |
| `compulsory_pair` | If one exists, both must | ANC1 requires ANC visit date |
| `exclusive_pair` | Only one can exist | Male XOR Female |

## Data Quality Dashboard Data

```python
def get_data_quality_metrics(dhis, org_unit: str, period: str) -> dict:
    """Get data quality metrics for dashboard display."""

    # Get all validation rules
    rules = get_validation_rules(dhis)

    # Run validation
    violations = run_validation(
        dhis,
        start_date=period,
        end_date=period,
        org_unit=org_unit
    )

    df = violations_to_df(violations) if violations else pd.DataFrame()

    return {
        "total_rules": len(rules),
        "rules_violated": df["rule_id"].nunique() if len(df) > 0 else 0,
        "total_violations": len(df),
        "high_importance": len(df[df["importance"] == "HIGH"]) if len(df) > 0 else 0,
        "medium_importance": len(df[df["importance"] == "MEDIUM"]) if len(df) > 0 else 0,
        "low_importance": len(df[df["importance"] == "LOW"]) if len(df) > 0 else 0,
        "compliance_rate": (len(rules) - df["rule_id"].nunique()) / len(rules) * 100 if rules else 100
    }
```

## Use Cases

| Scenario | Function |
|----------|----------|
| List all rules | `get_validation_rules()` |
| Run validation check | `run_validation()` |
| Validate specific dataset | `validate_dataset()` |
| Get historical violations | `get_validation_results()` |
| Track specific rule | `get_rule_violations()` |
| Data quality dashboard | `get_data_quality_metrics()` |

## Looker report: API compliance (`refundCreate` or `returnProcess`)

Use this pattern when you want to check if each app is using at least one approved API:

- `refundCreate`
- `returnProcess`

---

### 1) SQL (app-level compliance summary)

Replace `analytics.api_calls` and column names with your real table/fields.

```sql
SELECT
  app_id,
  SUM(CASE WHEN api_name = 'refundCreate' THEN 1 ELSE 0 END) AS refundcreate_calls,
  SUM(CASE WHEN api_name = 'returnProcess' THEN 1 ELSE 0 END) AS returnprocess_calls,
  SUM(CASE WHEN api_name IN ('refundCreate', 'returnProcess') THEN 1 ELSE 0 END) AS approved_api_calls,
  CASE
    WHEN SUM(CASE WHEN api_name IN ('refundCreate', 'returnProcess') THEN 1 ELSE 0 END) > 0
      THEN 'Compliant'
    ELSE 'Non-compliant'
  END AS api_compliance_status
FROM analytics.api_calls
GROUP BY app_id;
```

This gives one row per app with a clear compliance status.

---

### 2) Query to return only non-compliant apps

```sql
SELECT
  app_id
FROM analytics.api_calls
GROUP BY app_id
HAVING SUM(CASE WHEN api_name IN ('refundCreate', 'returnProcess') THEN 1 ELSE 0 END) = 0;
```

---

### 3) Looker custom field formula (row-level check)

If you need a row-level flag in an Explore:

```text
if(${api_name} = "refundCreate" OR ${api_name} = "returnProcess", "Approved API", "Not Approved API")
```

---

### 4) LookML dimension (if you maintain LookML)

```lookml
dimension: approved_api_call {
  type: yesno
  sql: ${api_name} IN ('refundCreate', 'returnProcess') ;;
}
```

Use this dimension in your Explore filters to include only approved API calls or to build compliance dashboards.

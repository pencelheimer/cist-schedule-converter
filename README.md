# CIST Schedule Converter

Small server that converst schedule CSV from cist.nure.ua into modern ICS.

## Endpoints
- `GET /groups` – List all available groups
- `GET /groups/{group_id}/schedule?from=YYYY-MM-DD&to=YYYY-MM-DD[&exclude=SUBJECT]` – Download schedule in `.ics` format

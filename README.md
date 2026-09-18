# CIST Schedule Converter

Small server that converts schedule CSV from `cist.nure.ua` into modern ICS format.

## Endpoints
- `GET /` – Web UI for building schedule URLs
- `GET /groups` – List all available groups
- `GET /groups/{group_id}/schedule?from=YYYY-MM-DD&to=YYYY-MM-DD` – Download schedule in `.ics` format

## Local Run
```bash
just dev
```

## NixOS Deployment (OCI Container)

Add this snippet to your `configuration.nix`:

```nix
virtualisation.oci-containers.containers.cist-schedule-converter = {
  image = "ghcr.io/pencelheimer/cist-schedule-converter:latest";
  ports = [ "8000:8000" ];
  environment = { PORT = "8000"; };
};
```

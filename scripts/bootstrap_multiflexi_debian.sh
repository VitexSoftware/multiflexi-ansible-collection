#!/bin/sh
# Bootstrap or update a Debian container with MultiFlexi CLI and SQLite backend
# Usage: sh scripts/bootstrap_multiflexi_debian.sh [container_name] [image]
# Defaults: container_name=multiflexi-debian, image=debian:12

set -eu

NAME="${1:-multiflexi-debian}"
IMAGE="${2:-debian:12}"

echo "[INFO] Ensuring image present: $IMAGE"
if ! podman image exists "$IMAGE"; then
  podman pull "$IMAGE"
fi

echo "[INFO] Ensuring container exists: $NAME"
if ! podman container exists "$NAME"; then
  podman run --name "$NAME" -itd "$IMAGE" sleep infinity
else
  # Ensure it is running
  if [ "$(podman inspect -f '{{.State.Running}}' "$NAME")" != "true" ]; then
    podman start "$NAME"
  fi
fi

echo "[INFO] Preparing apt in container"
podman exec -it "$NAME" sh -lc "apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg jq"

echo "[INFO] Installing MultiFlexi APT key and source in container"
# Use KEY.gpg (ASCII armored), dearmor to a keyring file and add repo with codename
podman exec -it "$NAME" sh -lc '
  set -e
  curl -fsSL -o /tmp/KEY.gpg https://repo.multiflexi.eu/KEY.gpg
  gpg --dearmor -o /usr/share/keyrings/multiflexi-archive-keyring.gpg /tmp/KEY.gpg
  CODENAME=$(. /etc/os-release; echo "$VERSION_CODENAME")
  echo "deb [signed-by=/usr/share/keyrings/multiflexi-archive-keyring.gpg] https://repo.multiflexi.eu/ ${CODENAME} main" > /etc/apt/sources.list.d/multiflexi.list
  apt-get clean && rm -rf /var/lib/apt/lists/*
  apt-get update
'

echo "[INFO] Installing MultiFlexi CLI and SQLite backend in container"
podman exec -it "$NAME" sh -lc "DEBIAN_FRONTEND=noninteractive apt-get install -y multiflexi-sqlite multiflexi-cli"

echo "[INFO] Verifying installation"
podman exec -it "$NAME" sh -lc "command -v multiflexi-cli && multiflexi-cli user --help | sed -n '1,20p'"

echo "[DONE] Container '$NAME' is ready with MultiFlexi CLI."

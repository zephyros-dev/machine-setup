#!/bin/bash

# KeePassXC install dir
APP_REF="org.keepassxc.KeePassXC/x86_64/stable"
for inst in "$HOME/.local/share/flatpak" "/var/lib/flatpak"; do
    if [ -d "$inst/app/$APP_REF" ]; then
        FLATPAK_INST="$inst"
        break
    fi
done
[ -z "$FLATPAK_INST" ] && exit 1

APP_PATH="$FLATPAK_INST/app/$APP_REF/active"

# runtime install dir
RUNTIME_REF=$(awk -F'=' '$1=="runtime" { print $2 }' < "$APP_PATH/metadata")
for inst in "$HOME/.local/share/flatpak" "/var/lib/flatpak"; do
    if [ -d "$inst/runtime/$RUNTIME_REF" ]; then
        FLATPAK_INST="$inst"
        break
    fi
done
[ -z "$FLATPAK_INST" ] && exit 1

RUNTIME_PATH="$FLATPAK_INST/runtime/$RUNTIME_REF/active"

exec flatpak-spawn \
    --env=LD_LIBRARY_PATH=/app/lib \
    --app-path="$APP_PATH/files" \
    --usr-path="$RUNTIME_PATH/files" \
    -- keepassxc-proxy "$@"

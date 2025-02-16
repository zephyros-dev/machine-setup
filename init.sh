#!/bin/bash
# flatpak --user install flathub com.visualstudio.code com.visualstudio.code.tool.podman
# flatpak override --user --filesystem=xdg-run/podman com.visualstudio.code
systemctl --user enable --now podman.socket
brew install sops uv
mkdir -p ~/.config/sops/age ~/.var/app/com.visualstudio.code/config/sops/age
touch ~/.config/sops/age/keys.txt
chmod 600 ~/.config/sops/age/keys.txt
ln -s /home/linuxbrew/.linuxbrew/bin/sops ~/.local/bin/sops
ln -s ~/.config/sops/age/keys.txt ~/.var/app/com.visualstudio.code/config/sops/age/keys.txt
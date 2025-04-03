import shutil
from pathlib import Path
import subprocess
import json
import os
import configparser

script_path = Path(os.path.realpath(__file__)).parent

# region: setup keepassxc
# https://github.com/keepassxreboot/keepassxc-browser/issues/1631#issuecomment-1153736766
print("Setting up keepassxc...")
subprocess.run(
    [
        "flatpak",
        "--user",
        "override",
        "org.mozilla.firefox",
        "--filesystem=/var/lib/flatpak/runtime/org.kde.Platform:ro",
        "--filesystem=xdg-data/flatpak/app/org.keepassxc.KeePassXC:ro",
        "--filesystem=xdg-run/app/org.keepassxc.KeePassXC:create",
    ]
)
firefox_path = Path.home() / ".var/app/org.mozilla.firefox"
keepass_proxy_path = firefox_path / "data/bin"
keepass_proxy_path.mkdir(parents=True, exist_ok=True)
shutil.copyfile(
    f"{script_path}/keepassxc-proxy-wrapper.sh",
    keepass_proxy_path / "keepassxc-proxy-wrapper.sh",
)
native_message_path = firefox_path / ".mozilla/native-messaging-hosts"
native_message_path.mkdir(parents=True, exist_ok=True)
shutil.copyfile(
    Path.home()
    / ".mozilla/native-messaging-hosts/org.keepassxc.keepassxc_browser.json",
    native_message_path / "org.keepassxc.keepassxc_browser.json",
)
change_path_content = json.loads(
    (native_message_path / "org.keepassxc.keepassxc_browser.json").read_text()
)
change_path_content["path"] = str(keepass_proxy_path / "keepassxc-proxy-wrapper.sh")
(native_message_path / "org.keepassxc.keepassxc_browser.json").write_text(
    json.dumps(change_path_content, sort_keys=True, indent=4)
)
# endregion

# region: install cli tools user
print("Installing cli tools...")
cli_tools_list = ["fd"]
subprocess.run(["brew", "install"] + cli_tools_list)
# endregion

# region: overlay tools
print("Installing overlay tools...")
overlay_list = ["fcitx5-unikey", "fcitx5-autostart", "goverlay"]
subprocess.run(["rpm-ostree", "install"] + overlay_list)
# endregion

# region: install pip tools
print("Installing pip tools...")
subprocess.run(["pip", "install", "-r", f"{script_path}/requirements.txt"])
# endregion

# region: install gnome extensions
print("Installing gnome extensions...")
gnome_extension_list = [
    "display-brightness-ddcutil@themightydeity.github.com",
    "kimpanel@kde.org",
]
subprocess.run(["gext", "install"] + gnome_extension_list)
# endregion

# region: install flatpak applications
print("Installing flatpak applications...")
flatpak_list = [
    "com.github.wwmm.easyeffects",
    "com.heroicgameslauncher.hgl",
    "com.visualstudio.code",
    "io.freetubeapp.FreeTube",
    "io.github.martchus.syncthingtray",
    "io.github.milkshiift.GoofCord",
    "io.github.pwr_solaar.solaar",
    "io.mpv.Mpv",
    "org.aegisub.Aegisub",
    "org.equeim.Tremotesf",
    "org.gimp.GIMP",
    "org.kde.krename",
    "org.keepassxc.KeePassXC",
    "org.mozilla.Thunderbird",
    "org.onlyoffice.desktopeditors",
]
subprocess.run(["flatpak", "install", "--user", "--noninteractive"] + flatpak_list)

startup_list = [
    "com.github.wwmm.easyeffects",
    "io.github.martchus.syncthingtray",
    "org.keepassxc.KeePassXC",
]
for application in startup_list:
    desktop_path = (
        Path.home()
        / ".local/share/flatpak/exports/share/applications"
        / f"{application}.desktop"
    ).resolve()
    autostart_path = Path.home() / ".config/autostart" / f"{application}.desktop"
    config = configparser.RawConfigParser()
    config.optionxform = (
        lambda option: option
    )  # Need this to keep Uppercase key https://docs.python.org/3/library/configparser.html#mapping-protocol-access
    config.read(desktop_path)
    if application == "com.github.wwmm.easyeffects":
        config["Desktop Entry"]["Exec"] = (
            f"{config['Desktop Entry']['Exec']} --hide-window"
        )
    if application == "io.github.martchus.syncthingtray":
        config["Desktop Entry"]["Exec"] = f"{config['Desktop Entry']['Exec']} --wait"
    with open(autostart_path, "w") as configfile:
        config.write(configfile, space_around_delimiters=False)

# endregion

# region: setup flatpak override
subprocess.run(
    [
        "flatpak",
        "--user",
        "override",
        "io.github.martchus.syncthingtray",
        f"--filesystem={Path.home()}/.var/app/io.freetubeapp.FreeTube/config/FreeTube",
    ]
)

subprocess.run(
    [
        "flatpak",
        "--user",
        "override",
        "com.visualstudio.code",
        f"--filesystem={Path.home()}/.var/app",
    ]
)

for app in [
    "com.heroicgameslauncher.hgl",
    "org.equeim.Tremotesf",
    "io.github.fastrizwaan.WineZGUI",
]:
    subprocess.run(
        [
            "flatpak",
            "--user",
            "override",
            app,
            "--filesystem=/mnt/server",
        ]
    )
subprocess.run(
    [
        "flatpak",
        "--user",
        "override",
        "io.github.fastrizwaan.WineZGUI",
        f"--filesystem={Path.home()}/Games",
    ]
)
subprocess.run(
    [
        "flatpak",
        "--user",
        "override",
        "com.github.Matoking.protontricks",
        f"--filesystem={Path.home()}/.local/share/Steam",
    ]
)
# endregion

# region: Setup mpv with mpv shim
# flatpak jellyfin mpv shim does not work with external mpv
mpv_config_path = Path(Path.home() / ".var/app/io.mpv.Mpv/config/mpv")
if not mpv_config_path.is_symlink():
    mpv_config_path.rmdir()
if mpv_config_path.resolve() != Path.home() / ".config/jellyfin-mpv-shim":
    mpv_config_path.unlink()
    mpv_config_path.symlink_to(Path.home() / ".config/jellyfin-mpv-shim")
shutil.copyfile(
    f"{script_path}/mpv",
    Path.home() / ".config/jellyfin-mpv-shim/mpv",
)
shutil.copyfile(
    f"{script_path}/jellyfin-mpv-shim.service",
    Path.home() / ".config/systemd/user/jellyfin-mpv-shim.service",
)
subprocess.run(["systemctl", "--user", "daemon-reload"])
subprocess.run(["systemctl", "--user", "enable", "jellyfin-mpv-shim", "--now"])
# endregion

# region: Setup sunshine
shutil.copyfile(
    f"{script_path}/sunshine-custom.service",
    Path.home() / ".config/systemd/user/sunshine-custom.service",
)
subprocess.run(["systemctl", "--user", "daemon-reload"])
subprocess.run(["systemctl", "--user", "enable", "sunshine-custom", "--now"])
# endregion

# region: Setup mangohud
shutil.copyfile(
    f"{script_path}/MangoHud.conf",
    Path.home() / ".config/MangoHud/MangoHud.conf",
)
# endregion

# region: Setup smb
print("Setup smb...")
# Decrypt smbcreds and move it to smbcreds
subprocess.run(
    [
        "sops",
        "decrypt",
        f"{script_path}/smbcreds.sops",
        "--output",
        f"{script_path}/.decrypted.smbcreds",
    ],
)
subprocess.run(
    [
        "sudo",
        "mv",
        f"{script_path}/.decrypted.smbcreds",
        "/etc/samba/smbcreds",
    ]
)
subprocess.run(
    [
        "sudo",
        "cp",
        f"{script_path}/var-mnt-server.mount.j2",
        "/etc/systemd/system/var-mnt-server.mount",
    ]
)
subprocess.run(
    [
        "sudo",
        "cp",
        f"{script_path}/var-mnt-server.automount.j2",
        "/etc/systemd/system/var-mnt-server.automount",
    ]
)
subprocess.run(["sudo", "systemctl", "enable", "var-mnt-server.automount", "--now"])
# endregion

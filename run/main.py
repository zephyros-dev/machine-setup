import configparser
import getpass
import json
import os
import shutil
import subprocess
from pathlib import Path

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
    ],
    check=False,
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
subprocess.run(["brew", "install"] + cli_tools_list, check=False)
# endregion

# region: overlay tools
print("Installing overlay tools...")
overlay_list = ["fcitx5-unikey", "fcitx5-autostart", "goverlay"]
subprocess.run(["rpm-ostree", "install"] + overlay_list, check=False)
# endregion

# region: install pip tools
print("Installing pip tools...")
subprocess.run(["pip", "install", "-r", f"{script_path}/requirements.txt"], check=False)
# endregion

# region: Gnome setup
print("Installing gnome extensions...")
gnome_extension_list = [
    "clipboard-indicator@tudmotu.com",
    "display-brightness-ddcutil@themightydeity.github.com",
    "kimpanel@kde.org",
]
subprocess.run(["gext", "install"] + gnome_extension_list, check=False)

print("Settings dconf...")
dconf_dict = {
    "/org/gnome/desktop/interface/enable-animations": "false",
    "/org/gnome/desktop/wm/keybindings/maximize": "['<Super>Up']",
    "/org/gnome/desktop/wm/keybindings/unmaximize": "['<Super>Down']",
}
for key, value in dconf_dict.items():
    subprocess.run(["dconf", "write", key, value], check=False)

print("Disable broken Gnome extensions...")
gnome_extension_disable_list = [
    "blur-my-shell@aunetx",
]
for extension in gnome_extension_disable_list:
    subprocess.run(["gnome-extensions", "disable", extension], check=False)
# endregion

# region: install flatpak applications
print("Installing flatpak applications...")
flatpak_list = [
    "com.github.wwmm.easyeffects",
    "com.heroicgameslauncher.hgl",
    "com.visualstudio.code.tool.podman",
    "com.visualstudio.code",
    "io.freetubeapp.FreeTube",
    "io.github.benjamimgois.goverlay",
    "io.github.martchus.syncthingtray",
    "io.github.milkshiift.GoofCord",
    "io.github.pwr_solaar.solaar",
    "io.mpv.Mpv",
    "org.aegisub.Aegisub",
    "org.equeim.Tremotesf",
    "org.fcitx.Fcitx5.Addon.Unikey",
    "org.fcitx.Fcitx5",
    "org.freedesktop.Platform.VulkanLayer.MangoHud",
    "org.gimp.GIMP",
    "org.kde.krename",
    "org.keepassxc.KeePassXC",
    "org.mozilla.Thunderbird",
    "org.onlyoffice.desktopeditors",
]
subprocess.run(
    ["flatpak", "install", "--user", "--noninteractive"] + flatpak_list, check=False
)

startup_list = [
    "com.github.wwmm.easyeffects",
    "io.github.martchus.syncthingtray",
    "org.fcitx.Fcitx5",
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
    ],
    check=False,
)

subprocess.run(
    [
        "flatpak",
        "--user",
        "override",
        "com.visualstudio.code",
        f"--filesystem={Path.home()}/.var/app",
    ],
    check=False,
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
        ],
        check=False,
    )
subprocess.run(
    [
        "flatpak",
        "--user",
        "override",
        "io.github.fastrizwaan.WineZGUI",
        f"--filesystem={Path.home()}/Games",
    ],
    check=False,
)
subprocess.run(
    [
        "flatpak",
        "--user",
        "override",
        "com.github.Matoking.protontricks",
        f"--filesystem={Path.home()}/.local/share/Steam",
    ],
    check=False,
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
subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
subprocess.run(
    ["systemctl", "--user", "enable", "jellyfin-mpv-shim", "--now"], check=False
)
# endregion

# region: Setup sunshine
# Sunshine itself is installed by `ujust setup-sunshine enable-brew`
# (homebrew.sunshine.service). It only runs inside a logged-in session, so we
# autologin and immediately lock the screen: a password is still required
# locally, while Moonlight can connect and launch apps right after boot.
print("Setup sunshine...")
user_systemd_path = Path.home() / ".config/systemd/user"

# Remove units that start a second Sunshine and race for its ports
for unit in ["sunshine-custom.service", "app-dev.lizardbyte.app.Sunshine.service"]:
    if (user_systemd_path / unit).exists():
        subprocess.run(["systemctl", "--user", "disable", "--now", unit], check=False)
        (user_systemd_path / unit).unlink()

shutil.copyfile(
    f"{script_path}/lock-on-login.service",
    user_systemd_path / "lock-on-login.service",
)
subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
subprocess.run(["systemctl", "--user", "enable", "lock-on-login"], check=False)

if (
    subprocess.run(
        ["systemctl", "--user", "cat", "homebrew.sunshine"],
        capture_output=True,
        check=False,
    ).returncode
    != 0
):
    print("homebrew.sunshine not found, run: ujust setup-sunshine enable-brew")

# Monitor layout: DP-2 is a portrait monitor on the left, DP-1 the primary.
# During a stream DP-2 is turned off so games launched from Heroic open on the
# streamed DP-1 instead of following the pointer to DP-2. If the layout in
# GNOME Settings changes, update the "undo" layout to match.
sunshine_stream_layout = "/usr/bin/gdctl set -L -M DP-1 --primary --scale 2"
sunshine_restore_layout = (
    "/usr/bin/gdctl set"
    " -L -M DP-2 --scale 2 --transform 90 --x 0 --y 0"
    " -L -M DP-1 --primary --scale 2 --x 1080 --y 492"
)
sunshine_settings = {
    # Capture via KMS instead of the GNOME screencast portal: the portal asks
    # for permission on every login (the "remember" choice is not honored for
    # host apps) and Sunshine hangs, without opening its ports, until it is
    # answered, which is impossible behind the lock screen. Requires
    # cap_sys_admin, which the brew install sets.
    "capture": "kms",
    "output_name": "DP-1",
    "global_prep_cmd": json.dumps(
        [
            {
                "do": sunshine_stream_layout,
                "undo": sunshine_restore_layout,
                "elevated": False,
            }
        ],
        separators=(",", ":"),
    ),
}
sunshine_conf_path = Path.home() / ".config/sunshine/sunshine.conf"
sunshine_conf_path.parent.mkdir(parents=True, exist_ok=True)
sunshine_conf_path.touch()
sunshine_conf = [
    line
    for line in sunshine_conf_path.read_text().splitlines()
    if line.split("=", 1)[0].strip() not in sunshine_settings
]
sunshine_conf += [f"{key} = {value}" for key, value in sunshine_settings.items()]
sunshine_conf_path.write_text("\n".join(sunshine_conf) + "\n")

# Enable GDM autologin (edit only the [daemon] keys, keep the rest of the file)
gdm_conf_path = Path("/etc/gdm/custom.conf")
gdm_autologin = {"AutomaticLoginEnable": "True", "AutomaticLogin": getpass.getuser()}
gdm_lines = gdm_conf_path.read_text().splitlines()
daemon_index = gdm_lines.index("[daemon]")
section_end = next(
    (
        i
        for i in range(daemon_index + 1, len(gdm_lines))
        if gdm_lines[i].startswith("[")
    ),
    len(gdm_lines),
)
for key, value in gdm_autologin.items():
    for i in range(daemon_index + 1, section_end):
        if gdm_lines[i].split("=", 1)[0].strip() == key:
            gdm_lines[i] = f"{key}={value}"
            break
    else:
        gdm_lines.insert(daemon_index + 1, f"{key}={value}")
        section_end += 1
subprocess.run(
    ["sudo", "tee", str(gdm_conf_path)],
    input="\n".join(gdm_lines) + "\n",
    text=True,
    stdout=subprocess.DEVNULL,
    check=False,
)
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
    check=False,
)
subprocess.run(
    [
        "sudo",
        "mv",
        f"{script_path}/.decrypted.smbcreds",
        "/etc/samba/smbcreds",
    ],
    check=False,
)
subprocess.run(
    [
        "sudo",
        "cp",
        f"{script_path}/var-mnt-server.mount.j2",
        "/etc/systemd/system/var-mnt-server.mount",
    ],
    check=False,
)
subprocess.run(
    [
        "sudo",
        "cp",
        f"{script_path}/var-mnt-server.automount.j2",
        "/etc/systemd/system/var-mnt-server.automount",
    ],
    check=False,
)
# endregion

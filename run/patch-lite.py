#!/usr/bin/env python3
# Download the latest FidelityFX SDK release (cached by version in ~/Downloads),
# then write its DX12 DLLs into the current directory, with the upscaler
# rebuilt to force the Lite path.
import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

REPO = "GPUOpen-LibrariesAndSDKs/FidelityFX-SDK"
CACHE_DIR = Path.home() / "Downloads"
SIGNEDBIN = "Kits/FidelityFX/signedbin"
COPY_DLLS = [
    "amd_fidelityfx_framegeneration_dx12.dll",
    "amd_fidelityfx_loader_dx12.dll",
]
PATCH_DLL = "amd_fidelityfx_upscaler_dx12.dll"

# (offset, expected original bytes, replacement bytes)
PATCHES = [
    (0x70D0, "48 83 ec 48", "b0 01 c3 90"),  # Lite  canProvide -> true
    (0x8D60, "40 53 48 83", "b0 00 c3 90"),  # Int8  canProvide -> false
    (0x97C0, "48 83 ec 48", "b0 00 c3 90"),  # Navi2 canProvide -> false
    (0xA1A0, "40 53 48 83", "b0 00 c3 90"),  # Base  canProvide -> false
]


def latest_version() -> str:
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    request = urllib.request.Request(url, headers={"User-Agent": "patch-lite"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["tag_name"].removeprefix("v")


def cached_zip(version: str) -> Path:
    path = CACHE_DIR / f"FidelityFX-SDK-{version}.zip"
    if path.exists():
        print(f"using cached {path}")
        return path
    url = f"https://github.com/{REPO}/archive/refs/tags/v{version}.zip"
    print(f"downloading {url}")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(".zip.part")
    with urllib.request.urlopen(url, timeout=60) as response, open(partial, "wb") as f:
        shutil.copyfileobj(response, f)
    partial.rename(path)
    return path


def patch_lite(data: bytes) -> bytes:
    patched = bytearray(data)
    for offset, original, replacement in PATCHES:
        original = bytes.fromhex(original)
        found = bytes(patched[offset : offset + len(original)])
        if found != original:
            sys.exit(
                f"{PATCH_DLL}: expected {original.hex(' ')} at {offset:#x}, "
                f"found {found.hex(' ')}; offsets only match the 2.4.0 build"
            )
        patched[offset : offset + len(original)] = bytes.fromhex(replacement)
    return bytes(patched)


def main() -> None:
    version = latest_version()
    print(f"latest FidelityFX SDK: {version}")
    with zipfile.ZipFile(cached_zip(version)) as archive:
        prefix = f"FidelityFX-SDK-{version}/{SIGNEDBIN}"
        dlls = {
            name: archive.read(f"{prefix}/{name}") for name in COPY_DLLS + [PATCH_DLL]
        }
    dlls[PATCH_DLL] = patch_lite(dlls[PATCH_DLL])
    for name, data in dlls.items():
        (Path.cwd() / name).write_bytes(data)
        print(f"wrote {Path.cwd() / name}")


if __name__ == "__main__":
    main()

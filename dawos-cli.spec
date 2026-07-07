# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for dawos-cli standalone binary.
#
# Build:
#   pip install pyinstaller
#   pyinstaller dawos-cli.spec
#
# Output: dist/dawos (single executable)

a = Analysis(
    ["dawos_cli/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        "dawos_cli",
        "dawos_cli.app",
        "dawos_cli.client",
        "dawos_cli.config",
        "dawos_cli.dashboard",
        "dawos_cli.doctor",
        "dawos_cli.output",
        "dawos_cli.shell",
        "dawos_cli.state",
        "dawos_cli.telemetry",
        "dawos_cli.updater",
        "dawos_cli.commands",
        "dawos_cli.commands.config_cmd",
        "dawos_cli.commands.conntrack",
        "dawos_cli.commands.dhcp",
        "dawos_cli.commands.diagnostics",
        "dawos_cli.commands.dns",
        "dawos_cli.commands.events",
        "dawos_cli.commands.firewall",
        "dawos_cli.commands.flow",
        "dawos_cli.commands.limits",
        "dawos_cli.commands.lldp",
        "dawos_cli.commands.logs",
        "dawos_cli.commands.monitoring",
        "dawos_cli.commands.nat",
        "dawos_cli.commands.network",
        "dawos_cli.commands.ntp",
        "dawos_cli.commands.pool",
        "dawos_cli.commands.pppoe",
        "dawos_cli.commands.profile",
        "dawos_cli.commands.routing",
        "dawos_cli.commands.scheduler",
        "dawos_cli.commands.service",
        "dawos_cli.commands.sessions",
        "dawos_cli.commands.system",
        "dawos_cli.commands.traffic",
        "dawos_cli.commands.vrrp",
        "dawos_cli.commands.zone",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="dawos",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

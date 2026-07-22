# HyprKeys

GTK4 explorer for Hyprland key bindings. It reads `hyprland.conf` and its
sourced configuration files, then offers search, categories, duplicate shortcut
detection, and direct configuration reload.

## Arch Linux

```bash
sudo pacman -S python python-gobject gtk4
```

## Run from source

```bash
cd hyprkeys
PYTHONPATH=. python -m hyprkeys.app
```

## Hyprland shortcut

```ini
bind = SUPER, K, exec, hyprkeys
```

## Add a shortcut safely

Use **Add shortcut** in the application to append a binding to the main
`hyprland.conf`. HyprKeys validates required fields, refuses line breaks, and
creates a timestamped backup next to the configuration before writing. Review
and apply the new binding with **Reload Hyprland**.

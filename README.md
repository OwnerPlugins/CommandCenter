<h1 align="center">⚙️ Command Center</h1>

![Visitors](https://komarev.com/ghpvc/?username=Belfagor2005&label=Repository%20Views&color=blueviolet)
[![Version](https://img.shields.io/badge/Version-1.1-blue.svg)](https://github.com/OwnerPlugins/CommandCenter)
[![Enigma2](https://img.shields.io/badge/Enigma2-Plugin-ff6600.svg)](https://www.enigma2.net)
[![Python](https://img.shields.io/badge/Python3-only-orange.svg)](https://www.python.org/)
[![Release](https://img.shields.io/github/v/release/OwnerPlugins/CommandCenter)](https://github.com/OwnerPlugins/CommandCenter/releases)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Donate](https://img.shields.io/badge/_-Donate-red.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge)](https://ko-fi.com/lululla)

---

## 📌 Overview

**Command Center** is an Enigma2 plugin that allows you to run shell/telnet commands directly on your receiver, organized by categories.  
It provides a user-friendly interface to select, execute, and monitor command output in real time – perfect for system administration, debugging, or learning Linux commands on your set‑top box.

The plugin includes **hundreds of pre‑defined commands** covering:

- System information (CPU, memory, disks)
- Process management
- Network diagnostics
- Package management (opkg, apt, dpkg)
- Filesystem operations
- Compression/archive tools
- Media / streaming utilities
- Enigma2 specific commands (restart GUI, reload channels, etc.)
- Screenshots
- And many more utilities

---

## Screenshots

<table align="center">
  <tr>
    <td align="center">
      <img src="screen/screen1.png?sanitize=true&raw=true" title="preview1" width="400"/><br/>
      <b>Preview 1</b>
    </td>
    <td align="center">
      <img src="screen/screen2.png?sanitize=true&raw=true" title="preview2" width="400"/><br/>
      <b>Preview 2</b>
    </td>
  </tr>

  <tr>
    <td align="center">
      <img src="screen/screen3.png?sanitize=true&raw=true" title="preview3" width="400"/><br/>
      <b>Preview 3</b>
    </td>
  </tr>
</table>


## ✨ Features (v1.1)

- 📂 **Categorized commands** – quickly find what you need.
- ▶️ **Execute any command** with the press of a button.
- 🖥️ **Live output monitor** – see command output as it runs.
- 📜 **Full scrollable output** – use **LEFT/RIGHT** for line‑by‑line scrolling, **CH+/CH–** for page scrolling.
- 💾 **Save output** to `/tmp/` for later analysis.
- 🔄 **Auto‑scroll** (optional) – automatically follows new output.
- 🎨 **Color‑coded buttons** – intuitive navigation.
- 📋 **Command descriptions** – understand what each command does.
- ⚙️ **Fully external command list** – commands are stored in `/etc/enigma2/commandcenter_commands.json`. Edit it with any text editor to add, remove or modify commands – no plugin code changes needed.
- 🛡️ **Automatic backups** – every time you save custom commands or settings, a timestamped backup (`.bak`) is created. Your data is safe.
- 🔘 **Manager screen** – easily add custom commands, edit existing ones, or disable predefined commands (toggle with INFO button).
- ℹ️ **INFO button works everywhere** – shows version, command details, or toggles disable state.
- 📱 **Optimized for all screen sizes** – includes dedicated skins for HD (1280×720), Full HD (1920×1080) and WQHD (2560×1440). Automatically selected based on your screen resolution.
- 🌍 **Fully translatable** – uses Enigma2’s locale system.

---

## 📦 Installation

1. **Copy the plugin folder** to your Enigma2 receiver:

```bash
/usr/lib/enigma2/python/Plugins/Extensions/CommandCenter
```

2. **Set permissions** (if needed):

```bash
chmod 755 /usr/lib/enigma2/python/Plugins/Extensions/CommandCenter/plugin.py
```

3. **Restart Enigma2** (GUI restart or full reboot).

> **Note:** On first run, the plugin will create the following configuration files:
> - `/etc/enigma2/commandcenter_commands.json` – your editable command list (copied from `default_commands.json` inside the plugin folder).
> - `/etc/enigma2/commandcenter_custom.json` – your personal custom commands.
> - `/etc/enigma2/commandcenter_config.json` – disabled states and command modifications.

---

## 🚀 Usage

### Main Category Screen

- **UP / DOWN** – navigate through categories.
- **OK** – open the selected category.
- **BLUE** – open the **Manager** screen (see below).
- **INFO** – show plugin version and info.

### Command Screen

- **UP / DOWN** – select a command from the list.
- **GREEN / OK** – execute the selected command.
- **LEFT / RIGHT** – scroll the output area **one line** up/down.
- **CH+ / CH– (PageUp/PageDown)** – scroll the output area **one page** up/down.
- **YELLOW** – clear the output area.
- **BLUE** – save the current output to `/tmp/command_output_YYYYMMDD_HHMMSS.txt`.
- **INFO** – show the full command and its description.
- **RED** – go back to category list.

### Manager Screen

- **UP / DOWN** – browse all commands (predefined + custom).
- **OK** – edit the selected command.
- **GREEN** – add a new custom command (enter command and description).
- **YELLOW** – edit the selected command.
- **BLUE** – delete a custom command or disable a predefined command (opens confirmation).
- **INFO** – toggle the `[DISABLED]` state for **predefined commands only** (disabled commands won’t appear in the main list).
- **RED** – exit the manager.

---

## 🛠️ Adding, Editing or Removing Commands

### Predefined commands (external file)

All predefined commands are stored in `/etc/enigma2/commandcenter_commands.json`.  
You can edit this file with any text editor (e.g., via FTP) – the plugin reads it every time it opens.  
The format is:

```json
{
  "Category Name": [
    ["command", "description"],
    ["another command", "description"]
  ]
}
```

If the file is missing or corrupted, the plugin recreates it from the default (shipped inside the plugin folder).

### Custom commands

Use the **Manager** screen (BLUE button) → **Add Custom** (GREEN).  
Custom commands are saved in `/etc/enigma2/commandcenter_custom.json` and appear under a special `"Custom"` category.

### Disabling predefined commands

In the **Manager** screen, move to a predefined command and press **INFO** to toggle the `[DISABLED]` flag. Disabled commands are hidden from the main command list.

### Automatic backups

Every time you save changes (custom commands, disabled state, modifications), the plugin creates a timestamped backup of the affected configuration file.  
Example: `/etc/enigma2/commandcenter_config.json.20260526_123456.bak`  
To restore, simply copy the backup file back to the original name.

---

## 🖥️ Skins (HD / FHD / WQHD)

The plugin automatically detects your screen resolution and loads the appropriate skin from:

- `skins/hd/`     – for 1280×720 (or narrower)
- `skins/fhd/`    – for 1920×1080
- `skins/wqhd/`   – for 2560×1440

You can customize the skin files (`CategoryScreen.xml`, `CommandScreen.xml`, `ManagerScreen.xml`) to match your personal taste.

---

## 📜 License

This project is licensed under the **GPLv3 License**.

You are free to use, modify, and distribute this software under the terms of the license.  
Please keep the original copyright and credits.

---

## 🙏 Credits

- **Plugin development:** [Lululla](https://github.com/OwnerPlugins).
- **Thanks to** the Enigma2 community and all testers.

---

## 📡 Enigma2 Project

Compatible with all Enigma2‑based receivers (OpenPLi, OpenATV, OpenVision, Pure2, etc.).

---

## 📸 Screenshots

*Screenshots can be added here (not included in this markdown).*

---

## 💬 Support

For issues, feature requests, or contributions, please open an issue on [GitHub](https://github.com/OwnerPlugins/CommandCenter/issues).

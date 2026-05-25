<h1 align="center">⚙️ Command Center</h1>

![Visitors](https://komarev.com/ghpvc/?username=Belfagor2005&label=Repository%20Views&color=blueviolet)
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

## ✨ Features

- 📂 **Categorized commands** – quickly find what you need.
- ▶️ **Execute any command** with the press of a button.
- 🖥️ **Live output monitor** – see command output as it runs.
- 📜 **Scrollable output** – review long command results.
- 💾 **Save output** to `/tmp/` for later analysis.
- 🔄 **Auto‑scroll** (optional) – automatically follows new output.
- 🎨 **Color‑coded buttons** – intuitive navigation.
- 📋 **Command descriptions** – understand what each command does.
- ⚙️ **Easily extensible** – add your own commands by editing the `COMMANDS` dictionary in `plugin.py`.

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

---

## 🚀 Usage

1. Open the plugin from the **Extensions** or **Plugin** menu.
2. Choose a category (e.g., "📁 System Info", "🌐 Network").
3. Select a command from the list – the description appears in the status bar.
4. Press **Run** (green button) to execute the command.
5. Watch the live output in the right panel.
6. Use **Clear** (yellow) to erase output, **Save** (blue) to store it to `/tmp/`, or **Info** (info button) to see the command description.
7. Press **Back** (red) to return to the category list or exit.

---

## 🛠️ Adding Custom Commands

You can easily add your own commands by editing the `COMMANDS` dictionary inside `plugin.py`.  
Each category is a dictionary key; the value is a list of tuples `(command, description)`.

Example:

```python
"🌐 My Custom Category": [
    ("echo Hello World", "Prints Hello World"),
    ("ls -la /tmp", "List content of /tmp"),
],
```

After adding, restart the plugin to see your new commands.

---

## 📜 License

This project is licensed under the **GPLv3 License**.

You are free to use, modify, and distribute this software under the terms of the license.  
Please keep the original copyright and credits.

---

## 🙏 Credits

- **Plugin development:** [Lululla](https://github.com/OwnerPlugins).
- **Thanks to** the Enigma2 community.

---

## 📡 Enigma2 Project

Compatible with all Enigma2‑based receivers (OpenPLi, OpenATV, OpenVision, Pure2, etc.).

---

## 📸 Screenshots

*Screenshots can be added here (not included in this markdown).*

---

## 💬 Support

For issues, feature requests, or contributions, please open an issue on [GitHub](https://github.com/OwnerPlugins/CommandCenter/issues).

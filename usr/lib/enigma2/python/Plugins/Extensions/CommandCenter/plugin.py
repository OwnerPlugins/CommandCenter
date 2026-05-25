# -*- coding: utf-8 -*-

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Button import Button
from Components.MenuList import MenuList
from Components.config import config, ConfigSubsection, ConfigYesNo
from enigma import eConsoleAppContainer
from datetime import datetime

from . import _

#########################################################
#                                                       #
#  Command Center - Telnet/Shell Plugin                 #
#  Based on commands extraction from telnet             #
#  License: GPLv3                                       #
#  https://www.gnu.org/licenses/gpl-3.0.html            #
#                                                       #
#  Credits:                                             #
#  - Original concept: Lululla                          #
#  - Development: Lululla                               #
#  - Contributions: OpenPLi, Enigma2 community          #
#                                                       #
#  This program is free software: you can redistribute  #
#  it and/or modify it under the terms of the GNU       #
#  General Public License as published by the Free      #
#  Software Foundation, either version 3 of the         #
#  License, or (at your option) any later version.      #
#                                                       #
#  This program is distributed in the hope that it      #
#  will be useful, but WITHOUT ANY WARRANTY; without    #
#  even the implied warranty of MERCHANTABILITY or      #
#  FITNESS FOR A PARTICULAR PURPOSE. See the GNU        #
#  General Public License for more details.             #
#                                                       #
#########################################################


config.plugins.CommandCenter = ConfigSubsection()
config.plugins.CommandCenter.autoScroll = ConfigYesNo(default=True)


COMMANDS = {
    "📁 System Info": [
        ("uname -a", "Kernel information"),
        ("uptime", "System uptime"),
        ("free -m", "Free memory (MB)"),
        ("cat /proc/meminfo", "Memory details"),
        ("df -h", "Disk space usage"),
        ("df -aTh", "Disk space with FS type"),
        ("blkid", "Block device UUIDs"),
        ("cat /proc/cpuinfo", "CPU info"),
        ("cat /proc/version", "Kernel version"),
        ("hostname", "Hostname"),
        ("who -a", "Logged users"),
        ("lsof", "Open files (may take time)"),
    ],
    "⚙️ Process Management": [
        ("ps aux", "Process list"),
        ("ps | grep enigma2", "Enigma2 processes"),
        ("killall -9 enigma2", "Kill Enigma2 (restart GUI)"),
        ("killall -9 python", "Kill all Python processes"),
        ("killall -INT ffmpeg", "Stop ffmpeg"),
        ("top -n 1 -b", "Real-time processes (one shot)"),
        ("lsof | wc -l", "Count open files"),
    ],
    "🌐 Network": [
        ("ifconfig", "Network configuration"),
        ("ip link", "Network interfaces"),
        ("ip route | grep default", "Default gateway"),
        ("netstat -tulpn", "Listening ports"),
        ("ping -c 1 8.8.8.8", "Ping Google DNS"),
        ("wget -q -T 1 -t 1 --spider http://www.google.com", "HTTP connectivity test"),
        ("arp -n", "ARP table"),
        ("hostname -I", "Local IP addresses"),
    ],
    "📦 Package Management": [
        ("opkg update", "Update package list (opkg)"),
        ("opkg list-installed", "Installed packages (opkg)"),
        ("opkg list | head -20", "First 20 available packages"),
        ("opkg install <name>", "Install package (replace <name>)"),
        ("opkg remove <name>", "Remove package"),
        ("apt-get update", "Update (apt)"),
        ("apt list --installed | head -20", "Installed apt packages"),
        ("dpkg -l | head -20", "dpkg list"),
    ],
    "📦 Package Search (opkg)": [
        ("opkg update", "Aggiorna lista pacchetti"),
        ("opkg list | grep -i ssl", "Cerca pacchetti SSL"),
        ("opkg list | grep -i dvbcsa", "Cerca pacchetti dvbcsa"),
        ("opkg list | grep -i pcsc", "Cerca pacchetti pcsc"),
        ("opkg list-installed | grep -i ssl", "Pacchetti SSL installati"),
        ("opkg list-installed | grep -i pcsc", "Pacchetti pcsc installati"),
        ("openssl version", "Versione OpenSSL"),
        ("ls -l /usr/lib/libss*.*", "Trova libreria SSL"),
        ("opkg install libcrypto-compat", "Installa libcrypto-compat"),
    ],
    "📂 Filesystem": [
        ("ls -la /etc/enigma2/", "Content of /etc/enigma2"),
        ("pwd", "Current directory"),
        ("cd /tmp && ls -la", "Content of /tmp"),
        ("find /etc/enigma2 -name '*.tv'", "Find TV bouquets"),
        ("du -shc /home/root 2>/dev/null", "Space used by /home/root"),
        ("mount", "Mount points"),
        ("cat /etc/fstab", "Filesystem table"),
        ("lsattr -d /etc", "Attributes of /etc"),
    ],
    "🔧 OSCam Tools": [
        ("find /usr/bin -name 'oscam*' -type f", "Cerca file oscam in /usr/bin"),
        ("ls -la /usr/bin/oscam*", "Dettaglio file oscam"),
        ("find /usr/bin -name 'oscam*' -type f 2>/dev/null", "Cerca ricorsiva oscam"),
        ("find /usr/bin -name 'oscam*' -o -name '*oscam*' -type f 2>/dev/null", "Cerca con wildcard estesa"),
        ("find /usr/bin -name 'oscam*' -type f 2>/dev/null | wc -l", "Conta file oscam trovati"),
        ("ps aux | grep oscam | grep -v grep", "Verifica se oscam è in esecuzione"),
        ("find / -name '*oscam*' -type f 2>/dev/null | head -20", "Cerca oscam in tutto il sistema (lento)"),
        ("find /usr/bin -name '*oscam*' -type f -exec file {} \\;", "Cerca script oscam"),
        ("find /usr/bin -name 'oscam*' -type f -executable", "Cerca eseguibili oscam"),
    ],
    "🗜️ Compression/Archive": [
        ("tar -czf /tmp/backup.tar.gz /etc/enigma2", "Backup settings (tar.gz)"),
        ("tar -xzf /tmp/backup.tar.gz -C /", "Restore backup"),
        ("unzip -l /tmp/file.zip", "List zip contents"),
        ("unrar l /tmp/file.rar", "List rar contents"),
        ("7za l /tmp/file.7z", "List 7z contents"),
        ("gzip -d /tmp/file.gz", "Decompress gz"),
        ("xz -d /tmp/file.xz", "Decompress xz"),
    ],
    "🎬 Media/Streaming": [
        ("ffmpeg -version | head -1", "FFmpeg version"),
        ("ffmpeg -i /media/hdd/movie/recording.ts -frames:v 1 screenshot.jpg", "Extract screenshot from video"),
        ("showiframe /usr/share/enigma2/backdrop.mvi", "Show MVI bootlogo"),
        ("killall -INT ffmpeg", "Stop running ffmpeg"),
    ],
    "🕹️ Enigma2 Specific": [
        ("wget -qO- http://127.0.0.1/web/servicelistreload", "Reload channel list (webif)"),
        ("init 3", "Restart GUI (alternative)"),
        ("systemctl restart enigma2", "Restart GUI (systemd)"),
        ("grep -i 'error' /home/root/.enigma2/enigma2.log | tail -20", "Last Enigma2 errors"),
    ],
    "📸 Screenshot": [
        ("grab -q -s jpg > /tmp/screenshot.jpg", "Screenshot JPG"),
        ("grab -p -s png > /tmp/screenshot.png", "Screenshot PNG"),
        ("dreamboxctl screenshot -f /tmp/screen.png", "Screenshot using dreamboxctl"),
    ],
    "🛠️ Utilities": [
        ("date", "Date and time"),
        ("date -s '2025-01-01 12:00:00'", "Set date/time (example)"),
        ("hwclock --systohc", "Sync hardware clock"),
        ("md5sum /etc/enigma2/settings", "MD5 of settings file"),
        ("sha256sum /etc/enigma2/settings", "SHA256 of settings file"),
        ("which python", "Python path"),
        ("echo -e 'Hello\\nWorld'", "Test echo with escape"),
        ("sync", "Sync disk buffers"),
    ],
    "🔗 Symlink & Architecture": [
        ("ln -sf /usr/lib/enigma2/python/Plugins/Extensions/ /", "Crea symlink Extensions"),
        ("ln -sf /usr/share/enigma2/ /", "Crea symlink share"),
        ("TARGET=$(find /media -maxdepth 1 -type d ! -name 'media' -exec mountpoint -q {} \\; -print | head -n 1) && [ -n \"$TARGET\" ] && ln -sf \"$TARGET\" /hdd && ln -sf \"$TARGET/picon\" /usr/share/enigma2/picon && ln -sf \"$TARGET/picon\" /picon && echo \"Creato per: $TARGET\"", "Crea symlink automatica per HDD/picon"),
        ("dpkg --print-architecture | grep -iE 'arm|aarch64|mips|cortex|sh4|sh_4'", "Architettura box (dpkg)"),
        ("opkg print-architecture | grep -iE 'arm|aarch64|mips|cortex|h4|sh_4'", "Architettura box (opkg)"),
    ],
}


class CategoryScreen(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.skin = self.build_skin()
        self["categories"] = MenuList([])
        self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"], {
            "ok": self.select_category,
            "cancel": self.close,
            "up": self.categories_up,
            "down": self.categories_down,
        }, -1)
        # self.onShown = None
        self.populate_categories()

    def build_skin(self):
        return """
        <screen name="CategoryScreen" position="center,center" size="600,500" title="Command Center - Categories" backgroundColor="#10000000">
            <widget name="categories" position="10,10" size="580,480" font="Regular;24" itemHeight="35" scrollbarMode="showOnDemand" />
        </screen>
        """

    def populate_categories(self):
        cat_list = [(cat, cat) for cat in COMMANDS.keys()]
        self["categories"].setList(cat_list)

    def categories_up(self):
        self["categories"].up()

    def categories_down(self):
        self["categories"].down()

    def select_category(self):
        selected = self["categories"].getCurrent()
        if selected:
            category_name = selected[1]
            self.session.open(CommandScreen, category_name)


class CommandScreen(Screen):
    skin = """
        <screen name="CommandScreen" position="center,center" size="1100,720" title="Command Center by Lululla" backgroundColor="#10000000">
            <widget name="command_list" position="10,35" size="400,600" font="Regular;24" itemHeight="30" scrollbarMode="showOnDemand" />
            <widget name="output_area" position="420,35" size="670,600" font="Courier;22" />
            <widget name="key_red" position="10,640" size="120,40" backgroundColor="#9f1313" font="Regular;20" valign="center" halign="center" />
            <widget name="key_green" position="140,640" size="120,40" backgroundColor="#005500" font="Regular;20" valign="center" halign="center" />
            <widget name="key_yellow" position="270,640" size="120,40" backgroundColor="#a08000" font="Regular;20" valign="center" halign="center" />
            <widget name="key_blue" position="400,640" size="120,40" backgroundColor="#18188b" font="Regular;20" valign="center" halign="center" />
            <widget name="key_info" position="530,640" size="120,40" backgroundColor="#33000000" font="Regular;20" valign="center" halign="center" />
            <widget name="statusbar" position="10,685" size="1080,30" font="Regular;22" backgroundColor="#33000000" />
        </screen>
    """

    def __init__(self, session, category_name):
        Screen.__init__(self, session)
        self.session = session
        self.category_name = category_name
        self.commands = COMMANDS[category_name]
        self.container = None
        self.output_text = ""
        self.menu_items = [(desc, cmd) for (cmd, desc) in self.commands]
        self.setTitle("Command Center by Lululla - %s" % self.category_name)
        self["command_list"] = MenuList([])
        self["command_list"].setList(self.menu_items)
        self["output_area"] = ScrollLabel("")
        self["output_area"].setText(_("Select a command and press Run.\n\n"))
        self["key_red"] = Button(_("Back"))
        self["key_green"] = Button(_("Run"))
        self["key_yellow"] = Button(_("Clear"))
        self["key_blue"] = Button(_("Save"))
        self["key_info"] = Button(_("Info"))
        self["statusbar"] = Label(_("Ready"))
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], {
            "ok": self.execute_command,
            "cancel": self.close,
            "red": self.close,
            "green": self.execute_command,
            "yellow": self.clear_output,
            "blue": self.save_output,
            "info": self.show_command_info,
            "up": self.command_up,
            "down": self.command_down,
        }, -1)

        self["command_list"].onSelectionChanged.append(
            self.on_selection_changed)

    def command_up(self):
        self["command_list"].up()

    def command_down(self):
        self["command_list"].down()

    def on_selection_changed(self):
        selected = self["command_list"].getCurrent()
        if selected:
            desc, cmd = selected
            self["statusbar"].setText("Command: " + cmd[:80])

    def execute_command(self):
        selected = self["command_list"].getCurrent()
        if not selected:
            self["statusbar"].setText(_("No command selected"))
            return
        desc, cmd = selected
        self.output_text = ""
        self["output_area"].setText("Executing: %s\n\n" % cmd)
        self["statusbar"].setText("Executing...")
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.cmd_finished)
        self.container.dataAvail.append(self.cmd_data_avail)
        if self.container.execute(cmd):
            self["output_area"].appendText(_("Failed to start command.\n"))
            self["statusbar"].setText(_("Execution error"))
            self.container = None

    def cmd_data_avail(self, data):
        try:
            text = data.decode('utf-8', errors='replace')
        except BaseException:
            text = str(data)
        self.output_text += text
        self["output_area"].appendText(text)
        if config.plugins.CommandCenter.autoScroll.value:
            self["output_area"].setPos(999999)

    def cmd_finished(self, retval):
        self["output_area"].appendText(_(
            "\n--- Execution finished (exit code %d) ---\n" %
            retval))
        self["statusbar"].setText(_("Command finished (code %d)" % retval))
        self.container = None

    def clear_output(self):
        self.output_text = ""
        self["output_area"].setText(_("Output cleared.\n"))

    def save_output(self):
        if not self.output_text:
            self["statusbar"].setText(_("No output to save"))
            return
        filename = "/tmp/command_output_%s.txt" % datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            with open(filename, "w") as f:
                f.write(self.output_text)
            self["statusbar"].setText(_("Saved to %s") % filename)
            self.session.open(
                MessageBox,
                _("Output saved to:\n%s") % filename,
                MessageBox.TYPE_INFO)
        except Exception as e:
            self["statusbar"].setText(_("Save error: %s") % str(e))
            self.session.open(
                MessageBox,
                _("Save error:\n%s") % str(e),
                MessageBox.TYPE_ERROR)

    def show_command_info(self):
        selected = self["command_list"].getCurrent()
        if selected:
            desc, cmd = selected
            info = _("Command:\n%s\n\nDescription:\n%s") % (cmd, desc)
        else:
            info = "No command selected."
        self.session.open(MessageBox, info, MessageBox.TYPE_INFO)


def main(session, **kwargs):
    session.open(CategoryScreen)


def Plugins(**kwargs):
    from Plugins.Plugin import PluginDescriptor
    return [
        PluginDescriptor(
            name=_("Command Center"),
            description=_("Run telnet/shell commands on Enigma2"),
            where=[
                PluginDescriptor.WHERE_PLUGINMENU,
                PluginDescriptor.WHERE_EXTENSIONSMENU],
            icon="icon.png",
            fnc=main)]

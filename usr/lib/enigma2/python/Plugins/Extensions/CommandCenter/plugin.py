# -*- coding: utf-8 -*-

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

import json
import os
import codecs
import shutil
from datetime import datetime
from os.path import join, basename, exists, getmtime
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.MenuList import MenuList
from Components.config import config, ConfigSubsection, ConfigYesNo
from enigma import eConsoleAppContainer, getDesktop
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

from . import _, __version__

PLUGIN_ID = 'CommandCenter'
PLUGIN_ROOT = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format(PLUGIN_ID))
config.plugins.CommandCenter = ConfigSubsection()
config.plugins.CommandCenter.autoScroll = ConfigYesNo(default=True)

# File paths
COMMANDS_FILE = "/etc/enigma2/commandcenter_commands.json"
CUSTOM_COMMANDS_FILE = "/etc/enigma2/commandcenter_custom.json"
USER_CONFIG_FILE = "/etc/enigma2/commandcenter_config.json"
DEFAULT_COMMANDS_FILE = join(PLUGIN_ROOT, "default_commands.json")

screen_real = getDesktop(0).size()
screen_width = screen_real.width()
BackfPath = join(PLUGIN_ROOT, "skins")

if screen_width == 2560:
    skin_path = join(BackfPath, 'wqhd')
elif screen_width >= 1920:
    skin_path = join(BackfPath, 'fhd')
else:
    skin_path = join(BackfPath, 'hd')


def backup_file(filepath):
    """Create a backup of the file with a timestamp before overwriting it."""
    if exists(filepath):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{filepath}.{timestamp}.bak"
        try:
            shutil.copy2(filepath, backup_path)
            print(f"[CommandCenter] Backup created: {backup_path}")
        except Exception as e:
            print(f"[CommandCenter] Backup error {filepath}: {e}")


def load_default_commands():
    """Load default commands from the JSON file included in the plugin."""
    if exists(DEFAULT_COMMANDS_FILE):
        try:
            with open(DEFAULT_COMMANDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[CommandCenter] Error loading default commands: {e}")

    # Minimal fallback (should never be needed)
    return {"📁 System Info": [("uname -a", "Kernel information")]}


def load_predefined_commands():
    """Load predefined commands from the external file; create it if missing."""
    if not exists(COMMANDS_FILE):
        # First creation: copy default commands
        default_cmds = load_default_commands()
        try:
            with open(COMMANDS_FILE, "w", encoding="utf-8") as f:
                json.dump(default_cmds, f, indent=4, ensure_ascii=False)
            print(f"[CommandCenter] Command file created: {COMMANDS_FILE}")
        except Exception as e:
            print(f"[CommandCenter] Error creating {COMMANDS_FILE}: {e}")
            return default_cmds

    # Load from existing file
    try:
        with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[CommandCenter] Error reading {COMMANDS_FILE}: {e}")

        # In case of error, return defaults
        return load_default_commands()


def load_custom_commands():
    if exists(CUSTOM_COMMANDS_FILE):
        try:
            with open(CUSTOM_COMMANDS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_custom_commands(commands):
    backup_file(CUSTOM_COMMANDS_FILE)
    with open(CUSTOM_COMMANDS_FILE, "w") as f:
        json.dump(commands, f, indent=4)


def load_user_config():
    if exists(USER_CONFIG_FILE):
        try:
            with open(USER_CONFIG_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"[CommandCenter] Config file corrupt: {e}")
            backup_file(USER_CONFIG_FILE)
            shutil.move(USER_CONFIG_FILE, USER_CONFIG_FILE + ".corrupt")
            data = {"disabled": [], "modified": {}}
        if "disabled" in data:
            data["disabled"] = [
                tuple(item) if isinstance(
                    item, list) else item for item in data["disabled"]]
        if "modified" in data:
            new_mod = {}
            for k, v in data["modified"].items():
                if isinstance(k, str) and "|" in k:
                    cat, cmd = k.split("|", 1)
                    new_mod[(cat, cmd)] = tuple(
                        v) if isinstance(v, list) else v
                else:
                    new_mod[k] = v
            data["modified"] = new_mod
        return data
    return {"disabled": [], "modified": {}}


def save_user_config(config):
    backup_file(USER_CONFIG_FILE)
    to_save = {}
    if "disabled" in config:
        to_save["disabled"] = [list(item) if isinstance(
            item, tuple) else item for item in config["disabled"]]
    if "modified" in config:
        new_mod = {}
        for k, v in config["modified"].items():
            if isinstance(k, tuple):
                new_mod[f"{k[0]}|{k[1]}"] = list(
                    v) if isinstance(v, tuple) else v
            else:
                new_mod[k] = v
        to_save["modified"] = new_mod
    try:
        with open(USER_CONFIG_FILE, "w") as f:
            json.dump(to_save, f, indent=4)
    except Exception as e:
        print(f"[CommandCenter] Save error: {e}")


def get_commands():
    user_config = load_user_config()
    disabled = set(user_config.get("disabled", []))
    modified = user_config.get("modified", {})
    custom = load_custom_commands()
    predefined = load_predefined_commands()

    commands = {}
    for category, items in predefined.items():
        cmd_list = []
        for cmd, desc in items:
            if (category, cmd) in disabled:
                continue
            key = (category, cmd)
            if key in modified:
                cmd, desc = modified[key]
            cmd_list.append((cmd, desc))
        if cmd_list:
            commands[category] = cmd_list

    if custom:
        commands["Custom"] = [
            (item["command"], item["description"]) for item in custom]

    return commands


class CategoryScreen(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = join(skin_path, 'CategoryScreen.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self["categories"] = MenuList([])
        self["key_blue"] = Label(_("Manager"))
        self["statusbar"] = Label(_("Press Manager to manage custom commands"))
        self["actions"] = ActionMap(["OkCancelActions",
                                     "ColorActions",
                                     "DirectionActions",
                                     "InfoActions",
                                     "MenuActions"],
                                    {"ok": self.select_category,
                                     "cancel": self.close,
                                     "red": self.close,
                                     "blue": self.open_manager,
                                     "up": self.categories_up,
                                     "down": self.categories_down,
                                     "info": self.show_info,
                                     "menu": self.open_debug_screen,
                                     },
                                    -1)
        self.populate_categories()

    def open_debug_screen(self):
        self.session.open(DebugScreen)

    def populate_categories(self):
        cmds = get_commands()
        cat_list = [(cat, cat) for cat in cmds.keys()]
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

    def open_manager(self):
        self.session.open(ManagerScreen, self.refresh_categories)

    def refresh_categories(self):
        self.populate_categories()

    def show_info(self):
        self.session.open(
            MessageBox, _(
                "Command Center - Telnet/Shell Plugin v.%s - by Lululla." %
                __version__), MessageBox.TYPE_INFO)


class CommandScreen(Screen):

    def __init__(self, session, category_name):
        Screen.__init__(self, session)
        self.session = session
        skin = join(skin_path, 'CommandScreen.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.category_name = category_name
        self.commands = get_commands()[category_name]
        self.container = None
        self.output_text = ""
        self.menu_items = [(desc, cmd) for (cmd, desc) in self.commands]
        self.setTitle(
            "Command Center by Lululla v.%s - %s" %
            (__version__, self.category_name))
        self["command_list"] = MenuList([])
        self["command_list"].setList(self.menu_items)
        self["output_area"] = ScrollLabel("")
        self["output_area"].setText(_("Select a command and press Run.\n\n"))
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Run"))
        self["key_yellow"] = Label(_("Clear"))
        self["key_blue"] = Label(_("Save"))
        self["key_info"] = Label(_("Info"))
        self["statusbar"] = Label(_("Ready"))
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "InfoActions"], {
            "ok": self.execute_command,
            "cancel": self.close,
            "red": self.close,
            "green": self.execute_command,
            "yellow": self.clear_output,
            "blue": self.save_output,
            "info": self.show_command_info,
            'up': self['command_list'].up,
            'down': self['command_list'].down,
            'left': self['output_area'].pageUp,
            'right': self['output_area'].pageDown,
            "upUp": self.pageUp,
            "leftUp": self.pageUp,
            "downUp": self.pageDown,
            "rightUp": self.pageDown,
        }, -1)
        self["command_list"].onSelectionChanged.append(
            self.on_selection_changed)

    def pageUp(self):
        self["output_area"].pageUp()

    def pageDown(self):
        self["output_area"].pageDown()

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
        except (UnicodeDecodeError, TypeError):
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


class ManagerScreen(Screen):

    def __init__(self, session, refresh_callback=None):
        Screen.__init__(self, session)
        self.session = session
        skin = join(skin_path, 'ManagerScreen.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.refresh_callback = refresh_callback
        self.custom_commands = []
        self.user_config = {}
        self.disabled = set()
        self.modified = {}
        self.setTitle("Command Center by Lululla v.%s" % __version__)
        self["command_list"] = MenuList([])
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Add Custom"))
        self["key_yellow"] = Label(_("Edit"))
        self["key_blue"] = Label(_("Delete/Disable"))
        self["key_info"] = Label(_("Toggle Disable"))
        self["statusbar"] = Label(_("Ready"))
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "InfoActions"], {
            "cancel": self.close,
            "red": self.close,
            "green": self.add_custom_command,
            "yellow": self.edit_item,
            "blue": self.delete_or_disable,
            "info": self.toggle_disable,
            "up": self.move_up,
            "down": self.move_down,
            "pageUp": self.page_up,
            "pageDown": self.page_down,
            "ok": self.select_item,
        }, -1)
        self.onLayoutFinish.append(self.init_ui)

    def init_ui(self):
        self.custom_commands = load_custom_commands()
        self.user_config = load_user_config()
        self.disabled = set(self.user_config.get("disabled", []))
        self.modified = self.user_config.get("modified", {})
        self.build_full_list()
        self.update_status()
        self.setFocus(self["command_list"])

    def build_full_list(self):
        predefined = load_predefined_commands()
        self.full_list = []
        self.item_types = []
        self.item_keys = []

        for category, items in predefined.items():
            for cmd, desc in items:
                key = (category, cmd)
                cur_cmd, cur_desc = self.modified.get(key, (cmd, desc))
                display = f"{category} : {cur_cmd[:40]} : {cur_desc[:30]}"
                if key in self.disabled:
                    display = "[DISABLED] " + display
                self.full_list.append(display)
                self.item_types.append('predef')
                self.item_keys.append(key)

        for idx, item in enumerate(self.custom_commands):
            display = f"CUSTOM : {item['command'][:40]} : {item['description'][:30]}"
            self.full_list.append(display)
            self.item_types.append('custom')
            self.item_keys.append(idx)

        self["command_list"].setList(self.full_list)

    def move_up(self):
        self["command_list"].up()
        self.update_status()

    def move_down(self):
        self["command_list"].down()
        self.update_status()

    def page_up(self):
        self["command_list"].pageUp()
        self.update_status()

    def page_down(self):
        self["command_list"].pageDown()
        self.update_status()

    def select_item(self):
        idx, typ, key = self.get_selection()
        if idx != -1:
            self.edit_item()

    def get_selection(self):
        idx = self["command_list"].getCurrentIndex()
        if idx is not None and idx < len(self.full_list):
            return idx, self.item_types[idx], self.item_keys[idx]
        return -1, None, None

    def update_status(self):
        self["statusbar"].setText(
            _("Total: %d commands (Predefined: %d, Custom: %d, Disabled: %d)") %
            (len(
                self.full_list), len(
                [
                    t for t in self.item_types if t == 'predef']), len(
                    self.custom_commands), len(
                        self.disabled)))

    def refresh(self):
        self.custom_commands = load_custom_commands()
        self.user_config = load_user_config()
        self.disabled = set(self.user_config.get("disabled", []))
        self.modified = self.user_config.get("modified", {})
        self.build_full_list()
        self.update_status()
        if self.refresh_callback:
            self.refresh_callback()

    def add_custom_command(self):
        self.session.openWithCallback(
            self.add_command_step1,
            InputBox,
            title=_("Enter command"),
            text="")

    def add_command_step1(self, command):
        if command:
            self.session.openWithCallback(lambda desc: self.add_command_step2(
                command, desc), InputBox, title=_("Enter description"), text="")

    def add_command_step2(self, command, description):
        if description:
            self.custom_commands.append(
                {"command": command, "description": description})
            save_custom_commands(self.custom_commands)
            self.refresh()

    def edit_item(self):
        idx, typ, key = self.get_selection()
        if idx == -1:
            return
        if typ == 'custom':
            item = self.custom_commands[key]
            self.session.openWithCallback(lambda new_cmd: self.edit_custom_command_step2(
                key, new_cmd), InputBox, title=_("Edit command"), text=item["command"])
        else:
            category, orig_cmd = key
            cur_cmd, cur_desc = self.modified.get(
                key, (orig_cmd, self.get_original_desc(category, orig_cmd)))
            self.session.openWithCallback(
                lambda new_cmd: self.edit_predef_command_step2(
                    key, new_cmd), InputBox, title=_("Edit command (original: %s)") %
                orig_cmd, text=cur_cmd)

    def edit_custom_command_step2(self, idx, new_cmd):
        if new_cmd:
            self.session.openWithCallback(
                lambda new_desc: self.edit_custom_command_step3(
                    idx,
                    new_cmd,
                    new_desc),
                InputBox,
                title=_("Edit description"),
                text=self.custom_commands[idx]["description"])

    def edit_custom_command_step3(self, idx, new_cmd, new_desc):
        if new_desc:
            self.custom_commands[idx]["command"] = new_cmd
            self.custom_commands[idx]["description"] = new_desc
            save_custom_commands(self.custom_commands)
            self.refresh()

    def get_original_desc(self, category, cmd):
        predefined = load_predefined_commands()
        for cat, items in predefined.items():
            if cat == category:
                for orig_cmd, orig_desc in items:
                    if orig_cmd == cmd:
                        return orig_desc
        return ""

    def edit_predef_command_step2(self, key, new_cmd):
        if new_cmd:
            category, orig_cmd = key
            orig_desc = self.get_original_desc(category, orig_cmd)
            self.session.openWithCallback(lambda new_desc: self.edit_predef_command_step3(
                key, new_cmd, new_desc), InputBox, title=_("Edit description"), text=orig_desc)

    def edit_predef_command_step3(self, key, new_cmd, new_desc):
        if new_desc:
            self.modified[key] = (new_cmd, new_desc)
            self.user_config["modified"] = self.modified
            save_user_config(self.user_config)
            self.refresh()

    def delete_or_disable(self):
        idx, typ, key = self.get_selection()
        if idx == -1:
            return
        if typ == 'custom':
            self.session.openWithCallback(
                self.confirm_delete_custom,
                MessageBox,
                _("Delete this custom command?\n%s") %
                self.custom_commands[key]["command"],
                MessageBox.TYPE_YESNO)
        else:
            self.toggle_disable()

    def confirm_delete_custom(self, answer):
        if answer:
            idx, typ, key = self.get_selection()
            if typ == 'custom':
                del self.custom_commands[key]
                save_custom_commands(self.custom_commands)
                self.refresh()

    def toggle_disable(self):
        idx, typ, key = self.get_selection()
        if idx == -1 or typ != 'predef':
            self["statusbar"].setText(
                _("Only predefined commands can be disabled/enabled"))
            return
        if key in self.disabled:
            self.disabled.remove(key)
        else:
            self.disabled.add(key)
        self.user_config["disabled"] = list(self.disabled)
        save_user_config(self.user_config)
        self.refresh()


class DebugScreen(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = join(skin_path, 'DebugScreen.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setTitle("Command Center - Debug Mode")

        self["debug_list"] = MenuList([])
        self["log_list"] = MenuList([])
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Run"))
        self["key_yellow"] = Label(_("Show Logs"))
        self["key_blue"] = Label(_("Delete Log"))
        self["statusbar"] = Label(_("Select a debug command and press Run"))

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "InfoActions"], {
            "cancel": self.close,
            "red": self.close,
            "green": self.run_debug_command,
            "yellow": self.toggle_logs,
            "blue": self.delete_selected_log,
            "ok": self.handle_ok,
            "info": self.handle_info,
            "up": self.move_up,
            "down": self.move_down,
        }, -1)

        self.logs_visible = False
        self.debug_commands = [
            ("init 4 ; killall -9 enigma2 ; ENIGMA_DEBUG_LVL=4 enigma2", "🔄 Full debug restart (OE-Alliance)"),
            ("init 4 ; killall -9 enigma2", "🛑 Stop Enigma2 only"),
            ("journalctl -u enigma2 > /tmp/enigma2.log", "📋 Enigma2 journal log (DreamBox)"),
            ("journalctl > /tmp/full_system.log", "📋 Full system journal (DreamBox)"),
            ("journalctl -f -u enigma2 > /tmp/enigma2_running.log &", "📡 Continuous Enigma2 log (DreamBox)"),
            ("grab -d -j -o /tmp/grab_debug.jpg", "📸 Screenshot with debug info"),
        ]
        self.current_logs = []
        self.onLayoutFinish.append(self.init_ui)

    def init_ui(self):
        self.populate_debug_list()
        self.scan_logs()
        self["log_list"].hide()
        self["debug_list"].show()
        self.setFocus(self["debug_list"])

    def populate_debug_list(self):
        # solo descrizioni
        items = [desc for (cmd, desc) in self.debug_commands]
        self["debug_list"].setList(items)

    def handle_ok(self):
        if self.logs_visible:
            self.show_log_content()
        else:
            self.run_debug_command()

    def handle_info(self):
        if self.logs_visible:
            self.show_log_content()

    def toggle_logs(self):
        self.logs_visible = not self.logs_visible
        if self.logs_visible:
            self.scan_logs()
            self["debug_list"].hide()
            self["log_list"].show()
            self.setFocus(self["log_list"])
            self["statusbar"].setText(
                _("Log files found: %d | Press Info for show") % len(
                    self.current_logs))
            self["key_yellow"].setText(_("Hide Logs"))
            self["key_green"].setText("")
            self["key_green"].hide()
        else:
            self["debug_list"].show()
            self["log_list"].hide()
            self.setFocus(self["debug_list"])
            self["statusbar"].setText(
                _("Select a debug command and press Run"))
            self["key_yellow"].setText(_("Show Logs"))
            self["key_green"].setText(_("Run"))
            self["key_green"].show()

    def move_up(self):
        if self.logs_visible:
            self["log_list"].up()
        else:
            self["debug_list"].up()

    def move_down(self):
        if self.logs_visible:
            self["log_list"].down()
        else:
            self["debug_list"].down()

    def run_debug_command(self):
        if self.logs_visible:
            print("run_debug_command: self.logs_visible")
            return
        idx = self["debug_list"].getCurrentIndex()
        if idx is None or idx >= len(self.debug_commands):
            return
        cmd, desc = self.debug_commands[idx]
        self.session.openWithCallback(
            lambda answer: self.confirm_run(
                answer,
                cmd,
                desc),
            MessageBox,
            _("⚠️ WARNING ⚠️\n\nThis debug command may restart or crash Enigma2.\n\nCommand: %s\n\n%s\n\nPress OK to execute or Cancel to abort.") %
            (desc,
             cmd),
            MessageBox.TYPE_YESNO,
            windowTitle=_("Confirm Debug Command"))

    def confirm_run(self, answer, cmd, desc):
        if not answer:
            return
        self.close()
        import tempfile
        log_dir = "/home/root/logs"
        if not exists(log_dir):
            os.makedirs(log_dir)
        log_filename = join(
            log_dir, "debug_%s.log" %
            datetime.now().strftime("%Y%m%d_%H%M%S"))
        script_content = f"""#!/bin/sh
    log="{log_filename}"
    echo "=== Command: {cmd} ===" > $log
    echo "Started at: $(date)" >> $log
    echo "=== Output ===" >> $log
    sync
    {cmd} >> $log 2>&1
    echo "=== Exit code: $? ===" >> $log
    echo "Finished at: $(date)" >> $log
    sync
    rm -f $0
    """
        fd, script_path = tempfile.mkstemp(suffix='.sh', prefix='debug_')
        with os.fdopen(fd, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        os.system(f"nohup {script_path} > /dev/null 2>&1 &")

    def scan_logs(self):
        import glob
        self.current_logs = []
        patterns = [
            "/tmp/*debug*.log",
            "/tmp/enigma2*.log",
            "/tmp/full*.log",
            "/tmp/grab*.log",
            "/home/root/logs/*.log",
            "/home/root/logs/debug_*.log",
            "/home/root/debug_*.log",
            "/home/root/.log",
        ]
        for pattern in patterns:
            self.current_logs.extend(glob.glob(pattern))
        self.current_logs = list(set(self.current_logs))
        self.current_logs.sort(key=getmtime, reverse=True)
        self["log_list"].setList(self.current_logs)

    def show_log_content(self):
        if not self.logs_visible:
            print("show_log_content: if not self.logs_visible")
            return
        idx = self["log_list"].getCurrentIndex()
        if idx is not None and idx < len(self.current_logs):
            logfile = self.current_logs[idx]
            self.session.open(LogViewer, logfile)

    def delete_selected_log(self):
        if not self.logs_visible:
            print("delete_selected_log: if not self.logs_visible")
            return
        idx = self["log_list"].getCurrentIndex()
        if idx is not None and idx < len(self.current_logs):
            logfile = self.current_logs[idx]
            self.session.openWithCallback(
                lambda answer: self.confirm_delete(answer, logfile),
                MessageBox,
                _("Delete log file?\n%s") % logfile,
                MessageBox.TYPE_YESNO
            )

    def confirm_delete(self, answer, logfile):
        if answer:
            try:
                os.remove(logfile)
                self.scan_logs()
                self["log_list"].setList(self.current_logs)
                self["statusbar"].setText(_("Deleted: %s") % basename(logfile))
            except Exception as e:
                self["statusbar"].setText(_("Error deleting: %s") % str(e))


class LogViewer(Screen):
    def __init__(self, session, logfile):
        self.session = session
        Screen.__init__(self, session)
        skin = join(skin_path, 'LogViewer.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.logfile = logfile
        self.current_view = "full"
        self.full_text = ""
        self.error_text = ""
        self.setTitle(_("Debug Log: %s") % basename(logfile))

        self["full_text"] = ScrollLabel("")
        self["error_text"] = ScrollLabel("")
        self["key_red"] = Label(_("Close"))
        self["key_green"] = Label(_("Error Only"))

        self["actions"] = ActionMap(["DirectionActions", "ColorActions", "OkCancelActions"], {
            "cancel": self.exit,
            "ok": self.exit,
            "red": self.exit,
            "green": self.switch_view,
            "up": self.page_up,
            "down": self.page_down,
            "left": self.page_up,
            "right": self.page_down,
            "pageUp": self.page_up,
            "pageDown": self.page_down,
        }, -1)

        self.onLayoutFinish.append(self.load_log)

    def load_log(self):
        try:
            with open(self.logfile, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            self.full_text = content
            lines = content.splitlines()
            error_lines = []
            for i, line in enumerate(lines):
                if "Traceback (most recent call last):" in line or "Backtrace:" in line:
                    for j in range(i, min(i + 30, len(lines))):
                        error_lines.append(lines[j])
                    break
            if not error_lines:
                for line in lines:
                    if "Error:" in line or "Exception:" in line or "FATAL" in line:
                        error_lines.append(line)
            if not error_lines:
                error_lines = [_("No specific error trace found in log")]

            self.error_text = "\n".join(error_lines)

        except Exception as e:
            msg = _("Error reading log: %s") % str(e)
            self.full_text = msg
            self.error_text = msg

        self["full_text"].setText(self.full_text)
        self["error_text"].setText(self.error_text)

        self["full_text"].show()
        self["error_text"].hide()
        self["key_green"].setText(_("Error Only"))

    def switch_view(self):
        if self.current_view == "full":
            self.current_view = "error"
            self["full_text"].hide()
            self["error_text"].show()
            self["key_green"].setText(_("Full Log"))
        else:
            self.current_view = "full"
            self["full_text"].show()
            self["error_text"].hide()
            self["key_green"].setText(_("Error Only"))

        self["full_text"].lastPage()
        self["error_text"].lastPage()

    def page_up(self):
        if self.current_view == "full":
            self["full_text"].pageUp()
        else:
            self["error_text"].pageUp()

    def page_down(self):
        if self.current_view == "full":
            self["full_text"].pageDown()
        else:
            self["error_text"].pageDown()

    def exit(self):
        self.close()


def main(session, **kwargs):
    session.open(CategoryScreen)


def Plugins(**kwargs):
    from Plugins.Plugin import PluginDescriptor
    return [
        PluginDescriptor(
            name=_("Command Center v.%s" % __version__),
            description=_("Run telnet/shell commands on Enigma2"),
            where=[
                PluginDescriptor.WHERE_PLUGINMENU,
                PluginDescriptor.WHERE_EXTENSIONSMENU],
            icon="icon.png",
            fnc=main)
    ]

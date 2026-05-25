#!/bin/bash
## setup command=wget -q --no-check-certificate https://raw.githubusercontent.com/OwnerPlugins/CommandCenter/main/installer.sh -O - | /bin/sh
version='1.0'
changelog='Recoded and porting to Python3\nAdd AI Translate'
TMPPATH=/tmp/CommandCenter-install
FILEPATH=/tmp/CommandCenter-main.tar.gz

echo "Starting CommandCenter installation..."

# Determine plugin path based on architecture
if [ ! -d /usr/lib64 ]; then
    PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/CommandCenter
else
    PLUGINPATH=/usr/lib64/enigma2/python/Plugins/Extensions/CommandCenter
fi

# Cleanup function
cleanup() {
    echo "Cleaning up temporary files..."
    [ -d "$TMPPATH" ] && rm -rf "$TMPPATH"
    [ -f "$FILEPATH" ] && rm -f "$FILEPATH"
    [ -d "/tmp/CommandCenter-main" ] && rm -rf "/tmp/CommandCenter-main"
}

# Detect OS type
detect_os() {
    if [ -f /var/lib/dpkg/status ]; then
        OSTYPE="DreamOs"
        STATUS="/var/lib/dpkg/status"
    elif [ -f /etc/opkg/opkg.conf ] || [ -f /var/lib/opkg/status ]; then
        OSTYPE="OE"
        STATUS="/var/lib/opkg/status"
    else
        OSTYPE="Unknown"
        STATUS=""
    fi
    echo "Detected OS type: $OSTYPE"
}
detect_os

# Cleanup before starting
cleanup
mkdir -p "$PLUGINPATH"

# Install wget if missing
if ! command -v wget >/dev/null 2>&1; then
    echo "Installing wget..."
    case "$OSTYPE" in
        "DreamOs")
            apt-get update && apt-get install -y wget || { echo "Failed to install wget"; exit 1; }
            ;;
        "OE")
            opkg update && opkg install wget || { echo "Failed to install wget"; exit 1; }
            ;;
        *)
            echo "Unsupported OS type. Cannot install wget."
            exit 1
            ;;
    esac
fi

# Detect Python version
if python --version 2>&1 | grep -q '^Python 3\.'; then
    echo "Python3 image detected"
    PYTHON="PY3"
    Packagerequests="python3-requests"
else
    echo "Python2 image detected"
    PYTHON="PY2"
    Packagerequests="python-requests"
fi

# Install required packages
install_pkg() {
    local pkg=$1
    if [ -z "$STATUS" ] || ! grep -qs "Package: $pkg" "$STATUS" 2>/dev/null; then
        echo "Installing $pkg..."
        case "$OSTYPE" in
            "DreamOs")
                apt-get update && apt-get install -y "$pkg" || { echo "Could not install $pkg, continuing anyway..."; }
                ;;
            "OE")
                opkg update && opkg install "$pkg" || { echo "Could not install $pkg, continuing anyway..."; }
                ;;
            *)
                echo "Cannot install $pkg on unknown OS type, continuing..."
                ;;
        esac
    else
        echo "$pkg already installed"
    fi
}
# Install Python requests
install_pkg "$Packagerequests"

# Download and extract
echo "Downloading CommandCenter..."
wget --no-check-certificate 'https://github.com/OwnerPlugins/CommandCenter/archive/refs/heads/main.tar.gz' -O "$FILEPATH"
if [ $? -ne 0 ]; then
    echo "Failed to download CommandCenter package!"
    cleanup
    exit 1
fi

echo "Extracting package..."
mkdir -p "$TMPPATH"
tar -xzf "$FILEPATH" -C "$TMPPATH"
if [ $? -ne 0 ]; then
    echo "Failed to extract CommandCenter package!"
    cleanup
    exit 1
fi

# Install plugin files
echo "Installing plugin files..."
# Find the correct directory in the extracted structure
if [ -d "$TMPPATH/CommandCenter-main" ]; then
    cp -rf "$TMPPATH/CommandCenter-main/"* "$PLUGINPATH/"
elif [ -d "$TMPPATH/CommandCenter-main/CommandCenter" ]; then
    cp -rf "$TMPPATH/CommandCenter-main/CommandCenter/"* "$PLUGINPATH/"
else
    cp -rf "$TMPPATH/"* "$PLUGINPATH/"
fi

# Final cleanup
cleanup

echo "CommandCenter installed successfully!"
echo "Please restart Enigma2 to complete the installation."

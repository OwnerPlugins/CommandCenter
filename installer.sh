#!/bin/sh

set -e

PLUGIN_NAME="CommandCenter"
PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_NAME"
TMPPATH="/tmp/$PLUGIN_NAME-install"
FILEPATH="/tmp/$PLUGIN_NAME-main.tar.gz"
GITHUB_URL="https://github.com/OwnerPlugins/CommandCenter/archive/refs/heads/main.tar.gz"

cleanup() {
    echo "Cleaning up temporary files..."
    rm -rf "$TMPPATH"
    rm -f "$FILEPATH"
}

echo "Starting $PLUGIN_NAME installation..."

# Detect OS type
if [ -f /etc/opkg/opkg.conf ]; then
    OS="OE"
    echo "Detected OS type: OE"
else
    OS="other"
    echo "Detected OS type: $OS"
fi

cleanup

# Check Python version
if command -v python3 >/dev/null 2>&1; then
    echo "Python3 image detected"
    PYTHON="python3"
else
    echo "Python2 image detected (deprecated)"
    PYTHON="python"
fi

# Install python-requests if missing
if ! $PYTHON -c "import requests" 2>/dev/null; then
    echo "Installing python-requests..."
    if [ "$OS" = "OE" ]; then
        opkg update >/dev/null 2>&1
        opkg install python3-requests
    else
        echo "Please install python-requests manually"
    fi
else
    echo "python3-requests already installed"
fi

echo "Downloading $PLUGIN_NAME..."
wget --no-check-certificate "$GITHUB_URL" -O "$FILEPATH"
if [ $? -ne 0 ]; then
    echo "Failed to download $PLUGIN_NAME package!"
    cleanup
    exit 1
fi

echo "Extracting package..."
mkdir -p "$TMPPATH"
tar -xzf "$FILEPATH" -C "$TMPPATH"
if [ $? -ne 0 ]; then
    echo "Failed to extract $PLUGIN_NAME package!"
    cleanup
    exit 1
fi

echo "Installing $PLUGIN_NAME..."
# Find the extracted folder (it will be like CommandCenter-main)
EXTRACTED_DIR=$(find "$TMPPATH" -maxdepth 1 -type d -name "CommandCenter*" | head -n 1)
if [ -z "$EXTRACTED_DIR" ]; then
    echo "Could not find extracted plugin directory!"
    cleanup
    exit 1
fi

# Create plugin directory if it doesn't exist
mkdir -p "$PLUGIN_DIR"

# Copy plugin files
cp -r "$EXTRACTED_DIR"/* "$PLUGIN_DIR/"
if [ $? -ne 0 ]; then
    echo "Failed to copy plugin files!"
    cleanup
    exit 1
fi

# Set permissions
chmod 755 "$PLUGIN_DIR/plugin.py"

cleanup

echo "$PLUGIN_NAME installed successfully!"
echo "Please restart Enigma2 GUI."
exit 0

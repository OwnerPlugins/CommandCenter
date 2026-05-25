#!/bin/sh
PLUGIN_NAME="CommandCenter"
TARGET_DIR="/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_NAME"
TEMP_DIR="/tmp/$PLUGIN_NAME-install"
FILEPATH="/tmp/$PLUGIN_NAME-main.tar.gz"

echo "Starting $PLUGIN_NAME installation..."

cleanup() {
    echo "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR" "$FILEPATH" 2>/dev/null
}

# Check Python3
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3 not found! This plugin requires Python3."
    exit 1
fi
echo "Python3 image detected"

# Check requests module
if ! python3 -c "import requests" 2>/dev/null; then
    echo "python3-requests not found. Installing..."
    if command -v opkg >/dev/null 2>&1; then
        opkg update && opkg install python3-requests
    elif command -v apt-get >/dev/null 2>&1; then
        apt-get update && apt-get install python3-requests -y
    else
        echo "Cannot install python3-requests. Please install manually."
        exit 1
    fi
else
    echo "python3-requests already installed"
fi

# Create target directory
mkdir -p "$TARGET_DIR"

# Download
echo "Downloading $PLUGIN_NAME..."
wget --no-check-certificate "https://github.com/OwnerPlugins/CommandCenter/archive/refs/heads/main.tar.gz" -O "$FILEPATH"
if [ $? -ne 0 ]; then
    echo "Failed to download package!"
    cleanup
    exit 1
fi

# Extract to temp directory
echo "Extracting package..."
mkdir -p "$TEMP_DIR"
tar -xzf "$FILEPATH" -C "$TEMP_DIR"
if [ $? -ne 0 ]; then
    echo "Failed to extract package!"
    cleanup
    exit 1
fi

# Find the actual plugin source directory (inside the extracted repo)
SOURCE_DIR=$(find "$TEMP_DIR" -type d -path "*/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_NAME" | head -n 1)
if [ -z "$SOURCE_DIR" ]; then
    echo "Could not find plugin source directory in the package!"
    cleanup
    exit 1
fi

# Copy plugin files to target
echo "Installing $PLUGIN_NAME..."
cp -rf "$SOURCE_DIR"/* "$TARGET_DIR/"

# Set permissions
chmod 755 "$TARGET_DIR/plugin.py" 2>/dev/null

cleanup
echo "$PLUGIN_NAME installed successfully! Restart Enigma2."

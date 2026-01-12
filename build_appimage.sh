#!/bin/bash
# Build script for Linux AppImage

set -e

echo "Building ER:LC Livery Maker AppImage..."

# Create build directory
BUILD_DIR="build/AppImage"
APP_DIR="$BUILD_DIR/ERLC_Livery_Maker.AppDir"

rm -rf "$BUILD_DIR"
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

# Install dependencies in virtual environment
echo "Setting up Python environment..."
python3 -m venv "$BUILD_DIR/venv"
source "$BUILD_DIR/venv/bin/activate"
pip install -r requirements.txt
pip install pyinstaller

# Build with PyInstaller
echo "Building with PyInstaller..."
pyinstaller --clean --onedir \
    --name ERLC_Livery_Maker \
    --add-data "config.json:." \
    --add-data "templates:templates" \
    --hidden-import PIL \
    --hidden-import PIL._imaging \
    --hidden-import PIL._tkinter_finder \
    --hidden-import cv2 \
    --hidden-import numpy \
    --hidden-import replicate \
    --windowed \
    src/main_tk.py

# Copy entire dist folder to AppDir
cp -r dist/ERLC_Livery_Maker/* "$APP_DIR/usr/bin/"

# Create desktop entry
cat > "$APP_DIR/erlc-livery-maker.desktop" << EOF
[Desktop Entry]
Type=Application
Name=ER:LC Livery Maker
Comment=Generate custom vehicle liveries for ER:LC
Exec=ERLC_Livery_Maker
Icon=erlc-livery-maker
Categories=Graphics;Utility;
Terminal=false
EOF

# Copy desktop file to proper location as well
cp "$APP_DIR/erlc-livery-maker.desktop" "$APP_DIR/usr/share/applications/"

# Create a simple icon (placeholder text file for now)
echo "ERLC" > "$APP_DIR/erlc-livery-maker.png"

# Create AppRun script
cat > "$APP_DIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/bin:${HERE}/usr/lib:${LD_LIBRARY_PATH}"
cd "${HERE}"
exec "${HERE}/usr/bin/ERLC_Livery_Maker" "$@"
EOF

chmod +x "$APP_DIR/AppRun"

# Download appimagetool if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppImage
echo "Creating AppImage..."
ARCH=x86_64 ./appimagetool-x86_64.AppImage "$APP_DIR" "ERLC_Livery_Maker-x86_64.AppImage"

echo "Build complete! AppImage: ERLC_Livery_Maker-x86_64.AppImage"

deactivate

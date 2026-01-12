# Quick Start Guide

## Installation (First Time Setup)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get your Replicate API key:**
   - Go to https://replicate.com/
   - Sign up for an account
   - Navigate to your account settings
   - Copy your API token

3. **Run the application:**
   - **Linux/Mac:** `./run.sh`
   - **Windows:** Double-click `run.bat` or run `python src/main.py`

## Using the App

### First Launch

1. When the app opens, paste your Replicate API key in the "API Configuration" section
2. Click "Save API Key"

### Generating a Livery

1. **Select Vehicle:** Choose a vehicle from the dropdown (e.g., "Bullhorn Determinator SFP Fury 2022")

2. **Enter Description:** In the "Livery Description" box, describe what you want:
   ```
   Example: "police car with blue and white stripes, sheriff badge on doors"
   Example: "fire truck with red and yellow safety markings"
   Example: "taxi with yellow and black checkered pattern"
   ```

3. **Preview First:** Click "Generate Preview (Left View)"
   - This shows you the left side of the vehicle
   - Takes about 10-30 seconds
   - Check if it matches what you wanted

4. **Generate All Views:** If you like the preview, click "Generate All Views"
   - Generates Front, Rear, Right, and Top views
   - Takes about 2-5 minutes total
   - Watch the progress in the status bar

5. **Save:** Click "Save Livery" to export all 5 PNG files to the `output/` folder

### Apply to Multiple Vehicles

After generating a livery:
1. The "Apply to Other Vehicles" section appears
2. Check the vehicles you want to apply the same design to
3. Click "Apply to Selected Vehicles"
4. Each vehicle will get the same livery design

## Cost Estimates

Replicate charges per image generated:
- **Preview only:** ~$0.003-0.01
- **Full livery (5 views):** ~$0.015-0.05
- **10 vehicles:** ~$0.15-0.50

## Tips for Best Results

### Good Prompts:
- Be specific: "police car with blue stripes on white base"
- Mention colors: "red and white racing stripes"
- Include details: "sheriff star badge on door, number 42 on roof"

### Avoid:
- Vague prompts: "cool design"
- Complex scenes: "car driving through city"
- Multiple conflicting styles: "police and fire and taxi"

### Template Requirements:
- Templates must have white vehicle body
- Background should be light blue (like provided example)
- All 5 views required: Front, Rear, Left, Right, Top

## Troubleshooting

**"No vehicles found"**
- Check that the `templates/` folder exists
- Make sure vehicle folders contain all 5 PNG files with correct names

**"Generation failed"**
- Verify your API key is correct
- Check your internet connection
- Make sure you have credits in your Replicate account

**App won't start**
- Run: `pip install -r requirements.txt`
- Make sure you have Python 3.8 or newer

## Building Executables

### Windows .exe
```bash
pip install pyinstaller
pyinstaller build_windows.spec
```
Executable will be in: `dist/ERLC_Livery_Maker.exe`

### Linux AppImage
```bash
./build_appimage.sh
```
AppImage will be: `ERLC_Livery_Maker-x86_64.AppImage`

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Review example templates in `templates/` folder
- Test the mask generator: `python src/image_processor.py`

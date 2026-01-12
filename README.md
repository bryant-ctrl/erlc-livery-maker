# ER:LC Livery Maker

Desktop application for generating custom vehicle liveries for ER:LC using AI image generation.

## Features

- **AI-Powered Generation**: Uses Replicate API with Stable Diffusion inpainting
- **Preview First**: Generate a preview (Left view) before committing to all 5 views
- **Multi-View Support**: Generates all 5 vehicle views (Front, Rear, Left, Right, Top)
- **Multi-Vehicle**: Apply the same livery design to multiple vehicles
- **Cross-Platform**: Available for Windows (.exe) and Linux (AppImage)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Replicate API Key

1. Sign up at [Replicate](https://replicate.com/)
2. Get your API key from your account settings
3. Add it to `config.json` or enter it in the app

### 3. Add Templates

Place vehicle template folders in the `templates/` directory. Each vehicle folder should contain 5 PNG files:
- `*_Front.png`
- `*_Rear.png`
- `*_Left.png`
- `*_Right.png`
- `*_Top.png`

## Running the Application

### Development Mode

```bash
cd src
python main.py
```

### Building for Distribution

#### Windows (.exe)

1. Install PyInstaller: `pip install pyinstaller`
2. Run: `pyinstaller build_windows.spec`
3. Executable will be in `dist/ERLC_Livery_Maker.exe`

#### Linux (AppImage)

1. Run the build script: `./build_appimage.sh`
2. AppImage will be created: `ERLC_Livery_Maker-x86_64.AppImage`

## Usage

1. **Set API Key**: Enter your Replicate API key in the settings
2. **Select Vehicle**: Choose a vehicle from the dropdown
3. **Enter Prompt**: Describe your livery design (e.g., "police car with blue and white stripes")
4. **Generate Preview**: Click "Generate Preview" to see the Left view
5. **Review**: Check if the preview matches your expectations
6. **Generate All**: Click "Generate All Views" to create all 5 views
7. **Save**: Click "Save Livery" to export all views
8. **Multi-Vehicle** (Optional): Select other vehicles to apply the same design

## API Costs

Replicate API pricing (approximate):
- Stable Diffusion Inpainting: ~$0.003-0.01 per image
- Full livery (5 views): ~$0.015-0.05
- Preview only: ~$0.003-0.01

## Project Structure

```
ERLC Livery Maker/
├── src/
│   ├── main.py                      # Application entry point
│   ├── livery_generator_window.py   # Main GUI window
│   ├── template_manager.py          # Template scanning and management
│   ├── image_processor.py           # Mask generation and compositing
│   └── api_client.py                # Replicate API integration
├── templates/                       # Vehicle template folders
├── output/                          # Generated liveries
├── config.json                      # Configuration file
├── requirements.txt                 # Python dependencies
├── build_windows.spec              # PyInstaller spec for Windows
└── build_appimage.sh               # Build script for Linux AppImage
```

## Troubleshooting

### "No templates found"
- Make sure template folders are in `templates/` directory
- Each folder must have all 5 views with correct naming

### "Generation failed"
- Check your Replicate API key is correct
- Ensure you have internet connection
- Check Replicate API status

### "Mask not detecting vehicle"
- Template must have white vehicle body
- Adjust tolerance in `image_processor.py` if needed

## License

MIT License - Feel free to modify and distribute

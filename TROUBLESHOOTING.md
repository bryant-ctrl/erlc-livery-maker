# Troubleshooting Guide

## Generation Failed Error

If you're getting "Generation failed - check API key and connection", follow these steps:

### 1. Verify Dependencies Are Installed

Run from terminal:
```bash
cd "ERLC Livery Maker"
pip install -r requirements.txt
```

Or use the test script:
```bash
python3 test_api.py
```

### 2. Check Your API Key

**Get your API key:**
1. Go to https://replicate.com/
2. Sign in or create account
3. Click your profile → Account Settings
4. Copy your API token (starts with `r8_`)

**Add to the app:**
1. Open the app
2. Paste your full API key in "Replicate API Key" field
3. Click "Save API Key"
4. You should see "API key saved!" message

**Or edit config.json directly:**
```json
{
  "replicate_api_key": "r8_YOUR_ACTUAL_KEY_HERE",
  "output_directory": "output",
  "templates_directory": "templates"
}
```

### 3. Verify Internet Connection

```bash
ping -c 3 replicate.com
```

If this fails, check your internet connection.

### 4. Test API Connection

Run the test script:
```bash
python3 test_api.py
```

This will check:
- Dependencies installed
- API key present
- API connection working

### 5. Check Replicate Account

**Credits:** Replicate requires payment for API usage
- Go to https://replicate.com/account/billing
- Add a payment method
- Ensure you have credits

**Pricing:**
- Stable Diffusion Inpainting: ~$0.003-0.01 per image
- Preview (1 image): ~$0.01
- Full livery (5 images): ~$0.05

### 6. Check Model Availability

The app uses: `stability-ai/stable-diffusion-inpainting`

If this model is deprecated, you may need to update `config.json`:
```json
{
  "inpainting_model": "stability-ai/stable-diffusion-inpainting",
  "model_version": "latest"
}
```

## Common Issues

### "No module named 'replicate'"

**Solution:**
```bash
pip install -r requirements.txt
```

### "No module named 'tkinter'"

**Linux:**
```bash
sudo apt-get install python3-tk   # Ubuntu/Debian
sudo dnf install python3-tkinter   # Fedora
sudo pacman -S tk                  # Arch
```

**Windows:** Tkinter is included with Python

### API Key Not Saving

1. Check that `config.json` exists in the project directory
2. Ensure you have write permissions
3. Try editing `config.json` manually

### Very Slow Generation

**Normal behavior:**
- Preview (Left view): 20-60 seconds
- Full set (5 views): 2-5 minutes total

If it takes longer:
- Replicate servers may be busy
- Try again later
- Check Replicate status page

### Generation Succeeds But Output Looks Wrong

**Possible causes:**
1. **Mask detection issue:** White vehicle not detected properly
   - Check template has white vehicle body
   - Adjust tolerance in `src/image_processor.py` line 27

2. **Prompt too vague:** Be specific
   - Good: "police car with blue and white stripes, sheriff badge on doors"
   - Bad: "cool design"

3. **Template format:** Ensure templates match expected format
   - White vehicle body
   - Light blue background
   - PNG format
   - High resolution (4000px)

## Getting Help

### View Console Output

**Run from terminal to see detailed errors:**
```bash
# Linux/Mac
cd "ERLC Livery Maker"
python3 src/main_tk.py

# Windows
cd "ERLC Livery Maker"
python src\main_tk.py
```

### Enable Debugging

Edit `src/api_client.py` and check the error output - it prints to console.

### Test Individual Components

**Test template detection:**
```bash
python3 src/template_manager.py
```

**Test image processing:**
```bash
python3 src/image_processor.py
```

**Test API client:**
```bash
python3 test_api.py
```

## Still Having Issues?

1. Run the test script and copy output:
   ```bash
   python3 test_api.py > test_output.txt
   ```

2. Try running from terminal to see console errors:
   ```bash
   python3 src/main_tk.py
   ```

3. Check Replicate API status: https://replicate.com/status

4. Open an issue on GitHub: https://github.com/bryant-ctrl/erlc-livery-maker/issues
   - Include test script output
   - Include any error messages
   - Describe what you tried

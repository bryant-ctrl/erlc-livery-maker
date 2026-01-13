# Available AI Models for Livery Generation

This document lists the AI models you can use with the ER:LC Livery Maker, from best quality to most affordable.

## Recommended Models (Best to Cheapest)

### 1. FLUX.1 Fill [pro] - HIGHEST QUALITY ⭐
**Model ID:** `black-forest-labs/flux-fill-pro`

**Quality:** Best available - state-of-the-art inpainting
- Photorealistic results
- Excellent prompt understanding
- Maintains lighting and perspective
- Professional-grade output

**Cost:** $0.05 per image ($0.25 for full 5-view livery)

**Speed:** ~15-30 seconds per image

**When to use:** Final production liveries, important designs

### 2. FLUX Dev Inpainting - HIGH QUALITY
**Model ID:** `zsxkib/flux-dev-inpainting`

**Quality:** Excellent - nearly as good as Pro
- Very high quality results
- Good prompt following
- Open-weight model
- Great value for money

**Cost:** ~$0.01-0.02 per image ($0.05-0.10 for full livery)

**Speed:** ~30-50 seconds per image

**When to use:** Best balance of quality and cost

### 3. Stable Diffusion Inpainting - BUDGET
**Model ID:** `stability-ai/stable-diffusion-inpainting:95b7223...`

**Quality:** Good for testing
- Basic inpainting
- Can look artificial/low quality
- Good for quick tests
- Not recommended for final output

**Cost:** $0.0027 per image ($0.01 for full livery)

**Speed:** ~2 seconds per image

**When to use:** Testing prompts, previews only

## How to Change Models

### Method 1: Edit config.json (Recommended)

Open `config.json` and change the model:

```json
{
  "replicate_api_key": "YOUR_KEY",
  "inpainting_model": "black-forest-labs/flux-fill-pro",
  "output_directory": "output",
  "templates_directory": "templates"
}
```

### Method 2: Edit api_client.py

Edit `src/api_client.py` line 16 and change the default model:

```python
def __init__(self, api_key: str, model: str = "black-forest-labs/flux-fill-pro"):
```

## Model Comparison

| Model | Quality | Cost/Image | Cost/Livery | Speed | Best For |
|-------|---------|------------|-------------|-------|----------|
| FLUX.1 Fill [pro] | ⭐⭐⭐⭐⭐ | $0.05 | $0.25 | 15-30s | Final designs |
| FLUX Dev | ⭐⭐⭐⭐ | $0.01-0.02 | $0.05-0.10 | 30-50s | Production use |
| Stable Diffusion | ⭐⭐ | $0.0027 | $0.01 | 2s | Testing only |

## Tips for Better Results

### 1. Use Specific Prompts
**Good:** "police car with blue and white horizontal stripes, sheriff star badge on doors, number 42 on roof"

**Bad:** "cool police design"

### 2. Avoid 3D Elements
The AI should focus on flat graphics/decals only, not create headlights, windows, or realistic lighting.

**Add to your prompt:**
- "flat 2D design"
- "vehicle wrap design"
- "decals and graphics only"

### 3. Use Negative Prompts
The app automatically includes these negative prompts to avoid:
- headlights, taillights
- wheels, windows
- 3d render, realistic lighting
- shadows, reflections

### 4. Iterate with Cheaper Model First
1. Test your prompt with Stable Diffusion ($0.01 total)
2. Refine the prompt until you get close
3. Switch to FLUX Pro for final high-quality version ($0.25)

This saves money while perfecting your design!

## Sources

- [FLUX.1 Fill [pro] on Replicate](https://replicate.com/black-forest-labs/flux-fill-pro)
- [FLUX Dev Inpainting](https://replicate.com/zsxkib/flux-dev-inpainting)
- [Ideogram v2 Inpainting](https://replicate.com/blog/ideogram-v2-inpainting)
- [Stable Diffusion Inpainting](https://replicate.com/stability-ai/stable-diffusion-inpainting)
- [FLUX Image Generation Models](https://replicate.com/collections/flux)

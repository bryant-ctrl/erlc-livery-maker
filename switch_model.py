#!/usr/bin/env python3
"""
Quick script to switch between AI models
"""
import json
import sys

MODELS = {
    "1": {
        "name": "Ideogram v3 Turbo - BEST FOR TEXT",
        "id": "ideogram-ai/ideogram-v3-turbo",
        "cost": "$0.03/image ($0.15/livery)",
        "quality": "⭐⭐⭐⭐⭐ (text)"
    },
    "2": {
        "name": "FLUX.1 Fill [pro] - BEST QUALITY",
        "id": "black-forest-labs/flux-fill-pro",
        "cost": "$0.05/image ($0.25/livery)",
        "quality": "⭐⭐⭐⭐⭐"
    },
    "3": {
        "name": "FLUX Dev Inpainting - HIGH QUALITY",
        "id": "zsxkib/flux-dev-inpainting",
        "cost": "$0.01-0.02/image ($0.05-0.10/livery)",
        "quality": "⭐⭐⭐⭐"
    },
    "4": {
        "name": "Stable Diffusion - BUDGET (Testing Only)",
        "id": "stability-ai/stable-diffusion-inpainting:95b7223104132402a9ae91cc677285bc5eb997834bd2349fa486f53910fd68b3",
        "cost": "$0.0027/image ($0.01/livery)",
        "quality": "⭐⭐"
    }
}

def main():
    print("=" * 70)
    print("ER:LC Livery Maker - Model Selector")
    print("=" * 70)
    print()

    # Show available models
    print("Available Models:\n")
    for key, model in MODELS.items():
        print(f"{key}. {model['name']}")
        print(f"   Quality: {model['quality']}")
        print(f"   Cost: {model['cost']}")
        print(f"   ID: {model['id']}")
        print()

    # Get user choice
    choice = input("Select model (1-4) or 'q' to quit: ").strip()

    if choice.lower() == 'q':
        print("Cancelled.")
        return

    if choice not in MODELS:
        print("Invalid choice!")
        return

    selected = MODELS[choice]

    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found!")
        return

    # Update model
    config['inpainting_model'] = selected['id']

    # Save config
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print()
    print("=" * 70)
    print(f"✓ Model changed to: {selected['name']}")
    print(f"  Cost: {selected['cost']}")
    print("=" * 70)
    print()
    print("The new model will be used next time you generate a livery.")
    print()

if __name__ == "__main__":
    main()

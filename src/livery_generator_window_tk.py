"""
Livery Generator Window - Tkinter GUI (AppImage compatible)
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from pathlib import Path
from typing import Optional, Dict
from PIL import Image, ImageTk
import threading

from template_manager import TemplateManager
from image_processor import ImageProcessor
from api_client import ReplicateAPIClient


class LiveryGeneratorApp:
    """Main application window using Tkinter"""

    def __init__(self, root):
        self.root = root
        self.root.title("ER:LC Livery Maker")
        self.root.geometry("1000x800")

        # Load config
        self.config = self.load_config()

        # Initialize components
        self.template_manager = TemplateManager(self.config["templates_directory"])
        self.processor = ImageProcessor()
        self.api_client = None

        # State
        self.current_vehicle: Optional[str] = None
        self.current_prompt: str = ""
        self.preview_image: Optional[Image.Image] = None
        self.generated_views: Dict[str, Image.Image] = {}
        self.is_generating = False

        # Setup UI
        self.setup_ui()

        # Initialize API client if key is set
        if self.config.get("replicate_api_key"):
            self.api_client = ReplicateAPIClient(self.config["replicate_api_key"])

    def load_config(self) -> dict:
        """Load configuration from config.json"""
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {
            "replicate_api_key": "",
            "output_directory": "output",
            "templates_directory": "templates"
        }

    def save_config(self):
        """Save configuration to config.json"""
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=2)

    def setup_ui(self):
        """Setup the user interface"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        row = 0

        # API Key section
        api_frame = ttk.LabelFrame(main_frame, text="API Configuration", padding="5")
        api_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        row += 1

        ttk.Label(api_frame, text="Replicate API Key:").grid(row=0, column=0, padx=5)
        self.api_key_var = tk.StringVar(value=self.config.get("replicate_api_key", ""))
        api_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=50, show="*")
        api_entry.grid(row=0, column=1, padx=5)
        ttk.Button(api_frame, text="Save API Key", command=self.save_api_key).grid(row=0, column=2, padx=5)

        # Vehicle selection
        vehicle_frame = ttk.Frame(main_frame)
        vehicle_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        row += 1

        ttk.Label(vehicle_frame, text="Select Vehicle:").pack(side=tk.LEFT, padx=5)
        self.vehicle_var = tk.StringVar()
        vehicle_combo = ttk.Combobox(vehicle_frame, textvariable=self.vehicle_var, width=50)
        vehicle_combo['values'] = self.template_manager.get_vehicle_names()
        if vehicle_combo['values']:
            vehicle_combo.current(0)
            self.current_vehicle = vehicle_combo.get()
        vehicle_combo.bind('<<ComboboxSelected>>', self.on_vehicle_changed)
        vehicle_combo.pack(side=tk.LEFT, padx=5)

        # Prompt input
        prompt_frame = ttk.LabelFrame(main_frame, text="Livery Description", padding="5")
        prompt_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        row += 1

        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, width=80, height=4)
        self.prompt_text.pack(fill=tk.BOTH, expand=True)
        self.prompt_text.insert(1.0, "Example: police car with blue and white stripes, sheriff badge on doors")

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        row += 1

        self.preview_btn = ttk.Button(button_frame, text="Generate Preview (Left View)", command=self.generate_preview)
        self.preview_btn.pack(side=tk.LEFT, padx=5)

        self.generate_all_btn = ttk.Button(button_frame, text="Generate All Views", command=self.generate_all_views, state=tk.DISABLED)
        self.generate_all_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ttk.Button(button_frame, text="Save Livery", command=self.save_livery, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Preview area
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="5")
        preview_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)
        row += 1

        # Canvas for image display
        self.canvas = tk.Canvas(preview_frame, bg='white', height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)

    def save_api_key(self):
        """Save API key to config"""
        api_key = self.api_key_var.get().strip()
        self.config["replicate_api_key"] = api_key
        self.save_config()
        self.api_client = ReplicateAPIClient(api_key)
        messagebox.showinfo("Success", "API key saved!")

    def on_vehicle_changed(self, event=None):
        """Handle vehicle selection change"""
        self.current_vehicle = self.vehicle_var.get()
        self.preview_image = None
        self.generated_views.clear()
        self.status_var.set(f"Selected: {self.current_vehicle}")
        self.generate_all_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.canvas.delete("all")

    def generate_preview(self):
        """Generate preview (Left view only)"""
        if not self.api_client or not self.config.get("replicate_api_key"):
            messagebox.showerror("Error", "Please set your Replicate API key first!")
            return

        if not self.current_vehicle:
            messagebox.showerror("Error", "Please select a vehicle!")
            return

        prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not prompt or prompt.startswith("Example:"):
            messagebox.showerror("Error", "Please enter a livery description!")
            return

        self.current_prompt = prompt

        # Get Left template
        template_path = self.template_manager.get_template_path(self.current_vehicle, "Left")
        if not template_path:
            messagebox.showerror("Error", "Left template not found!")
            return

        # Start generation in thread
        self.start_generation(template_path, prompt, "Left", is_preview=True)

    def start_generation(self, template_path, prompt, view, is_preview=False):
        """Start image generation in background thread"""
        if self.is_generating:
            return

        self.is_generating = True
        self.preview_btn.config(state=tk.DISABLED)
        self.generate_all_btn.config(state=tk.DISABLED)
        self.progress.start(10)

        def generate():
            try:
                self.status_var.set(f"Loading template ({view})...")
                template = self.processor.load_template(template_path)

                self.status_var.set(f"Creating mask ({view})...")
                mask = self.processor.create_mask(template)

                self.status_var.set(f"Preparing images ({view})...")
                template_resized, mask_resized = self.processor.prepare_for_api(template, mask)

                self.status_var.set(f"Generating livery ({view})... This may take 20-60 seconds")
                generated = self.api_client.generate_inpainting(
                    template_resized,
                    mask_resized,
                    prompt,
                    view
                )

                if generated is None:
                    error_msg = "Generation failed - check API key and connection\n\nPossible issues:\n- Invalid API key\n- No internet connection\n- Insufficient Replicate credits\n- Model not available"
                    print(f"ERROR: {error_msg}")
                    self.root.after(0, lambda: self.on_error(error_msg))
                    return

                self.status_var.set(f"Compositing result ({view})...")
                if generated.size != template.size:
                    generated = generated.resize(template.size, Image.Resampling.LANCZOS)
                    mask = mask.resize(template.size, Image.Resampling.LANCZOS)

                final = self.processor.composite_result(template, generated, mask)

                self.root.after(0, lambda: self.on_generation_finished(final, view, is_preview))

            except Exception as e:
                import traceback
                error_details = f"{str(e)}\n\nDetails:\n{traceback.format_exc()}"
                self.root.after(0, lambda: self.on_error(error_details))

        thread = threading.Thread(target=generate, daemon=True)
        thread.start()

    def on_generation_finished(self, image: Optional[Image.Image], view: str, is_preview: bool):
        """Handle generation completion"""
        self.progress.stop()
        self.preview_btn.config(state=tk.NORMAL)
        self.is_generating = False

        if image is None:
            self.status_var.set("Generation failed!")
            return

        # Store the result
        if is_preview:
            self.preview_image = image
            self.generate_all_btn.config(state=tk.NORMAL)
            self.status_var.set(f"Preview generated! Review and click 'Generate All Views' to continue.")
        else:
            self.generated_views[view] = image
            self.status_var.set(f"Generated {view} view ({len(self.generated_views)}/5)")

        # Display the image
        self.display_image(image)

        # Check if all views are complete
        if len(self.generated_views) == 5:
            self.save_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Complete", "All views generated successfully!")

    def on_error(self, error_msg: str):
        """Handle generation error"""
        self.progress.stop()
        self.preview_btn.config(state=tk.NORMAL)
        self.is_generating = False
        self.status_var.set(f"Error: {error_msg}")
        messagebox.showerror("Error", error_msg)

    def display_image(self, image: Image.Image):
        """Display image in canvas"""
        # Resize image to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width < 100:  # Not initialized yet
            canvas_width = 900
            canvas_height = 400

        # Calculate scaling
        img_ratio = image.width / image.height
        canvas_ratio = canvas_width / canvas_height

        if img_ratio > canvas_ratio:
            new_width = canvas_width - 20
            new_height = int(new_width / img_ratio)
        else:
            new_height = canvas_height - 20
            new_width = int(new_height * img_ratio)

        # Resize image
        display_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(display_img)

        # Display on canvas
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.photo)

    def generate_all_views(self):
        """Generate all 5 views sequentially"""
        if not self.preview_image:
            messagebox.showerror("Error", "Please generate a preview first!")
            return

        # Clear previous results
        self.generated_views.clear()
        self.save_btn.config(state=tk.DISABLED)

        # Add the preview to results
        self.generated_views["Left"] = self.preview_image

        # Generate remaining views
        self.views_to_generate = ["Front", "Rear", "Right", "Top"]
        self.generate_next_view()

    def generate_next_view(self):
        """Generate the next view in sequence"""
        if not self.views_to_generate:
            return

        next_view = self.views_to_generate.pop(0)
        template_path = self.template_manager.get_template_path(self.current_vehicle, next_view)

        if template_path:
            def on_finished(img, view):
                self.on_view_finished(img, view)

            self.start_generation_with_callback(template_path, self.current_prompt, next_view, on_finished)

    def start_generation_with_callback(self, template_path, prompt, view, callback):
        """Start generation with callback"""
        if self.is_generating:
            return

        self.is_generating = True
        self.progress.start(10)

        def generate():
            try:
                self.status_var.set(f"Generating {view} view...")
                template = self.processor.load_template(template_path)
                mask = self.processor.create_mask(template)
                template_resized, mask_resized = self.processor.prepare_for_api(template, mask)

                generated = self.api_client.generate_inpainting(
                    template_resized,
                    mask_resized,
                    prompt,
                    view
                )

                if generated:
                    if generated.size != template.size:
                        generated = generated.resize(template.size, Image.Resampling.LANCZOS)
                        mask = mask.resize(template.size, Image.Resampling.LANCZOS)
                    final = self.processor.composite_result(template, generated, mask)
                    self.root.after(0, lambda: callback(final, view))
                else:
                    self.root.after(0, lambda: callback(None, view))

            except Exception as e:
                import traceback
                error_details = f"{str(e)}\n\nDetails:\n{traceback.format_exc()}"
                self.root.after(0, lambda: self.on_error(error_details))

        thread = threading.Thread(target=generate, daemon=True)
        thread.start()

    def on_view_finished(self, image: Optional[Image.Image], view: str):
        """Handle individual view completion"""
        self.progress.stop()
        self.is_generating = False

        if image:
            self.generated_views[view] = image
            self.display_image(image)

            # Continue with next view
            if self.views_to_generate:
                self.root.after(100, self.generate_next_view)
            else:
                self.save_btn.config(state=tk.NORMAL)
                self.status_var.set("All views complete!")
                messagebox.showinfo("Complete", "All views generated successfully!")

    def save_livery(self):
        """Save all generated views"""
        if not self.generated_views:
            messagebox.showerror("Error", "No views to save!")
            return

        output_dir = Path(self.config["output_directory"]) / self.current_vehicle
        output_dir.mkdir(parents=True, exist_ok=True)

        for view, image in self.generated_views.items():
            output_path = output_dir / f"Livery_{view}.png"
            self.processor.save_image(image, output_path)

        messagebox.showinfo(
            "Success",
            f"Livery saved to: {output_dir}\n\n{len(self.generated_views)} views saved."
        )


def main():
    """Main entry point"""
    root = tk.Tk()
    app = LiveryGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

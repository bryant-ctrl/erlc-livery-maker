"""
Livery Generator Window - Main GUI for the application
"""
import sys
import json
from pathlib import Path
from typing import Optional, Dict, List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QTextEdit, QProgressBar, QMessageBox, QScrollArea,
    QCheckBox, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image
import io

from template_manager import TemplateManager
from image_processor import ImageProcessor
from api_client import ReplicateAPIClient


class GenerationWorker(QThread):
    """Worker thread for image generation"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(object)  # Emits generated image or None
    error = pyqtSignal(str)

    def __init__(self, api_client, processor, template_path, prompt, view):
        super().__init__()
        self.api_client = api_client
        self.processor = processor
        self.template_path = template_path
        self.prompt = prompt
        self.view = view

    def run(self):
        try:
            self.progress.emit(f"Loading template ({self.view})...")

            # Load template
            template = self.processor.load_template(self.template_path)

            self.progress.emit(f"Creating mask ({self.view})...")

            # Generate mask
            mask = self.processor.create_mask(template)

            self.progress.emit(f"Preparing images ({self.view})...")

            # Prepare for API (resize if needed)
            template_resized, mask_resized = self.processor.prepare_for_api(template, mask)

            self.progress.emit(f"Generating livery ({self.view})...")

            # Generate with API
            generated = self.api_client.generate_inpainting(
                template_resized,
                mask_resized,
                self.prompt,
                self.view
            )

            if generated is None:
                self.error.emit("Generation failed - check API key and connection")
                self.finished.emit(None)
                return

            self.progress.emit(f"Compositing result ({self.view})...")

            # Resize generated back to original size if needed
            if generated.size != template.size:
                generated = generated.resize(template.size, Image.Resampling.LANCZOS)
                mask = mask.resize(template.size, Image.Resampling.LANCZOS)

            # Composite result
            final = self.processor.composite_result(template, generated, mask)

            self.progress.emit(f"Complete ({self.view})!")
            self.finished.emit(final)

        except Exception as e:
            self.error.emit(f"Error: {str(e)}")
            self.finished.emit(None)


class LiveryGeneratorWindow(QMainWindow):
    """Main window for livery generation"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ER:LC Livery Maker")
        self.setMinimumSize(1000, 700)

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
        self.worker: Optional[GenerationWorker] = None

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
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # API Key section
        api_group = QGroupBox("API Configuration")
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("Replicate API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(self.config.get("replicate_api_key", ""))
        self.api_key_input.setPlaceholderText("Enter your Replicate API key")
        api_layout.addWidget(self.api_key_input)
        api_save_btn = QPushButton("Save API Key")
        api_save_btn.clicked.connect(self.save_api_key)
        api_layout.addWidget(api_save_btn)
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Vehicle selection
        vehicle_layout = QHBoxLayout()
        vehicle_layout.addWidget(QLabel("Select Vehicle:"))
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.addItems(self.template_manager.get_vehicle_names())
        self.vehicle_combo.currentTextChanged.connect(self.on_vehicle_changed)
        vehicle_layout.addWidget(self.vehicle_combo)
        layout.addLayout(vehicle_layout)

        # Prompt input
        prompt_layout = QVBoxLayout()
        prompt_layout.addWidget(QLabel("Livery Description:"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Example: police car with blue and white stripes, sheriff badge on doors")
        self.prompt_input.setMaximumHeight(80)
        prompt_layout.addWidget(self.prompt_input)
        layout.addLayout(prompt_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.preview_btn = QPushButton("Generate Preview (Left View)")
        self.preview_btn.clicked.connect(self.generate_preview)
        button_layout.addWidget(self.preview_btn)

        self.generate_all_btn = QPushButton("Generate All Views")
        self.generate_all_btn.clicked.connect(self.generate_all_views)
        self.generate_all_btn.setEnabled(False)
        button_layout.addWidget(self.generate_all_btn)

        self.save_btn = QPushButton("Save Livery")
        self.save_btn.clicked.connect(self.save_livery)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel("No preview yet")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("border: 1px solid #ccc;")

        scroll = QScrollArea()
        scroll.setWidget(self.preview_label)
        scroll.setWidgetResizable(True)
        preview_layout.addWidget(scroll)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Multi-vehicle section (initially hidden)
        self.multi_vehicle_group = QGroupBox("Apply to Other Vehicles")
        self.multi_vehicle_group.setVisible(False)
        multi_layout = QVBoxLayout()
        self.vehicle_checkboxes: Dict[str, QCheckBox] = {}
        self.checkbox_layout = QGridLayout()
        multi_layout.addLayout(self.checkbox_layout)
        apply_btn = QPushButton("Apply to Selected Vehicles")
        apply_btn.clicked.connect(self.apply_to_vehicles)
        multi_layout.addWidget(apply_btn)
        self.multi_vehicle_group.setLayout(multi_layout)
        layout.addWidget(self.multi_vehicle_group)

    def save_api_key(self):
        """Save API key to config"""
        api_key = self.api_key_input.text().strip()
        self.config["replicate_api_key"] = api_key
        self.save_config()
        self.api_client = ReplicateAPIClient(api_key)
        QMessageBox.information(self, "Success", "API key saved!")

    def on_vehicle_changed(self, vehicle_name: str):
        """Handle vehicle selection change"""
        self.current_vehicle = vehicle_name
        self.preview_image = None
        self.generated_views.clear()
        self.preview_label.setText(f"Selected: {vehicle_name}")
        self.generate_all_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

    def generate_preview(self):
        """Generate preview (Left view only)"""
        if not self.api_client or not self.config.get("replicate_api_key"):
            QMessageBox.warning(self, "Error", "Please set your Replicate API key first!")
            return

        if not self.current_vehicle:
            QMessageBox.warning(self, "Error", "Please select a vehicle!")
            return

        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Error", "Please enter a livery description!")
            return

        self.current_prompt = prompt

        # Get Left template
        template_path = self.template_manager.get_template_path(self.current_vehicle, "Left")
        if not template_path:
            QMessageBox.warning(self, "Error", "Left template not found!")
            return

        # Start generation
        self.start_generation(template_path, prompt, "Left", is_preview=True)

    def start_generation(self, template_path, prompt, view, is_preview=False):
        """Start image generation in worker thread"""
        self.preview_btn.setEnabled(False)
        self.generate_all_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # Indeterminate

        self.worker = GenerationWorker(
            self.api_client,
            self.processor,
            template_path,
            prompt,
            view
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(lambda img: self.on_generation_finished(img, view, is_preview))
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, message: str):
        """Update progress"""
        self.status_label.setText(message)

    def on_generation_finished(self, image: Optional[Image.Image], view: str, is_preview: bool):
        """Handle generation completion"""
        self.progress_bar.setVisible(False)
        self.preview_btn.setEnabled(True)

        if image is None:
            self.status_label.setText("Generation failed!")
            return

        # Store the result
        if is_preview:
            self.preview_image = image
            self.generate_all_btn.setEnabled(True)
            self.status_label.setText(f"Preview generated! Review and click 'Generate All Views' to continue.")
        else:
            self.generated_views[view] = image
            self.status_label.setText(f"Generated {view} view ({len(self.generated_views)}/5)")

        # Display the image
        self.display_image(image)

        # Check if all views are complete
        if len(self.generated_views) == 5:
            self.save_btn.setEnabled(True)
            self.show_multi_vehicle_options()
            QMessageBox.information(self, "Complete", "All views generated successfully!")

    def on_error(self, error_msg: str):
        """Handle generation error"""
        self.progress_bar.setVisible(False)
        self.preview_btn.setEnabled(True)
        self.status_label.setText(f"Error: {error_msg}")
        QMessageBox.critical(self, "Error", error_msg)

    def display_image(self, image: Image.Image):
        """Display image in preview area"""
        # Convert PIL Image to QPixmap
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        qimage = QImage()
        qimage.loadFromData(img_byte_arr)
        pixmap = QPixmap.fromImage(qimage)

        # Scale to fit preview area
        scaled_pixmap = pixmap.scaled(
            self.preview_label.width() - 20,
            self.preview_label.height() - 20,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.preview_label.setPixmap(scaled_pixmap)

    def generate_all_views(self):
        """Generate all 5 views sequentially"""
        if not self.preview_image:
            QMessageBox.warning(self, "Error", "Please generate a preview first!")
            return

        # Clear previous results
        self.generated_views.clear()
        self.save_btn.setEnabled(False)

        # Add the preview to results
        self.generated_views["Left"] = self.preview_image

        # Generate remaining views
        self.generate_next_view()

    def generate_next_view(self):
        """Generate the next view in sequence"""
        views = ["Front", "Rear", "Right", "Top"]
        remaining = [v for v in views if v not in self.generated_views]

        if not remaining:
            return

        next_view = remaining[0]
        template_path = self.template_manager.get_template_path(self.current_vehicle, next_view)

        if template_path:
            self.worker = GenerationWorker(
                self.api_client,
                self.processor,
                template_path,
                self.current_prompt,
                next_view
            )
            self.worker.progress.connect(self.on_progress)
            self.worker.finished.connect(lambda img: self.on_view_finished(img, next_view))
            self.worker.error.connect(self.on_error)
            self.worker.start()

    def on_view_finished(self, image: Optional[Image.Image], view: str):
        """Handle individual view completion"""
        if image:
            self.generated_views[view] = image
            self.display_image(image)

            # Continue with next view
            if len(self.generated_views) < 5:
                self.generate_next_view()
            else:
                self.save_btn.setEnabled(True)
                self.show_multi_vehicle_options()
                self.status_label.setText("All views complete!")
                QMessageBox.information(self, "Complete", "All views generated successfully!")

    def save_livery(self):
        """Save all generated views"""
        if not self.generated_views:
            QMessageBox.warning(self, "Error", "No views to save!")
            return

        output_dir = Path(self.config["output_directory"]) / self.current_vehicle
        output_dir.mkdir(parents=True, exist_ok=True)

        for view, image in self.generated_views.items():
            output_path = output_dir / f"Livery_{view}.png"
            self.processor.save_image(image, output_path)

        QMessageBox.information(
            self,
            "Success",
            f"Livery saved to: {output_dir}\n\n{len(self.generated_views)} views saved."
        )

    def show_multi_vehicle_options(self):
        """Show checkboxes for other vehicles"""
        # Clear existing checkboxes
        for checkbox in self.vehicle_checkboxes.values():
            checkbox.deleteLater()
        self.vehicle_checkboxes.clear()

        # Get other vehicles
        other_vehicles = [v for v in self.template_manager.get_vehicle_names()
                         if v != self.current_vehicle]

        # Create checkboxes
        row, col = 0, 0
        for vehicle in other_vehicles:
            checkbox = QCheckBox(vehicle)
            self.vehicle_checkboxes[vehicle] = checkbox
            self.checkbox_layout.addWidget(checkbox, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        self.multi_vehicle_group.setVisible(len(other_vehicles) > 0)

    def apply_to_vehicles(self):
        """Apply current livery to selected vehicles"""
        selected = [v for v, cb in self.vehicle_checkboxes.items() if cb.isChecked()]

        if not selected:
            QMessageBox.warning(self, "Error", "Please select at least one vehicle!")
            return

        QMessageBox.information(
            self,
            "Apply to Vehicles",
            f"This will generate the same livery for {len(selected)} vehicle(s).\n\n"
            "This may take several minutes."
        )

        # TODO: Implement batch generation for multiple vehicles
        # For now, just show a message
        self.status_label.setText(f"Batch generation for {len(selected)} vehicles - Coming soon!")

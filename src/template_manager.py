"""
Template Manager - Scans and manages vehicle template files
"""
import os
from pathlib import Path
from typing import Dict, List, Optional


class TemplateManager:
    """Manages vehicle template files and folders"""

    REQUIRED_VIEWS = ["Front", "Rear", "Left", "Right", "Top"]

    def __init__(self, templates_dir: str):
        self.templates_dir = Path(templates_dir)
        self.vehicles: Dict[str, Dict[str, Path]] = {}
        self.scan_templates()

    def scan_templates(self) -> None:
        """Scan templates directory for vehicle folders"""
        self.vehicles.clear()

        if not self.templates_dir.exists():
            print(f"Templates directory not found: {self.templates_dir}")
            return

        # Scan each subdirectory
        for vehicle_dir in self.templates_dir.iterdir():
            if not vehicle_dir.is_dir():
                continue

            # Look for template files
            templates = self._find_templates(vehicle_dir)

            # Only add if all 5 views are present
            if len(templates) == 5:
                self.vehicles[vehicle_dir.name] = templates
                print(f"Found vehicle: {vehicle_dir.name} with {len(templates)} views")
            else:
                print(f"Skipping {vehicle_dir.name}: only found {len(templates)}/5 views")

    def _find_templates(self, vehicle_dir: Path) -> Dict[str, Path]:
        """Find all template files for a vehicle"""
        templates = {}

        for view in self.REQUIRED_VIEWS:
            # Look for files matching pattern: *_<View>.png
            matches = list(vehicle_dir.glob(f"*_{view}.png"))

            if matches:
                templates[view] = matches[0]

        return templates

    def get_vehicle_names(self) -> List[str]:
        """Get list of all available vehicle names"""
        return sorted(self.vehicles.keys())

    def get_vehicle_templates(self, vehicle_name: str) -> Optional[Dict[str, Path]]:
        """Get template paths for a specific vehicle"""
        return self.vehicles.get(vehicle_name)

    def get_template_path(self, vehicle_name: str, view: str) -> Optional[Path]:
        """Get path to a specific template file"""
        templates = self.get_vehicle_templates(vehicle_name)
        if templates:
            return templates.get(view)
        return None


if __name__ == "__main__":
    # Test the template manager
    manager = TemplateManager("templates")
    print(f"\nFound {len(manager.vehicles)} vehicles:")
    for vehicle in manager.get_vehicle_names():
        print(f"  - {vehicle}")

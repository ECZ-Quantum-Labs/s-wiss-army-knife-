#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import logging
import sys
from pathlib import Path
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class ModuleRegistry:
    """Dynamic module loader for Swiss Army Knife blades."""
    
    def __init__(self, blades_dir_name: str = "blades"):
        self.src_dir = Path(__file__).resolve().parent.parent
        self.blades_path = self.src_dir / blades_dir_name
        self.loaded_modules: Dict[str, Any] = {}
        self.blades_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Registry initialized. Blades directory: {self.blades_path}")

    def discover_modules(self) -> list[str]:
        if not self.blades_path.exists():
            return []
        return [
            p.stem for p in self.blades_path.glob("*.py")
            if p.stem != "__init__"
        ]

    def load_module(self, module_name: str) -> Optional[object]:
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
        
        file_path = self.blades_path / f"{module_name}.py"
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            self.loaded_modules[module_name] = mod
            logger.info(f"Module loaded: {module_name}")
            return mod
        except Exception as e:
            logger.error(f"Failed to load {module_name}: {e}")
            return None



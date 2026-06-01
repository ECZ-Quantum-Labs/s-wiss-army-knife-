#!/usr/bin/env python3
"""
Module Registry V1/V2 - Dynamic Blade Loader
Loads, caches, and manages security modules from src/blades/
"""
from __future__ import annotations
import importlib
import logging
import sys
from pathlib import Path
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class ModuleRegistry:
    """Dynamic module loader for Swiss Army Knife blades."""
    
    def __init__(self, blades_dir: str = "src/blades"):
        self.blades_path = Path(blades_dir)
        self.loaded_modules: Dict[str, Any] = {}
        self.blades_path.mkdir(parents=True, exist_ok=True)
        
        # Ensure parent directory is in Python path
        root = Path(__file__).resolve().parent.parent.parent
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
            
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
        try:
            mod = importlib.import_module(f"src.blades.{module_name}")
            self.loaded_modules[module_name] = mod
            logger.info(f"Module loaded: {module_name}")
            return mod
        except Exception as e:
            logger.error(f"Failed to load {module_name}: {e}")
            return None

    def reload_all(self) -> int:
        self.loaded_modules.clear()
        count = 0
        for mod_name in self.discover_modules():
            if self.load_module(mod_name):
                count += 1
        logger.info(f"Reloaded {count} modules")
        return count


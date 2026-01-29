from __future__ import annotations

import importlib_resources

from tutor import exceptions, serialize
from tutor.types import Config

PRESETS_DIR = importlib_resources.files("tutor") / "templates" / "config" / "presets"

def load_preset(name: str) -> Config:
    """加载指定名称的预设配置。"""
    preset_path = PRESETS_DIR / f"{name}.yml"
    if not preset_path.exists():
        available = [p.name.replace(".yml", "") for p in PRESETS_DIR.iterdir() if p.name.endswith(".yml")]
        raise exceptions.TutorError(
            f"找不到预设配置 '{name}'。可用预设: {', '.join(available)}"
        )

    return serialize.load(preset_path.read_text(encoding="utf-8"))

def apply_preset(config: Config, name: str) -> None:
    """将预设配置应用到现有配置中。"""
    preset_config = load_preset(name)
    config.update(preset_config)

"""모든 puck_screen_holder 모델을 STEP으로 export."""

import importlib
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# show()를 no-op으로 만들어 import 시 viewer 호출 방지
import ocp_vscode
ocp_vscode.show = lambda *args, **kwargs: None

from build123d import export_step

MODULES = [
    "body", "handle", "handle_pin", "inner_shell", "inner_shell_cover",
    "inner_shell_cover_top", "pillar", "spring_pins",
]

export_dir = PROJECT_ROOT / "exports" / "puck_screen_holder"
export_dir.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for name in MODULES:
    full_name = f"models.coffee.puck_screen_holder.{name}"
    print(f"Building {name}...")
    module = importlib.import_module(full_name)
    result = getattr(module, "result")
    step_path = export_dir / f"{name}_{timestamp}.step"
    export_step(result, str(step_path))
    print(f"  -> {step_path}")

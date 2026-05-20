"""퍽 스크린 홀더 - 핸들 핀 (기둥 구멍에 끼우는 4x4 핀)."""

from datetime import datetime
from pathlib import Path

from build123d import (
    Align, Box, BuildPart, chamfer,
)
from ocp_vscode import Camera, show

INSERT_X = 4
INSERT_Y = 4
INSERT_H = 16
CHAMFER = 0.5

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    Box(INSERT_X, INSERT_Y, INSERT_H, align=ALIGN_BOTTOM)
    # 위/아래 면 모서리에 챔퍼
    chamfer(
        [e for e in part.edges()
         if abs(e.center().Z) < 0.01 or abs(e.center().Z - INSERT_H) < 0.01],
        length=CHAMFER,
    )

result = part.part

# STEP 내보내기
# export_dir = Path(__file__).resolve().parent.parent.parent.parent / "exports"
# export_dir.mkdir(exist_ok=True)
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# step_path = export_dir / f"puck_screen_holder_handle_pin_{timestamp}.step"
# export_step(result, str(step_path))
# print(f"Exported: {step_path}")

show(result, reset_camera=Camera.RESET)

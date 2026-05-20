"""퍽 스크린 홀더 - 스프링 핀 (반구형 머리 기둥)."""

from datetime import datetime
from pathlib import Path

from build123d import (
    Align, BuildPart, Cylinder, Locations, Sphere,
)
from ocp_vscode import Camera, show

PIN_D = 3
TOTAL_H = 8
CYL_H = TOTAL_H - PIN_D / 2  # 반구 반지름만큼 빼서 전체 높이가 TOTAL_H이 되도록
PIN_COUNT = 12
PIN_GAP = 2  # 핀 사이 edge 간격
PIN_PITCH = PIN_D + PIN_GAP  # 중심 간 간격

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

pin_xs = [(i - (PIN_COUNT - 1) / 2) * PIN_PITCH for i in range(PIN_COUNT)]
pin_locs_cyl = [(x, 0, 0) for x in pin_xs]
pin_locs_sphere = [(x, 0, CYL_H) for x in pin_xs]

with BuildPart() as part:
    with Locations(*pin_locs_cyl):
        Cylinder(PIN_D / 2, CYL_H, align=ALIGN_BOTTOM)
    with Locations(*pin_locs_sphere):
        Sphere(PIN_D / 2)

result = part.part

# STEP 내보내기
# export_dir = Path(__file__).resolve().parent.parent.parent.parent / "exports"
# export_dir.mkdir(exist_ok=True)
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# step_path = export_dir / f"puck_screen_holder_spring_pins_{timestamp}.step"
# export_step(result, str(step_path))
# print(f"Exported: {step_path}")

show(result, reset_camera=Camera.RESET)

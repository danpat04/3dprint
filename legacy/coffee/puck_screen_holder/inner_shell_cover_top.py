"""퍽 스크린 홀더 - 이너 쉘 커버 위 캡 (기둥 위에 얹는 원판)."""

from datetime import datetime
from pathlib import Path

from build123d import (
    Align, Box, BuildPart, Cylinder, Locations, Mode,
)
from ocp_vscode import Camera, show

DISC_D = 30
DISC_H = 3

# 기둥이 들어갈 구멍 (원형 - 가운데 사각형으로 파인 단면)
TIGHT_TOL = 0.1
PILLAR_D = 15   # inner_shell_cover의 PILLAR_D
HOLE_D = PILLAR_D + 2 * TIGHT_TOL  # 15.2 (round 부분, tight 끼움)
RECT_BASE = 7   # 가운데 사각 base (= slot base)
RECT_W = RECT_BASE + 2 * TIGHT_TOL  # 7.2 (pillar slot 7.4 안에 양쪽 0.1씩 여유)
HOLE_DEPTH = 2

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    Cylinder(DISC_D / 2, DISC_H, align=ALIGN_BOTTOM)
    # 윗면에서 깊이 HOLE_DEPTH 만큼 round 구멍
    with Locations((0, 0, DISC_H - HOLE_DEPTH)):
        Cylinder(HOLE_D / 2, HOLE_DEPTH,
                 align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 구멍 가운데에 사각 material (Y 방향 RECT_W, X 방향 hole 직경만큼)
    with Locations((0, 0, DISC_H - HOLE_DEPTH)):
        Box(HOLE_D, RECT_W, HOLE_DEPTH,
            align=ALIGN_BOTTOM, mode=Mode.ADD)

result = part.part

# STEP 내보내기
# export_dir = Path(__file__).resolve().parent.parent.parent.parent / "exports"
# export_dir.mkdir(exist_ok=True)
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# step_path = export_dir / f"puck_screen_holder_inner_shell_cover_top_{timestamp}.step"
# export_step(result, str(step_path))
# print(f"Exported: {step_path}")

show(result, reset_camera=Camera.RESET)

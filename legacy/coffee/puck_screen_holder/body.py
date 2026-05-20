"""퍽 스크린 홀더 - 본체."""

import math
from datetime import datetime
from pathlib import Path

from build123d import (
    Align, Box, BuildPart, BuildSketch, Circle, Cylinder, Locations, Mode,
    Plane, extrude,
)
from ocp_vscode import Camera, show

OUTER_D = 30
HEIGHT = 10
HOLE_D = 4.9
HOLE_DEPTH = 5.3
HOLE_COUNT = 8
HOLE_RADIUS = 10  # 중앙으로부터 구멍 중심까지 거리
RING_OD = 5
RING_DEPTH = 4
TIGHT_TOL = 0.1  # 빡빡한 공차 (양쪽 적용 → 치수당 +0.2)
CENTER_RECT_X_BASE = 10
CENTER_RECT_Y_BASE = 2.5
CENTER_RECT_DEPTH_BASE = 5
CENTER_RECT_X = CENTER_RECT_X_BASE + 2 * TIGHT_TOL  # 10.2
CENTER_RECT_Y = CENTER_RECT_Y_BASE + 2 * TIGHT_TOL  # 2.7
CENTER_RECT_DEPTH = CENTER_RECT_DEPTH_BASE + TIGHT_TOL  # 5.1 (한쪽 면에만 공차)
CENTER_SLOT_X_BASE = 7
CENTER_SLOT_Y_BASE = 2.5
CENTER_SLOT_X = CENTER_SLOT_X_BASE + 2 * TIGHT_TOL  # 7.2
CENTER_SLOT_Y = CENTER_SLOT_Y_BASE + 2 * TIGHT_TOL  # 2.7
TOP_RING_WIDTH = 1.2   # 외경에서 안쪽으로 깎이는 반경 폭 (30 → 27.6)
TOP_RING_DEPTH = 2.1

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

positions_xy = [
    (HOLE_RADIUS * math.cos(2 * math.pi * i / HOLE_COUNT),
     HOLE_RADIUS * math.sin(2 * math.pi * i / HOLE_COUNT))
    for i in range(HOLE_COUNT)
]
top_hole_locs = [(x, y, HEIGHT - HOLE_DEPTH) for x, y in positions_xy]
bottom_ring_locs = [(x, y, 0) for x, y in positions_xy]

with BuildPart() as part:
    Cylinder(OUTER_D / 2, HEIGHT, align=ALIGN_BOTTOM)
    # 위에서 8개 실린더 구멍 파내기
    with Locations(*top_hole_locs):
        Cylinder(HOLE_D / 2, HOLE_DEPTH, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 아래에서 4.5mm 지름 구멍 파내기
    with Locations(*bottom_ring_locs):
        Cylinder(RING_OD / 2, RING_DEPTH, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 위에서 가운데 사각 기둥 파내기
    with Locations((0, 0, HEIGHT - CENTER_RECT_DEPTH)):
        Box(CENTER_RECT_X, CENTER_RECT_Y, CENTER_RECT_DEPTH,
            align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 가운데 좁은 슬롯 관통 (바닥까지)
    Box(CENTER_SLOT_X, CENTER_SLOT_Y, HEIGHT,
        align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 위 외경 따라 사각 ring 모양으로 깎기 (외경 30 → 안쪽 28.6, 깊이 0.6)
    with BuildSketch(Plane.XY.offset(HEIGHT)) as top_ring_sketch:
        Circle(OUTER_D / 2)
        Circle(OUTER_D / 2 - TOP_RING_WIDTH, mode=Mode.SUBTRACT)
    extrude(amount=-TOP_RING_DEPTH, mode=Mode.SUBTRACT)

result = part.part

# STEP 내보내기
# export_dir = Path(__file__).resolve().parent.parent.parent.parent / "exports"
# export_dir.mkdir(exist_ok=True)
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# step_path = export_dir / f"puck_screen_holder_body_{timestamp}.step"
# export_step(result, str(step_path))
# print(f"Exported: {step_path}")

show(result, reset_camera=Camera.RESET)

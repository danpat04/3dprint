"""퍽 스크린 홀더 - 이너 쉘 커버."""

import math
from datetime import datetime
from pathlib import Path

from build123d import (
    Align, Box, BuildPart, Cylinder, Locations, Mode, chamfer,
)
from ocp_vscode import Camera, show

WALL_OUTER_D = 38.4  # inner_shell의 벽 외경 (wall thickness 4mm 기준)
EAVES = 6            # 처마 (양쪽으로 튀어나오는 폭)
OUTER_D = WALL_OUTER_D + 2 * EAVES  # 50.4
HEIGHT = 3

# bolt hole — inner_shell 벽 위 4구멍과 같은 위치에 정렬
BOLT_HOLE_D = 2.2
BOLT_HOLE_R = 17.2  # inner_shell의 TOP_HOLE_R와 동일

# body 아래 ring 위치와 같은 8개 구멍
RING_HOLE_D = 3
RING_HOLE_R = 10  # body의 HOLE_RADIUS와 동일
RING_HOLE_COUNT = 8

# 처마 정중앙 ring 구멍 4개 (상하좌우)
OUTER_RING_HOLE_D = 3
OUTER_RING_HOLE_R = (WALL_OUTER_D / 2 + OUTER_D / 2) / 2  # 처마 정중앙 (22.2)

# 정중앙 기둥
PILLAR_D = 15
PILLAR_H = 35  # 바닥(Z=0)부터의 전체 높이

# 기둥 위쪽에 handle 작동 범위 사각 슬롯
LOOSE_TOL = 0.2
SLOT_BASE = 7
SLOT_SIZE = SLOT_BASE + 2 * LOOSE_TOL  # 7.4
SLOT_DEPTH = 20

# 기둥 윗부분 챔퍼 (옆 0.5, 위 0.3 → 옆이 더 가파른 슬로프)
PILLAR_CHAMFER_SIDE = 0.5
PILLAR_CHAMFER_TOP = 0.3

# pillar.py 관통용 7x2.5 사각 구멍 (loose tol)
PASS_HOLE_X = 7 + 2 * LOOSE_TOL    # 7.4
PASS_HOLE_Y = 2.5 + 2 * LOOSE_TOL  # 2.9


ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

bolt_hole_locs = [
    (BOLT_HOLE_R * math.cos(a), BOLT_HOLE_R * math.sin(a), 0)
    for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2)
]
ring_hole_locs = [
    (RING_HOLE_R * math.cos(2 * math.pi * i / RING_HOLE_COUNT),
     RING_HOLE_R * math.sin(2 * math.pi * i / RING_HOLE_COUNT),
     0)
    for i in range(RING_HOLE_COUNT)
]
outer_ring_hole_locs = [
    (OUTER_RING_HOLE_R * math.cos(a), OUTER_RING_HOLE_R * math.sin(a), 0)
    for a in (math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4)
]

with BuildPart() as part:
    Cylinder(OUTER_D / 2, HEIGHT, align=ALIGN_BOTTOM)
    with Locations(*bolt_hole_locs):
        Cylinder(BOLT_HOLE_D / 2, HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    with Locations(*ring_hole_locs):
        Cylinder(RING_HOLE_D / 2, HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    with Locations(*outer_ring_hole_locs):
        Cylinder(OUTER_RING_HOLE_D / 2, HEIGHT,
                 align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 정중앙 기둥 (바닥부터 PILLAR_H 높이)
    Cylinder(PILLAR_D / 2, PILLAR_H, align=ALIGN_BOTTOM)
    # 기둥 위에서 슬롯 파기 (상하 Y는 7.4, 좌우 X는 관통 → 양쪽에 얇은 기둥)
    with Locations((0, 0, PILLAR_H - SLOT_DEPTH)):
        Box(PILLAR_D + 10, SLOT_SIZE, SLOT_DEPTH,
            align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # pillar.py 관통용 2.9 x 7.4 수직 사각 구멍 (전체 Z 관통, slot과 같은 방향)
    Box(PASS_HOLE_Y, PASS_HOLE_X, PILLAR_H + 2,
        align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 기둥 위 모서리 비대칭 챔퍼 (옆 0.5, 위 0.3)
    chamfer(
        [e for e in part.edges() if abs(e.center().Z - PILLAR_H) < 0.01],
        length=PILLAR_CHAMFER_SIDE, length2=PILLAR_CHAMFER_TOP,
    )

result = part.part

# STEP 내보내기
# export_dir = Path(__file__).resolve().parent.parent.parent.parent / "exports"
# export_dir.mkdir(exist_ok=True)
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# step_path = export_dir / f"puck_screen_holder_inner_shell_cover_{timestamp}.step"
# export_step(result, str(step_path))
# print(f"Exported: {step_path}")

show(result, reset_camera=Camera.RESET)

"""퍽 스크린 홀더 - 이너 쉘 (body를 감싸는 디스크)."""

import math
from datetime import datetime
from pathlib import Path

from build123d import (
    Align, BuildPart, Cylinder, Locations, Mode,
)
from ocp_vscode import Camera, show

OUTER_D = 58.3
HEIGHT = 3
INNER_D_BASE = 30  # body 외경과 동일
LOOSE_TOL = 0.2    # 느슨한 공차 (양쪽 적용)
INNER_D = INNER_D_BASE + 2 * LOOSE_TOL  # 30.4
WALL_THICKNESS = 4
WALL_H = 20
WALL_OUTER_D = INNER_D + 2 * WALL_THICKNESS  # 34.4

# body의 TOP_RING 단차 매칭 — body 깎인 부분이 끼워지는 좁은 ID 영역
BODY_RING_OD_BASE = 27.6  # body OUTER_D(30) - 2 * TOP_RING_WIDTH(1.2)
BODY_RING_DEPTH = 2.1     # body TOP_RING_DEPTH와 일치
INNER_D_NARROW = BODY_RING_OD_BASE + 2 * LOOSE_TOL  # 28.0

# 벽 위쪽 상하좌우 4구멍
TOP_HOLE_D = 2.8
TOP_HOLE_DEPTH = 3.6
TOP_HOLE_R = (INNER_D + WALL_OUTER_D) / 4  # 벽 두께 정 중앙 (17.2)

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    # 외형: 디스크 + 그 위 원통 벽
    Cylinder(OUTER_D / 2, HEIGHT, align=ALIGN_BOTTOM)
    with Locations((0, 0, HEIGHT)):
        Cylinder(WALL_OUTER_D / 2, WALL_H, align=ALIGN_BOTTOM)
    # 안쪽 단차형 구멍: 아래 좁은 ID(body 깎인 부분), 위 넓은 ID(body 본체)
    Cylinder(INNER_D_NARROW / 2, BODY_RING_DEPTH,
             align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    with Locations((0, 0, BODY_RING_DEPTH)):
        Cylinder(INNER_D / 2, HEIGHT + WALL_H - BODY_RING_DEPTH,
                 align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 벽 위쪽 상하좌우 4구멍 (Z축으로 깊이 TOP_HOLE_DEPTH)
    top_z = HEIGHT + WALL_H
    top_hole_locs = [
        (TOP_HOLE_R * math.cos(a), TOP_HOLE_R * math.sin(a), top_z - TOP_HOLE_DEPTH)
        for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2)
    ]
    with Locations(*top_hole_locs):
        Cylinder(TOP_HOLE_D / 2, TOP_HOLE_DEPTH,
                 align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

result = part.part

# STEP 내보내기
# export_dir = Path(__file__).resolve().parent.parent.parent.parent / "exports"
# export_dir.mkdir(exist_ok=True)
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# step_path = export_dir / f"puck_screen_holder_inner_shell_{timestamp}.step"
# export_step(result, str(step_path))
# print(f"Exported: {step_path}")

show(result, reset_camera=Camera.RESET)

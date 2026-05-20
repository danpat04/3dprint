"""버블 팁 — bubble_head 위에 6개 들어가는 실린더 단품."""

import math
from datetime import datetime
from pathlib import Path

from build123d import (
    Align, Box, BuildLine, BuildPart, BuildSketch, CenterArc, Cylinder, Line,
    Location, Locations, Mode, Plane, export_step, extrude, make_face,
)
from ocp_vscode import Camera, show

# 치수 (mm)
POST_OUTER_D = 20   # 외경
POST_WALL = 1.5     # 두께
POST_H = 8          # 높이
HOLE_H = 5          # 부채꼴 구멍 높이
HOLE_ANGLE_SPAN = 90  # 부채꼴 각도 폭
HOLE_RADIUS = POST_OUTER_D  # 부채꼴 반지름
PLATE_THICK = 0.5   # 돌기 판 두께 (접선 방향)
PLATE_DEPTH = 3     # 돌기 판 돌출 길이 (cavity 안쪽)
PLATE_H = 3         # 돌기 판 높이
PLATE_COUNT = 15    # 돌기 개수
TOLERANCE = 0.05    # 다리 공차
TAB_L = 7 - TOLERANCE    # 다리 길이 (slot의 7mm - 공차)
TAB_T = 1.5 - TOLERANCE  # 다리 두께 (slot의 1.5mm - 공차)
TAB_H = 3           # 다리 높이 (disc 관통 — DISC_H와 동일)
TAB_INNER_GAP = 17  # 두 다리의 안쪽 edge 사이 거리 (bubble_head SLOT_INNER_GAP과 일치)
TAB_OFFSET = (TAB_INNER_GAP + 1.5) / 2  # tip 중심 → 다리 중심 (슬롯 중심과 일치)

POST_OUTER_R = POST_OUTER_D / 2
POST_INNER_R = POST_OUTER_R - POST_WALL

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    Cylinder(POST_OUTER_R, POST_H, align=ALIGN_BOTTOM)
    Cylinder(POST_INNER_R, POST_H, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

# 바깥쪽(+X 방향)으로 부채꼴 구멍 (바닥 기준 0~HOLE_H)
start_angle = -HOLE_ANGLE_SPAN / 2
a0 = math.radians(start_angle)
a1 = math.radians(start_angle + HOLE_ANGLE_SPAN)
with BuildPart() as hp:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine():
            CenterArc((0, 0), HOLE_RADIUS, start_angle, HOLE_ANGLE_SPAN)
            Line(
                (HOLE_RADIUS * math.cos(a1), HOLE_RADIUS * math.sin(a1)),
                (0, 0),
            )
            Line(
                (0, 0),
                (HOLE_RADIUS * math.cos(a0), HOLE_RADIUS * math.sin(a0)),
            )
        make_face()
    extrude(amount=HOLE_H)
result = part.part - hp.part

# 내벽 상단에 돌기 판 PLATE_COUNT개
plate_center_r = POST_INNER_R - PLATE_DEPTH / 2
with BuildPart() as plates:
    for j in range(PLATE_COUNT):
        phi = 2 * math.pi * j / PLATE_COUNT
        cx = plate_center_r * math.cos(phi)
        cy = plate_center_r * math.sin(phi)
        cz = POST_H - PLATE_H / 2
        loc = Location((cx, cy, cz), (0, 0, math.degrees(phi)))
        with Locations(loc):
            Box(
                PLATE_DEPTH, PLATE_THICK, PLATE_H,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )
result = result.fuse(plates.part)

# 다리 2개 — tip 바닥(z=0)에서 아래쪽으로 TAB_H만큼 내려감
# bubble_head의 슬롯은 접선 방향(±Y at ±TAB_OFFSET)에 놓여 있고
# 슬롯의 7mm(긴축)는 조립 시 반경 = tip의 local X, 1.5mm(얇은축)는 tip의 local Y와 정렬
with BuildPart() as tabs:
    for sign in (-1, +1):
        with Locations((0, sign * TAB_OFFSET, -TAB_H / 2)):
            Box(
                TAB_L, TAB_T, TAB_H,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )
result = result.fuse(tabs.part)

# STEP 내보내기
export_dir = Path(__file__).resolve().parent.parent.parent / "exports"
export_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
step_path = export_dir / f"bubble_tip_{timestamp}.step"
export_step(result, str(step_path))
print(f"Exported: {step_path}")

show(result, reset_camera=Camera.RESET)

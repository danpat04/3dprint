"""버블 헤드."""


import math

from build123d import (
    Align, Box, BuildPart, BuildSketch, Circle, Cylinder, Location, Locations, Mode,
    Plane, loft,
)

# 치수 (mm)
OUTER_D = 79.82     # 실린더 외경
WALL = 3            # 실린더 두께
HEIGHT = 9.5        # 실린더 높이
DISC_D = 86         # 원판 아래쪽 지름
DISC_TOP_D = 90     # 원판 위쪽 지름 (아래보다 커서 위 edge가 뾰족)
DISC_H = 3          # 원판 두께
POST_COUNT = 6      # tip 개수
POST_RADIUS = 24    # 중심 → tip 중심 거리
SLOT_W = 7          # 슬롯 폭 (긴 축)
SLOT_T = 1.5        # 슬롯 두께 (얇은 축)
SLOT_INNER_GAP = 17 # 한 tip에서 슬롯 2개의 안쪽 edge 사이 거리
SLOT_SPACING = SLOT_INNER_GAP + SLOT_T  # 중심 간 거리 (= 18.5mm)
DISC_HOLE_D = 3     # tip 중앙 관통 구멍 지름

OUTER_R = OUTER_D / 2
INNER_R = OUTER_R - WALL
DISC_R = DISC_D / 2
DISC_TOP_R = DISC_TOP_D / 2

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    Cylinder(OUTER_R, HEIGHT, align=ALIGN_BOTTOM)
    Cylinder(INNER_R, HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 원판 (실린더 위에) — 아래는 DISC_R, 위는 DISC_TOP_R로 테이퍼
    with BuildSketch(Plane.XY.offset(HEIGHT)) as disc_bottom:
        Circle(DISC_R)
    with BuildSketch(Plane.XY.offset(HEIGHT + DISC_H)) as disc_top:
        Circle(DISC_TOP_R)
    loft([disc_bottom.sketch, disc_top.sketch])

    # 각 tip 위치마다 슬롯 2개 관통 (접선 방향으로 20mm 간격 — 부채꼴 구멍 피함)
    slot_locs = []
    for i in range(POST_COUNT):
        theta = 2 * math.pi * i / POST_COUNT
        theta_deg = math.degrees(theta)
        tip_cx = POST_RADIUS * math.cos(theta)
        tip_cy = POST_RADIUS * math.sin(theta)
        # 접선 단위벡터
        tx = -math.sin(theta)
        ty = math.cos(theta)
        for offset in (-SLOT_SPACING / 2, SLOT_SPACING / 2):
            cx = tip_cx + offset * tx
            cy = tip_cy + offset * ty
            cz = HEIGHT + DISC_H / 2
            slot_locs.append(Location((cx, cy, cz), (0, 0, theta_deg + 90)))
    with Locations(*slot_locs):
        Box(SLOT_T, SLOT_W, DISC_H + 2,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
            mode=Mode.SUBTRACT)

    # 각 tip 중앙 관통 구멍
    center_hole_locs = [
        (POST_RADIUS * math.cos(2 * math.pi * i / POST_COUNT),
         POST_RADIUS * math.sin(2 * math.pi * i / POST_COUNT),
         HEIGHT)
        for i in range(POST_COUNT)
    ]
    with Locations(*center_hole_locs):
        Cylinder(DISC_HOLE_D / 2, DISC_H, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

result = part.part

from models._lib.iter import finalize_iteration
finalize_iteration(part.part)

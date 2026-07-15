"""버블 튜브 — 나팔 형태 (아래 끝 직선 실린더)."""


from build123d import (
    Align, BuildPart, BuildSketch, Circle, Cylinder, Mode, Plane, loft,
)

# 치수 (mm)
BOTTOM_INNER_D = 80   # 나가는 쪽 (아래) 내경
WAIST_INNER_D = 25    # 중간 허리 내경
TOP_INNER_D = 40      # 입 쪽 (위) 내경
STRAIGHT_H = 10       # 아래 직선 실린더 높이
WAIST_Z = 100         # 허리 위치 (아래에서부터)
WALL = 3              # 벽 두께
HEIGHT = 200          # 전체 길이

BOTTOM_INNER_R = BOTTOM_INNER_D / 2
BOTTOM_OUTER_R = BOTTOM_INNER_R + WALL
WAIST_INNER_R = WAIST_INNER_D / 2
TOP_INNER_R = TOP_INNER_D / 2

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    # 아래 직선 실린더 (z = 0 ~ STRAIGHT_H)
    Cylinder(BOTTOM_OUTER_R, STRAIGHT_H, align=ALIGN_BOTTOM)

    # 곡선부 외부 (z = STRAIGHT_H ~ HEIGHT)
    with BuildSketch(Plane.XY.offset(STRAIGHT_H)) as outer_bottom:
        Circle(BOTTOM_OUTER_R)
    with BuildSketch(Plane.XY.offset(WAIST_Z)) as outer_waist:
        Circle(WAIST_INNER_R + WALL)
    with BuildSketch(Plane.XY.offset(HEIGHT)) as outer_top:
        Circle(TOP_INNER_R + WALL)
    loft([outer_bottom.sketch, outer_waist.sketch, outer_top.sketch])

    # 내부 파냄 — 직선 구간
    Cylinder(BOTTOM_INNER_R, STRAIGHT_H, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

    # 내부 파냄 — 곡선 구간
    with BuildSketch(Plane.XY.offset(STRAIGHT_H)) as inner_bottom:
        Circle(BOTTOM_INNER_R)
    with BuildSketch(Plane.XY.offset(WAIST_Z)) as inner_waist:
        Circle(WAIST_INNER_R)
    with BuildSketch(Plane.XY.offset(HEIGHT)) as inner_top:
        Circle(TOP_INNER_R)
    loft(
        [inner_bottom.sketch, inner_waist.sketch, inner_top.sketch],
        mode=Mode.SUBTRACT,
    )

from models._lib.iter import finalize_iteration
finalize_iteration(part.part)

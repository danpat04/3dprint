"""distributor_stand — 커피 디스트리뷰터 거치대.

디스트리뷰터를 올려두는 스탠드. 상단의 물결 산(삼각 골짜기 10개) 위에
디스트리뷰터를 얹고 돌리면, 디스트리뷰터에 묻은 커피 가루가 산에 긁혀 떨어진다.
(legacy/coffee/distributer.py 이관 + 파라미터 정리, 오타 교정)
"""

import math

from build123d import (
    Align,
    BuildLine,
    BuildPart,
    BuildSketch,
    CenterArc,
    Cylinder,
    Line,
    Mode,
    Plane,
    loft,
    make_face,
)

from models._lib.iter import finalize_iteration

# ---- 내부 실린더 (물결 산이 있는 안쪽 링) ----
INNER_D = 59.5     # 내경
INNER_WALL = 6.0   # 벽 두께
HEIGHT = 15.0      # 높이 (내부/중간 공통)

# ---- 물결 산 (디스트리뷰터 가루를 긁어내는 삼각 골짜기) ----
N_VALLEYS = 10     # 골짜기 개수
VALLEY_DEPTH = 3.0 # 골짜기 깊이

# ---- 중간 실린더 (내부와 한 몸) ----
MID_D = 71.5       # 내경
MID_WALL = 2.0     # 벽 두께

# ---- 외부 실린더 (감싸는 벽) ----
OUTER_D = 75.5     # 내경
OUTER_WALL = 2.0   # 벽 두께
OUTER_HEIGHT = 20.0  # 높이 (내부보다 높게 감쌈)

# ---- 계산값 ----
INNER_R = INNER_D / 2
INNER_OUTER_R = INNER_R + INNER_WALL
MID_OUTER_R = MID_D / 2 + MID_WALL
OUTER_INNER_R = OUTER_D / 2
OUTER_OUTER_R = OUTER_INNER_R + OUTER_WALL
VALLEY_ANGLE = 360 / N_VALLEYS
ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def annular_sector_sketch(plane, inner_r, outer_r, start_angle, angle_span):
    """내경~외경 사이의 부채꼴 스케치."""
    a0 = math.radians(start_angle)
    a1 = math.radians(start_angle + angle_span)
    with BuildSketch(plane) as sk:
        with BuildLine():
            CenterArc((0, 0), inner_r, start_angle, angle_span)
            Line((inner_r * math.cos(a1), inner_r * math.sin(a1)),
                 (outer_r * math.cos(a1), outer_r * math.sin(a1)))
            CenterArc((0, 0), outer_r, start_angle + angle_span, -angle_span)
            Line((outer_r * math.cos(a0), outer_r * math.sin(a0)),
                 (inner_r * math.cos(a0), inner_r * math.sin(a0)))
        make_face()
    return sk


with BuildPart() as part:
    # 외부 실린더 (감싸는 벽)
    Cylinder(OUTER_OUTER_R, OUTER_HEIGHT, align=ALIGN_BOTTOM)
    Cylinder(OUTER_INNER_R, OUTER_HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 내부 + 중간 실린더 (한 몸체)
    Cylinder(MID_OUTER_R, HEIGHT, align=ALIGN_BOTTOM)
    Cylinder(INNER_R, HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

    # 역삼각형 골짜기 10개 (상단 물결 산)
    for i in range(N_VALLEYS):
        valley_angle = i * VALLEY_ANGLE
        base_start = valley_angle - VALLEY_ANGLE / 2
        # 꼭대기: 36° 부채꼴 (상단, 내경~외경 전체)
        top = annular_sector_sketch(
            Plane.XY.offset(HEIGHT), INNER_R, INNER_OUTER_R, base_start, VALLEY_ANGLE)
        # 바닥: 1° 얇은 부채꼴 (내경 쪽, 골짜기 바닥)
        bottom = annular_sector_sketch(
            Plane.XY.offset(HEIGHT - VALLEY_DEPTH), INNER_R, INNER_R + 0.1, valley_angle - 0.5, 1.0)
        loft([top.sketch, bottom.sketch], ruled=True, mode=Mode.SUBTRACT)

finalize_iteration(part.part)

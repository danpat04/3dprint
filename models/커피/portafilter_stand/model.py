"""portafilter_stand — 포터필터 거치대 (디스트리뷰팅/탬핑 겸용).

포터필터를 끼워 넣고 디스트리뷰션·탬핑을 하는 받침대.
  - 내부 실린더: 포터필터(바스켓)를 수용, 노치로 정렬
  - 외부 껍질: 감싸는 보호/거치
  - X자 결속 기둥: 내부-외부 실린더 연결

(legacy/coffee/tamping_base_v5.py 이관 + 파라미터 정리)
"""

import math

from build123d import (
    Align,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    CenterArc,
    Cylinder,
    Line,
    Locations,
    Mode,
    Plane,
    extrude,
    make_face,
)

from models._lib.iter import finalize_iteration

# ============================================================
# 파라미터 (mm)
# ============================================================

# ---- 내부 실린더 (포터필터 수용) ----
INNER_D = 70.2         # 내경 (포터필터 바스켓 외경)
WALL = 5.0             # 벽 두께
HEIGHT = 80.0          # 높이

# ---- 외부 껍질 실린더 ----
# 내부보다 높게(90 > 80) 세워, 디스트리뷰팅 시 커피가루가 밖으로 튀는 것을 1차 차단.
SHELL_OUTER_D = 100.0  # 외경
SHELL_WALL = 2.0       # 벽 두께
SHELL_H = 90.0         # 높이 (내부 HEIGHT 보다 높음 → 가루 튐 방지)
ARC_INSET = 3.0        # 외부 노치 반원 파냄을 껍질 내벽에서 안쪽으로 시작하는 관통 여유

# ---- 아래(정남) 노치: 포터필터 스파우트 자리 ----
# 포터필터의 기울어진 부분에 맞춰 내경/외경 깊이가 다른 사선 바닥.
NOTCH_S_GAP = 21.29        # 노치 폭 (직선 간격)
NOTCH_S_DEPTH = 28.5       # 내경 쪽 깊이 (얕음)
NOTCH_S_OUTER_DEPTH = 37.5 # 외경 쪽 깊이 (깊음) → 둘 사이가 사선
SHELL_NOTCH_S_DEPTH = 35.5 # 외부 껍질 쪽 노치 깊이

# ---- 좌우(정동/정서) 노치: 포터필터 귀 자리 ----
NOTCH_LR_GAP = 27.6    # 노치 폭
NOTCH_LR_DEPTH = 6.0   # 깊이

# ---- 기타 ----
CHAMFER = 1.5          # 노치 상단 모서리 45° 챔퍼
STRUT_BASE = 5.0       # X자 결속 기둥 정삼각형 밑변

# ---- 계산값 ----
INNER_R = INNER_D / 2
OUTER_R = INNER_R + WALL
SHELL_OUTER_R = SHELL_OUTER_D / 2
SHELL_INNER_R = SHELL_OUTER_R - SHELL_WALL
ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


with BuildPart() as part:
    # 외부 껍질 실린더
    Cylinder(SHELL_OUTER_R, SHELL_H, align=ALIGN_BOTTOM)
    Cylinder(SHELL_INNER_R, SHELL_H, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 내부 실린더
    Cylinder(OUTER_R, HEIGHT, align=ALIGN_BOTTOM)
    Cylinder(INNER_R, HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

    # 외부 껍질 아래(정남) 노치
    with Locations((0, 0, SHELL_H - SHELL_NOTCH_S_DEPTH)):
        Box(NOTCH_S_GAP, SHELL_OUTER_R + 1, SHELL_NOTCH_S_DEPTH,
            align=(Align.CENTER, Align.MAX, Align.MIN), mode=Mode.SUBTRACT)
    # 외부 노치 바닥 반원형 파냄
    shell_notch_bottom_z = SHELL_H - SHELL_NOTCH_S_DEPTH
    semi_r = NOTCH_S_GAP / 2
    with BuildSketch(Plane.XZ.offset(SHELL_INNER_R - ARC_INSET)):
        with BuildLine():
            Line((-semi_r, shell_notch_bottom_z), (semi_r, shell_notch_bottom_z))
            CenterArc((0, shell_notch_bottom_z), semi_r, 0, -180)
        make_face()
    extrude(amount=SHELL_WALL + 5, mode=Mode.SUBTRACT)
    # 외부 노치 상단 모서리 45° 챔퍼
    half_gap_shell = NOTCH_S_GAP / 2
    for sign in (-1, 1):
        edge = sign * half_gap_shell
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Line((edge, SHELL_H), (edge + sign * CHAMFER, SHELL_H))
                Line((edge + sign * CHAMFER, SHELL_H), (edge, SHELL_H - CHAMFER))
                Line((edge, SHELL_H - CHAMFER), (edge, SHELL_H))
            make_face()
        extrude(amount=SHELL_OUTER_R + 1, mode=Mode.SUBTRACT)

    # 내부 실린더 아래(정남) 노치 — 내경/외경 깊이가 다른 사선 바닥
    notch_inner_z = HEIGHT - NOTCH_S_DEPTH        # 내경 쪽 바닥 z
    notch_outer_z = HEIGHT - NOTCH_S_OUTER_DEPTH  # 외경 쪽 바닥 z
    with BuildSketch(Plane.YZ):
        with BuildLine():
            Line((0, HEIGHT), (-(OUTER_R + 1), HEIGHT))
            Line((-(OUTER_R + 1), HEIGHT), (-(OUTER_R + 1), notch_outer_z))
            Line((-(OUTER_R + 1), notch_outer_z), (-OUTER_R, notch_outer_z))
            Line((-OUTER_R, notch_outer_z), (-INNER_R, notch_inner_z))  # 사선
            Line((-INNER_R, notch_inner_z), (0, notch_inner_z))
            Line((0, notch_inner_z), (0, HEIGHT))
        make_face()
    extrude(amount=NOTCH_S_GAP / 2, both=True, mode=Mode.SUBTRACT)

    # 아래 노치 상단 모서리 45° 챔퍼 (좌/우)
    half_gap_s = NOTCH_S_GAP / 2
    for sign in (-1, 1):
        edge = sign * half_gap_s
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Line((edge, HEIGHT), (edge + sign * CHAMFER, HEIGHT))
                Line((edge + sign * CHAMFER, HEIGHT), (edge, HEIGHT - CHAMFER))
                Line((edge, HEIGHT - CHAMFER), (edge, HEIGHT))
            make_face()
        extrude(amount=OUTER_R + 1, mode=Mode.SUBTRACT)

    # B 영역 보강: 노치 부분 내경 안쪽 초승달 영역 채움
    half_gap = NOTCH_S_GAP / 2
    y_int = -math.sqrt(INNER_R**2 - half_gap**2)  # 절단면과 내경 원 교점 y
    angle_right = math.degrees(math.atan2(y_int, half_gap)) % 360
    angle_left = math.degrees(math.atan2(y_int, -half_gap)) % 360
    arc_span = angle_left - angle_right
    with BuildSketch(Plane.XY):
        with BuildLine():
            CenterArc((0, 0), INNER_R, angle_right, arc_span)
            Line((-half_gap, y_int), (half_gap, y_int))
        make_face()
    extrude(amount=notch_inner_z)

    # X자 결속 기둥 (내부-외부 실린더 연결, 정삼각형 단면)
    strut_length = SHELL_INNER_R - OUTER_R
    tri_h = STRUT_BASE * math.sqrt(3) / 2
    for angle in (45, 135, 225, 315):
        rad = math.radians(angle)
        origin = (OUTER_R * math.cos(rad), OUTER_R * math.sin(rad), 0)
        plane = Plane(origin=origin, z_dir=(math.cos(rad), math.sin(rad), 0), x_dir=(0, 0, 1))
        with BuildSketch(plane):
            with BuildLine():
                Line((0, -STRUT_BASE / 2), (0, STRUT_BASE / 2))
                Line((0, STRUT_BASE / 2), (tri_h, 0))
                Line((tri_h, 0), (0, -STRUT_BASE / 2))
            make_face()
        extrude(amount=strut_length)

    # 좌우(정동/정서) 노치
    with Locations((0, 0, HEIGHT - NOTCH_LR_DEPTH)):
        Box(OUTER_R + 1, NOTCH_LR_GAP, NOTCH_LR_DEPTH,
            align=(Align.MIN, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        Box(OUTER_R + 1, NOTCH_LR_GAP, NOTCH_LR_DEPTH,
            align=(Align.MAX, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    # 좌우 노치 상단 모서리 45° 챔퍼 (앞/뒤)
    half_gap_lr = NOTCH_LR_GAP / 2
    for sign in (-1, 1):
        edge = sign * half_gap_lr
        with BuildSketch(Plane.YZ):
            with BuildLine():
                Line((edge, HEIGHT), (edge + sign * CHAMFER, HEIGHT))
                Line((edge + sign * CHAMFER, HEIGHT), (edge, HEIGHT - CHAMFER))
                Line((edge, HEIGHT - CHAMFER), (edge, HEIGHT))
            make_face()
        extrude(amount=OUTER_R + 1, both=True, mode=Mode.SUBTRACT)


finalize_iteration(part.part)

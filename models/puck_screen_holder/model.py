"""puck_screen_holder — 단일 파일 통합.

레거시 models/coffee/puck_screen_holder/ 의 11개 부품을 한 파일에 함수로 통합.
각 부품 build 함수가 part 를 반환. assembly 에서 Pos 로 그리드 layout 후 finalize_iteration.
"""

import math

from build123d import (
    Align, Box, BuildLine, BuildPart, BuildSketch, Circle, Cone, Cylinder, Line,
    Location, Locations, Mode, Plane, Pos, Sphere, Spline, chamfer, extrude,
    make_face,
)

from models._lib.iter import finalize_iteration


ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


# ============================================================
# body — Ø30 × 10 본체 (뒤집힌 자세 + 아래 cone 자기정렬)
#   아래 (z=0): 자석 hole + center rect (puck-facing)
#   위 (z=10): ring hole (cover 핀이 끼움)
#   외경: 아래 cone (Ø27.6→Ø30, z=0..2.1) + 위 cylinder (Ø30, z=2.1..10)
# ============================================================
def build_body():
    OUTER_D = 30
    HEIGHT = 10
    HOLE_D = 4.9
    HOLE_DEPTH = 5.3
    HOLE_COUNT = 8
    HOLE_RADIUS = 10
    RING_OD = 5
    RING_DEPTH = 4
    TIGHT_TOL = 0.1
    CENTER_RECT_X = 10 + 2 * TIGHT_TOL
    CENTER_RECT_Y = 2.5 + 2 * TIGHT_TOL
    CENTER_RECT_DEPTH = 5 + TIGHT_TOL
    CENTER_SLOT_X = 7 + 2 * TIGHT_TOL
    CENTER_SLOT_Y = 2.5 + 2 * TIGHT_TOL
    # Cone 자기정렬 (이전 위 ring 깎임 → 이제 아래 cone)
    CONE_WIDTH = 1.2
    CONE_DEPTH = 2.1
    CONE_BOTTOM_OD = OUTER_D - 2 * CONE_WIDTH  # 27.6

    positions = [
        (HOLE_RADIUS * math.cos(2 * math.pi * i / HOLE_COUNT),
         HOLE_RADIUS * math.sin(2 * math.pi * i / HOLE_COUNT))
        for i in range(HOLE_COUNT)
    ]
    # 자석 hole: 아래 면 (z=0) 에서 위로 5.3mm
    magnet_hole_locs = [(x, y, 0) for x, y in positions]
    # Ring hole: 위 면 (z=10) 에서 아래로 4mm → z=6..10
    ring_hole_locs = [(x, y, HEIGHT - RING_DEPTH) for x, y in positions]

    with BuildPart() as part:
        # 아래 cone (z=0..2.1, 아래 Ø27.6 → 위 Ø30) — inner_shell cone 스토퍼와 매칭
        Cone(
            bottom_radius=CONE_BOTTOM_OD / 2,
            top_radius=OUTER_D / 2,
            height=CONE_DEPTH,
            align=ALIGN_BOTTOM,
        )
        # 위 cylinder (z=2.1..10)
        with Locations((0, 0, CONE_DEPTH)):
            Cylinder(OUTER_D / 2, HEIGHT - CONE_DEPTH, align=ALIGN_BOTTOM)
        # 자석 hole (아래에서 위로 5.3mm)
        with Locations(*magnet_hole_locs):
            Cylinder(HOLE_D / 2, HOLE_DEPTH, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        # Ring hole (위에서 아래로 4mm)
        with Locations(*ring_hole_locs):
            Cylinder(RING_OD / 2, RING_DEPTH, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        # Center rect (아래에서 위로 5.1mm, pillar BOTTOM 단 자리)
        Box(CENTER_RECT_X, CENTER_RECT_Y, CENTER_RECT_DEPTH,
            align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        # Center slot (전체 관통, pillar TOP 단 자리)
        Box(CENTER_SLOT_X, CENTER_SLOT_Y, HEIGHT,
            align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    return part.part


# ============================================================
# handle (좌/우 두 부품). 옆모습 곡선 (위 PILLAR + 아래 GRIP + Spline)
# ============================================================
def build_handle():
    GRIP_X = 7
    GRIP_Y = 7
    GRIP_H = 4
    PILLAR_Y = 3
    PILLAR_H = 16
    TOTAL_H = GRIP_H + PILLAR_H
    FLAT_SIDE_Y = GRIP_Y / 2
    GRIP_CURVE_Y = -GRIP_Y / 2
    PILLAR_CURVE_Y = FLAT_SIDE_Y - PILLAR_Y
    CURVE_Z_BOTTOM = 4
    CURVE_Z_TOP = 12
    TIGHT_TOL = 0.1
    HOLE_SIZE = 4 + 2 * TIGHT_TOL
    HOLE_GAP_FROM_FLAT = 3
    HOLE_DEPTH = 7

    with BuildPart() as part:
        with BuildSketch(Plane.YZ):
            with BuildLine():
                Line((GRIP_CURVE_Y, 0), (FLAT_SIDE_Y, 0))
                Line((FLAT_SIDE_Y, 0), (FLAT_SIDE_Y, TOTAL_H))
                Line((FLAT_SIDE_Y, TOTAL_H), (PILLAR_CURVE_Y, TOTAL_H))
                Line((PILLAR_CURVE_Y, TOTAL_H), (PILLAR_CURVE_Y, CURVE_Z_TOP))
                Spline((PILLAR_CURVE_Y, CURVE_Z_TOP),
                       (GRIP_CURVE_Y, CURVE_Z_BOTTOM),
                       tangents=((0, -1), (0, -1)))
                Line((GRIP_CURVE_Y, CURVE_Z_BOTTOM), (GRIP_CURVE_Y, 0))
            make_face()
        extrude(amount=GRIP_X / 2, both=True)
        with Locations((0, FLAT_SIDE_Y - HOLE_GAP_FROM_FLAT, 0)):
            Box(HOLE_SIZE, HOLE_SIZE, HOLE_DEPTH,
                align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

    handle_offset = (GRIP_X + 2) / 2  # HANDLE_GAP = 2
    result_left = Location((-handle_offset, 0, 0)) * part.part
    result_right = Location((handle_offset, 0, 0)) * part.part
    return result_left, result_right


# ============================================================
# handle_pin — 4×4×16 사각 핀 (위/아래 챔퍼)
# ============================================================
def build_handle_pin():
    INSERT_X = 4
    INSERT_Y = 4
    INSERT_H = 16
    CHAMFER_SIZE = 0.5

    with BuildPart() as part:
        Box(INSERT_X, INSERT_Y, INSERT_H, align=ALIGN_BOTTOM)
        chamfer(
            [e for e in part.edges()
             if abs(e.center().Z) < 0.01 or abs(e.center().Z - INSERT_H) < 0.01],
            length=CHAMFER_SIZE,
        )
    return part.part


# ============================================================
# inner_shell — Ø38.4 wall × 20 실린더만
# ============================================================
def build_inner_shell():
    LOOSE_TOL = 0.2
    INNER_D = 30 + 2 * LOOSE_TOL
    WALL_THICKNESS = 4
    WALL_H = 20
    WALL_OUTER_D = INNER_D + 2 * WALL_THICKNESS
    BODY_RING_OD_BASE = 27.6
    BODY_RING_DEPTH = 2.1
    INNER_D_NARROW = BODY_RING_OD_BASE + 2 * LOOSE_TOL
    TOP_HOLE_D = 2.8
    TOP_HOLE_DEPTH = 5.0  # cover bolt pin (5mm) 수용 — 이전 3.6
    TOP_HOLE_R = (INNER_D + WALL_OUTER_D) / 4

    with BuildPart() as part:
        Cylinder(WALL_OUTER_D / 2, WALL_H, align=ALIGN_BOTTOM)
        # 아래 cone 스토퍼 (z=0..2.1, 아래 Ø28 → 위 Ø30.4) — 자기 정렬용 대각선
        Cone(
            bottom_radius=INNER_D_NARROW / 2,
            top_radius=INNER_D / 2,
            height=BODY_RING_DEPTH,
            align=ALIGN_BOTTOM,
            mode=Mode.SUBTRACT,
        )
        # 위 chamber (z=2.1..20, Ø30.4 직선)
        with Locations((0, 0, BODY_RING_DEPTH)):
            Cylinder(INNER_D / 2, WALL_H - BODY_RING_DEPTH,
                     align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        top_z = WALL_H
        top_hole_locs = [
            (TOP_HOLE_R * math.cos(a), TOP_HOLE_R * math.sin(a), top_z - TOP_HOLE_DEPTH)
            for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2)
        ]
        with Locations(*top_hole_locs):
            Cylinder(TOP_HOLE_D / 2, TOP_HOLE_DEPTH,
                     align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    return part.part


# ============================================================
# inner_shell_cover — Ø38.4 disc (inner_shell wall 에 fit) + Ø15 기둥 × 35
# ============================================================
def build_inner_shell_cover():
    OUTER_D = 38.4  # inner_shell wall 외경에 딱 맞음 (처마 제거)
    HEIGHT = 3
    BOLT_HOLE_D = 2.2
    BOLT_HOLE_R = 17.2
    RING_HOLE_D = 3
    RING_HOLE_R = 10
    RING_HOLE_COUNT = 8
    PILLAR_D = 15
    PILLAR_H = 38   # 35 → 38 (cover top 두께 +3 매칭)
    LOOSE_TOL = 0.2
    SLOT_SIZE = 7 + 2 * LOOSE_TOL
    SLOT_DEPTH = 23   # 20 → 23 (PILLAR_H +3 보상, slot 아래 끝 원위치 유지)
    PASS_HOLE_X = 7 + 2 * LOOSE_TOL
    PASS_HOLE_Y = 2.5 + 2 * LOOSE_TOL
    PILLAR_CHAMFER_SIDE = 0.5
    PILLAR_CHAMFER_TOP = 0.3

    bolt_hole_locs = [
        (BOLT_HOLE_R * math.cos(a), BOLT_HOLE_R * math.sin(a), 0)
        for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2)
    ]
    ring_hole_locs = [
        (RING_HOLE_R * math.cos(2 * math.pi * i / RING_HOLE_COUNT),
         RING_HOLE_R * math.sin(2 * math.pi * i / RING_HOLE_COUNT), 0)
        for i in range(RING_HOLE_COUNT)
    ]

    # Spring pins (cover 디스크의 ring_hole 위치에 통합. 위 끝 z=HEIGHT, 둥근 머리 아래 향함)
    PIN_D = 3
    PIN_TOTAL_H = 8
    PIN_CYL_H = PIN_TOTAL_H - PIN_D / 2  # 6.5
    PIN_TOP_Z = HEIGHT                    # cover 디스크 위 면 (3)
    PIN_CYL_BOTTOM_Z = PIN_TOP_Z - PIN_CYL_H  # -3.5 (sphere center)

    # Bolt pin — 이전 bolt hole subtract → 봉 add (spring pin 과 같은 형태)
    BOLT_PIN_D = 2.7                                 # wall hole Ø2.8 - 0.1 양쪽 0.05 (빡빡 press fit)
    BOLT_PIN_TOTAL_H = 8
    BOLT_PIN_CYL_H = BOLT_PIN_TOTAL_H - BOLT_PIN_D / 2  # 6.7
    BOLT_PIN_BOTTOM_Z = HEIGHT - BOLT_PIN_CYL_H        # 3 - 6.7 = -3.7

    with BuildPart() as part:
        Cylinder(OUTER_D / 2, HEIGHT, align=ALIGN_BOTTOM)
        Cylinder(PILLAR_D / 2, PILLAR_H, align=ALIGN_BOTTOM)
        with Locations((0, 0, PILLAR_H - SLOT_DEPTH)):
            Box(PILLAR_D + 10, SLOT_SIZE, SLOT_DEPTH,
                align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        Box(PASS_HOLE_Y, PASS_HOLE_X, PILLAR_H + 2,
            align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        chamfer(
            [e for e in part.edges() if abs(e.center().Z - PILLAR_H) < 0.01],
            length=PILLAR_CHAMFER_SIDE, length2=PILLAR_CHAMFER_TOP,
        )
        # Spring pins — ring_hole 위치에 통합. 둥근 머리 아래 향함.
        with Locations(*[(x, y, PIN_CYL_BOTTOM_Z) for x, y, _ in ring_hole_locs]):
            Cylinder(PIN_D / 2, PIN_CYL_H, align=ALIGN_BOTTOM)
        with Locations(*[(x, y, PIN_CYL_BOTTOM_Z) for x, y, _ in ring_hole_locs]):
            Sphere(PIN_D / 2)
        # Bolt pins — 이전 bolt_hole_locs 위치 (R=17.2, 4개). inner_shell wall hole 끼움.
        with Locations(*[(x, y, BOLT_PIN_BOTTOM_Z) for x, y, _ in bolt_hole_locs]):
            Cylinder(BOLT_PIN_D / 2, BOLT_PIN_CYL_H, align=ALIGN_BOTTOM)
        with Locations(*[(x, y, BOLT_PIN_BOTTOM_Z) for x, y, _ in bolt_hole_locs]):
            Sphere(BOLT_PIN_D / 2)
    return part.part


# ============================================================
# inner_shell_cover_top — Ø30 × 3. 기둥 위 캡 (원형 + 사각)
# ============================================================
def build_inner_shell_cover_top():
    DISC_D = 30
    DISC_H = 6                              # 3 → 6 (두께 +3, 끼우는 영역 깊게)
    PRESS_TOL = 0.05                        # 빡빡 press fit (이전 0.1)
    PILLAR_D = 15
    HOLE_D = PILLAR_D + 2 * PRESS_TOL       # 15.1 (이전 15.2)
    RECT_W = 7 + 2 * PRESS_TOL              # 7.1 (이전 7.2)
    HOLE_DEPTH = 5                           # 2 → 5 (깊이 +3)

    with BuildPart() as part:
        Cylinder(DISC_D / 2, DISC_H, align=ALIGN_BOTTOM)
        with Locations((0, 0, DISC_H - HOLE_DEPTH)):
            Cylinder(HOLE_D / 2, HOLE_DEPTH, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        with Locations((0, 0, DISC_H - HOLE_DEPTH)):
            Box(HOLE_D, RECT_W, HOLE_DEPTH, align=ALIGN_BOTTOM, mode=Mode.ADD)
    return part.part


# ============================================================
# pillar — 10×2.5 (bottom) → 7×2.5 (top) 사각 기둥, 46 높이
# ============================================================
def build_pillar():
    BOTTOM_X = 10
    BOTTOM_Y = 2.5
    BOTTOM_H = 5
    TOP_X = 7
    TOP_Y = 2.5
    TOTAL_H = 48  # 중간 길이 +2 (이전 46)
    TIGHT_TOL = 0.1
    HOLE_SIZE = 4 + 2 * TIGHT_TOL
    HOLE_Z_FROM_TOP = 4
    CHAMFER_SIZE = 0.5

    with BuildPart() as part:
        Box(BOTTOM_X, BOTTOM_Y, BOTTOM_H, align=ALIGN_BOTTOM)
        with Locations((0, 0, BOTTOM_H)):
            Box(TOP_X, TOP_Y, TOTAL_H - BOTTOM_H, align=ALIGN_BOTTOM)
        with Locations((0, 0, TOTAL_H - HOLE_Z_FROM_TOP)):
            Box(HOLE_SIZE, TOP_Y + 4, HOLE_SIZE, mode=Mode.SUBTRACT)
        chamfer(
            [e for e in part.edges() if abs(e.center().Z - TOTAL_H) < 0.01],
            length=CHAMFER_SIZE,
        )
        chamfer(
            [e for e in part.edges()
             if abs(e.center().Z - BOTTOM_H) < 0.01
             and abs(e.center().X) > TOP_X / 2 + 0.1],
            length=CHAMFER_SIZE,
        )
    return part.part


# ============================================================
# Assembly — 그리드 layout 으로 펼침
# ============================================================
body_p = build_body()
handle_left, handle_right = build_handle()
handle_pin_p = build_handle_pin()
inner_shell_p = build_inner_shell()
inner_shell_cover_p = build_inner_shell_cover()
inner_shell_cover_top_p = build_inner_shell_cover_top()
pillar_p = build_pillar()

parts = [
    Pos(0, 0, 0) * body_p,
    Pos(100, 0, 0) * handle_left,
    Pos(100, 30, 0) * handle_right,
    Pos(200, 0, 0) * handle_pin_p,
    Pos(0, 100, 0) * inner_shell_p,
    Pos(100, 100, 0) * inner_shell_cover_p,
    Pos(200, 100, 0) * inner_shell_cover_top_p,
    Pos(0, 220, 0) * pillar_p,
]

assembly = parts[0]
for p in parts[1:]:
    assembly = assembly + p

finalize_iteration(assembly)

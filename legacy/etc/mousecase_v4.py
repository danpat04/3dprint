"""mousecase v4 — 처음부터 다시 설계."""

from build123d import (
    Align, Box, BuildLine, BuildPart, BuildSketch, Cylinder, Locations, Mode,
    Plane, Polyline, extrude, make_face,
)
from ocp_vscode import Camera, show

# 벽 두께 (mm)
WALL = 1.5            # 왼쪽/위/바닥 벽
WALL_FB = 2.6         # 앞/뒤 벽 (두꺼움)
WALL_FB_THIN = 1.5    # 오른쪽 돌출 부분의 앞/뒤 벽 (얇음)

# 내부 치수 (mm) — 고정
INNER_W = 63.5
INNER_D = 107.5
INNER_H = 26

# 외부 치수 (mm) — 앞/뒤 벽이 두꺼워지면 외부 깊이도 늘어남
OUTER_W = 65                        # 폭 (X)
OUTER_D = INNER_D + 2 * WALL_FB     # 깊이 112.7 (내부 유지, 앞/뒤로 확장)
OUTER_H = 29                        # 높이 (Z)

# 사다리꼴 기둥 (직각삼각형 2mm × 1.5mm에서 1.5mm 변의 0.3mm를 잘라낸 단면)
PILLAR_BASE = 2.0
PILLAR_ORIG_H = 1.5
PILLAR_CUT = 0.3
PILLAR_H = PILLAR_ORIG_H - PILLAR_CUT                  # 1.2
PILLAR_TOP = PILLAR_BASE * PILLAR_CUT / PILLAR_ORIG_H  # 0.4
PILLAR_LEN = 29                                         # 기둥 Z 길이

# 기둥 직각 꼭짓점 (오른쪽 외벽 경계)
PILLAR_X = OUTER_W / 2                      # 32.5
PILLAR_Y_FRONT = -OUTER_D / 2 + WALL_FB_THIN  # -54.85 (얇은 벽 내부)
PILLAR_Y_BACK = OUTER_D / 2 - WALL_FB_THIN    # +54.85

# 안쪽 사각 기둥 치수 (앞/뒤 둘 다 동일)
INNER_PILLAR_W = 60.5
INNER_PILLAR_D = 10
INNER_PILLAR_H = 8
INNER_PILLAR_X_END = -OUTER_W / 2 + WALL + INNER_PILLAR_W             # 29.5 (기둥 +X 끝)
INNER_PILLAR_CY_FRONT = -OUTER_D / 2 + WALL_FB + INNER_PILLAR_D / 2   # -48.75
INNER_PILLAR_CY_BACK = OUTER_D / 2 - WALL_FB - INNER_PILLAR_D / 2     # 48.75
INNER_PILLAR_CZ = OUTER_H - WALL - INNER_PILLAR_H / 2                  # 23.5

# 안쪽 기둥에 +X에서 파낼 원기둥
INNER_HOLE_R = 4.97 / 2
INNER_HOLE_DEPTH = 5.2

with BuildPart() as part:
    Box(
        OUTER_W, OUTER_D, OUTER_H,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # 오른쪽 벽에서 안쪽으로 상자 모양 파냄 — 오른쪽만 뚫리고 나머지 면은 1.5mm 벽
    with Locations((-OUTER_W / 2 + WALL, 0, (OUTER_H - INNER_H) / 2)):
        Box(
            INNER_W, INNER_D, INNER_H,
            align=(Align.MIN, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )
    # 오른쪽 위 천장 일부를 Y 방향 내부 깊이, 폭 3mm로 추가로 파냄
    with Locations((OUTER_W / 2, 0, OUTER_H)):
        Box(
            3, INNER_D, WALL,
            align=(Align.MAX, Align.CENTER, Align.MAX),
            mode=Mode.SUBTRACT,
        )
    # 오른쪽 돌출 부분(X=29.5~32.5)의 앞/뒤 벽만 1.5mm로 얇게 — 내부를 1.1씩 확장
    # Z 범위 WALL~OUTER_H (바닥은 건드리지 않음)
    with Locations((INNER_PILLAR_X_END, -OUTER_D / 2 + WALL_FB_THIN, WALL)):
        Box(
            3, WALL_FB - WALL_FB_THIN, OUTER_H - WALL,
            align=(Align.MIN, Align.MIN, Align.MIN),
            mode=Mode.SUBTRACT,
        )
    with Locations((INNER_PILLAR_X_END, OUTER_D / 2 - WALL_FB_THIN, WALL)):
        Box(
            3, WALL_FB - WALL_FB_THIN, OUTER_H - WALL,
            align=(Align.MIN, Align.MAX, Align.MIN),
            mode=Mode.SUBTRACT,
        )
    # 앞쪽 위 내부 사각 기둥 — 왼쪽/앞쪽/위쪽 내벽에 붙음
    with Locations((-OUTER_W / 2 + WALL, -OUTER_D / 2 + WALL_FB, OUTER_H - WALL)):
        Box(
            60.5, 10, 8,
            align=(Align.MIN, Align.MIN, Align.MAX),
        )
    # 뒤쪽 위 내부 사각 기둥 — 왼쪽/뒤쪽/위쪽 내벽에 붙음
    with Locations((-OUTER_W / 2 + WALL, OUTER_D / 2 - WALL_FB, OUTER_H - WALL)):
        Box(
            60.5, 10, 8,
            align=(Align.MIN, Align.MAX, Align.MAX),
        )

    # 앞쪽 사다리꼴 기둥 — 2mm 바닥이 앞쪽(-Y), 1.2mm 수직변이 오른쪽(+X), Z 방향 29mm
    with BuildSketch(Plane.XY) as pillar_front:
        with BuildLine():
            Polyline(
                (PILLAR_X, PILLAR_Y_FRONT),
                (PILLAR_X - PILLAR_BASE, PILLAR_Y_FRONT),
                (PILLAR_X - PILLAR_TOP, PILLAR_Y_FRONT + PILLAR_H),
                (PILLAR_X, PILLAR_Y_FRONT + PILLAR_H),
                close=True,
            )
        make_face()
    extrude(amount=PILLAR_LEN)

    # 뒤쪽 사다리꼴 기둥 — 앞쪽 기둥을 X-Z 평면 기준(Y 반전) 대칭
    with BuildSketch(Plane.XY) as pillar_back:
        with BuildLine():
            Polyline(
                (PILLAR_X, PILLAR_Y_BACK),
                (PILLAR_X - PILLAR_BASE, PILLAR_Y_BACK),
                (PILLAR_X - PILLAR_TOP, PILLAR_Y_BACK - PILLAR_H),
                (PILLAR_X, PILLAR_Y_BACK - PILLAR_H),
                close=True,
            )
        make_face()
    extrude(amount=PILLAR_LEN)

    # 안쪽 앞/뒤 사각 기둥에 오른쪽(+X)에서 원기둥 구멍 2개
    with Locations(Plane.YZ.offset(INNER_PILLAR_X_END)):
        with Locations(
            (INNER_PILLAR_CY_FRONT, INNER_PILLAR_CZ),
            (INNER_PILLAR_CY_BACK, INNER_PILLAR_CZ),
        ):
            Cylinder(
                INNER_HOLE_R, INNER_HOLE_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
                mode=Mode.SUBTRACT,
            )

show(part, reset_camera=Camera.RESET)

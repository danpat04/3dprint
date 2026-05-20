"""mousecase v3 — 처음부터 다시 설계."""

from build123d import (
    Align, Box, BuildLine, BuildPart, BuildSketch, Cylinder,
    Locations, Mode, Plane, Polyline, chamfer, extrude, make_face,
)
from ocp_vscode import Camera, show

# 외부 치수 (mm)
OUTER_W = 65      # 폭 (X)
OUTER_D = 110.5   # 깊이 (Y)
OUTER_H = 39      # 높이 (Z)

# 내부 공간 치수 (mm)
INNER_W = 60.5
INNER_D = 107.5
INNER_H = 26

WALL = 1.5        # 왼쪽/위 벽 두께
BOTTOM = OUTER_H - INNER_H - WALL  # 바닥 두께 = 11.5

# 오른쪽 벽 사각형 파냄 치수
CUTOUT_W = 3
CUTOUT_D = 107.5
CUTOUT_H = 37.5
CUTOUT_INNER_X = OUTER_W / 2 - CUTOUT_W  # 파낸 면의 -X 쪽 경계 (29.5)

# 오른쪽 파낸 면에서 파들어갈 원기둥 4개 (v1/v2와 동일한 배치)
HOLE_R = 10.5 / 2
HOLE_DEPTH = 45
HOLE_GAP = 1
HOLE_PITCH = HOLE_R * 2 + HOLE_GAP        # 중심 간 거리 11.5
HOLE_Z = BOTTOM / 2                        # 바닥 두께 중앙 5.75
HOLE_YS = [-1.5 * HOLE_PITCH, -0.5 * HOLE_PITCH,
            0.5 * HOLE_PITCH,  1.5 * HOLE_PITCH]

# 기둥 — 직각 사다리꼴 단면 (직각삼각형의 수직변 0.2mm를 잘라낸 모양)
PILLAR_BASE = 2.0                                   # 앞쪽 향하는 바닥 (긴 평행 변)
PILLAR_ORIG_H = 1.5                                 # 원래 수직변 (자르기 전)
PILLAR_CUT = 0.5                                    # 위에서 잘라내는 높이 (chamfer 0.5 여유 확보)
PILLAR_H = PILLAR_ORIG_H - PILLAR_CUT                # 사다리꼴 높이 1.3
PILLAR_TOP = PILLAR_BASE * PILLAR_CUT / PILLAR_ORIG_H  # 짧은 평행 변 ≈ 0.267
PILLAR_LEN = 37.5                                   # 기둥 Z 길이

# 기둥 직각 꼭짓점 X (파낸 부분 오른쪽 끝)
PILLAR_X = OUTER_W / 2           # 32.5
PILLAR_Y_FRONT = -OUTER_D / 2 + WALL  # -53.75 (앞쪽)
PILLAR_Y_BACK = OUTER_D / 2 - WALL    # +53.75 (뒤쪽, X축 기준 반전)

with BuildPart() as part:
    Box(
        OUTER_W, OUTER_D, OUTER_H,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # 외곽 직육면체 모서리 0.5mm 챔퍼 — +X 쪽 4개는 기둥 챔퍼와 충돌하므로 제외
    half_w = OUTER_W / 2
    box_outer_edges = [
        e for e in part.edges()
        if abs(e.center().X - half_w) > 1e-3
    ]
    chamfer(box_outer_edges, length=0.5)
    # 내부 공간 — 왼쪽 위 꼭짓점에서 1.5mm 안쪽, Y는 중앙 대칭
    with Locations((-OUTER_W / 2 + WALL, 0, OUTER_H - WALL)):
        Box(
            INNER_W, INNER_D, INNER_H,
            align=(Align.MIN, Align.CENTER, Align.MAX),
            mode=Mode.SUBTRACT,
        )
    # 오른쪽 벽을 사각형으로 파냄 — 오른쪽 바닥에 붙이고 앞쪽 외벽에서 1.5mm 떨어짐
    with Locations((OUTER_W / 2, -OUTER_D / 2 + WALL, 0)):
        Box(
            CUTOUT_W, CUTOUT_D, CUTOUT_H,
            align=(Align.MAX, Align.MIN, Align.MIN),
            mode=Mode.SUBTRACT,
        )

    # 오른쪽 파낸 면 기준으로 원기둥 4개를 -X 방향으로 파냄
    with Locations(Plane.YZ.offset(CUTOUT_INNER_X)):
        with Locations(*[(y, HOLE_Z) for y in HOLE_YS]):
            Cylinder(
                HOLE_R, HOLE_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
                mode=Mode.SUBTRACT,
            )

    # 앞쪽 기둥 — 2mm 바닥은 앞쪽(-Y), 1.3mm 수직변은 오른쪽(+X)
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

    # 뒤쪽 기둥 — 앞쪽 기둥을 X축 기준 반전 (2mm 바닥이 뒤쪽(+Y))
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

    # 기둥 수직변 밑면 chamfer — X=PILLAR_X, Z=0인 Y 방향 에지 (박스 +X 쪽 남은 부분과 합쳐져 있음)
    pillar_bottom_edges = [
        e for e in part.edges()
        if abs(e.center().X - PILLAR_X) < 1e-3
        and abs(e.center().Z) < 1e-3
    ]
    chamfer(pillar_bottom_edges, length=0.5)

show(part, reset_camera=Camera.RESET)

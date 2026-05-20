"""mousehead_cover — 새로운 모델링."""

from build123d import Align, Box, BuildPart, Cylinder, Locations, Mode, chamfer
from ocp_vscode import Camera, show

# 외부 치수 (mm) — 왼쪽 외곽선은 X=-31.75로 고정 (구멍 위치 유지)
OUTER_W = 27.5
OUTER_D = 109.7   # 기존 107.5에서 양쪽 1.1mm씩 확장 (case 돌출부 내부 맞춤)
OUTER_H = 3
BOX_LEFT = -31.75
BOX_RIGHT = BOX_LEFT + OUTER_W       # -4.25
BOX_CENTER_X = BOX_LEFT + OUTER_W / 2  # -18

# 앞-위 모서리 비대칭 챔퍼
CHAMFER_TOP = 1.65    # 위쪽 면에서 앞쪽으로 깎는 거리
CHAMFER_FRONT = 2.15  # 앞쪽 면에서 아래로 깎는 거리

# 앞/뒤/오른쪽 수직 면을 얇게 깎기 (챔퍼 영역은 건드리지 않음)
FACE_CUT = 0.15

# Z 방향으로 파낼 원기둥 (v4 원기둥과 같은 위치, 아랫면에서 깊이 2.1)
HOLE_R = 4.97 / 2
HOLE_DEPTH = 2.1
HOLE_X = BOX_LEFT + 5.5   # 왼쪽 외곽에서 5.5mm → X=-26.25
HOLE_Y = 48.75            # X축에서 ±48.75

with BuildPart() as part:
    with Locations((BOX_CENTER_X, 0, 0)):
        Box(
            OUTER_W, OUTER_D, OUTER_H,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    # 앞쪽-위쪽 모서리 (Y=-OUTER_D/2, Z=OUTER_H)만 선택
    top_front_edges = [
        e for e in part.edges()
        if abs(e.center().Y - (-OUTER_D / 2)) < 1e-3
        and abs(e.center().Z - OUTER_H) < 1e-3
    ]
    chamfer(top_front_edges, length=CHAMFER_FRONT, length2=CHAMFER_TOP)

    # 뒤쪽-위쪽 모서리 (Y=+OUTER_D/2, Z=OUTER_H) — X-Z 평면 반전 대칭
    top_back_edges = [
        e for e in part.edges()
        if abs(e.center().Y - OUTER_D / 2) < 1e-3
        and abs(e.center().Z - OUTER_H) < 1e-3
    ]
    chamfer(top_back_edges, length=CHAMFER_TOP, length2=CHAMFER_FRONT)

    # 앞쪽 면 전체(챔퍼 포함)를 Y 방향으로 안쪽으로 — 각도는 유지
    with Locations((BOX_CENTER_X, -OUTER_D / 2, 0)):
        Box(
            OUTER_W, FACE_CUT, OUTER_H,
            align=(Align.CENTER, Align.MIN, Align.MIN),
            mode=Mode.SUBTRACT,
        )
    # 뒤쪽 면도 동일 (X-Z 평면 반전)
    with Locations((BOX_CENTER_X, OUTER_D / 2, 0)):
        Box(
            OUTER_W, FACE_CUT, OUTER_H,
            align=(Align.CENTER, Align.MAX, Align.MIN),
            mode=Mode.SUBTRACT,
        )
    # 오른쪽 면도 안쪽으로 깎음
    with Locations((BOX_RIGHT, 0, 0)):
        Box(
            FACE_CUT, OUTER_D, OUTER_H,
            align=(Align.MAX, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )
    # 상단(구멍 없는 쪽) 면도 깎음 — 세운 상태에서 X 방향 공차 확보, 챔퍼 각도는 유지
    with Locations((BOX_CENTER_X, 0, OUTER_H)):
        Box(
            OUTER_W, OUTER_D, FACE_CUT,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
            mode=Mode.SUBTRACT,
        )

    # Z 방향 원기둥 2개 — 아랫면(Z=0)에서 위로 2.1mm 깊이
    with Locations(
        (HOLE_X, -HOLE_Y, 0),
        (HOLE_X, HOLE_Y, 0),
    ):
        Cylinder(
            HOLE_R, HOLE_DEPTH,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )

show(part, reset_camera=Camera.RESET)

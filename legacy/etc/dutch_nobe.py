"""dutch_nobe — 새로운 모델링."""

from build123d import (
    Align, Box, BuildLine, BuildPart, BuildSketch, Cylinder, Locations, Mode,
    Plane, Polyline, extrude, make_face, mirror,
)
from ocp_vscode import Camera, show

# 외부 치수 (mm)
OUTER_W = 17.5    # 폭 (X)
OUTER_D = 45      # 깊이 (Y)
OUTER_H = 12.5    # 높이 (Z)

# 사선으로 깎기 (좌우에서 본 단면이 직각삼각형인 X 방향 기둥)
SLOPE_Z = 10           # 앞쪽 면(-Y)에서 사선 시작 Z 위치
SLOPE_LEN_Y = 30       # 앞에서 Y 방향으로 깎는 길이

# Y=0이 SLOPE 끝(미러 기준)이 되도록 박스를 Y 방향으로 이동
# 박스 -Y 끝 = -SLOPE_LEN_Y (-30), +Y 끝 = OUTER_D - SLOPE_LEN_Y (10)
BOX_FRONT_Y = -SLOPE_LEN_Y
BOX_BACK_Y = OUTER_D - SLOPE_LEN_Y
BOX_CENTER_Y = (BOX_FRONT_Y + BOX_BACK_Y) / 2  # -10

# X=0 기준으로 왼쪽에 5mm만 남도록 박스 위치 결정 (박스 -X 끝 = -5)
BOX_CENTER_X = OUTER_W / 2 - 5   # 3.75

# Z 방향: 박스 위쪽이 Z=0, 바닥이 Z=-OUTER_H
BOX_TOP_Z = 0
BOX_BOTTOM_Z = -OUTER_H          # -12.5

with BuildPart() as part:
    with Locations((BOX_CENTER_X, BOX_CENTER_Y, BOX_BOTTOM_Z)):
        Box(
            OUTER_W, OUTER_D, OUTER_H,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    # 직각삼각형: 사선 시작 Z = BOX_BOTTOM_Z + SLOPE_Z, 박스 바닥 = BOX_BOTTOM_Z
    with BuildSketch(Plane.YZ.offset(BOX_CENTER_X)) as triangle:
        with BuildLine():
            Polyline(
                (BOX_FRONT_Y, BOX_BOTTOM_Z + SLOPE_Z),
                (BOX_FRONT_Y, BOX_BOTTOM_Z),
                (0, BOX_BOTTOM_Z),
                close=True,
            )
        make_face()
    extrude(amount=OUTER_W / 2 + 1, both=True, mode=Mode.SUBTRACT)

    # Y=0을 기준으로 X-Z 평면 미러
    with BuildSketch(Plane.YZ.offset(BOX_CENTER_X)) as triangle_mirror:
        with BuildLine():
            Polyline(
                (SLOPE_LEN_Y, BOX_BOTTOM_Z + SLOPE_Z),
                (SLOPE_LEN_Y, BOX_BOTTOM_Z),
                (0, BOX_BOTTOM_Z),
                close=True,
            )
        make_face()
    extrude(amount=OUTER_W / 2 + 1, both=True, mode=Mode.SUBTRACT)

    # 원점 (0,0,0) 기준 X축을 축으로 하는 원기둥 (지름 13.5, 길이 12) 파냄
    with Locations(Plane.YZ):
        Cylinder(
            radius=13.5 / 2,
            height=12,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
            mode=Mode.SUBTRACT,
        )

    # 원점 (0,0,0) 기준 Y축을 축으로 하는 원기둥 (지름 5.3, 길이 42) 파냄
    with Locations(Plane.XZ):
        Cylinder(
            radius=5.3 / 2,
            height=42,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
            mode=Mode.SUBTRACT,
        )

    # Z 방향 원기둥 구멍 (지름 4.98, 깊이 5.3) — 위에서 아래로 파냄
    with Locations(
        (8.5, 10, 0),
        (8.5, -10, 0),
    ):
        Cylinder(
            radius=4.98 / 2,
            height=5.3,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
            mode=Mode.SUBTRACT,
        )

    # (0, -26, 0) Z 방향 원기둥 구멍 (지름 4.98, 깊이 2.2)
    with Locations((0, -26, 0)):
        Cylinder(
            radius=4.98 / 2,
            height=2.2,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
            mode=Mode.SUBTRACT,
        )

    # X=-10 기준 Y-Z 평면 거울상 모델링 추가
    mirror(about=Plane.YZ.offset(-10))

show(part, reset_camera=Camera.RESET)

"""그라인더."""

import math
from datetime import datetime
from pathlib import Path

from build123d import (
    Align, Axis, Box, BuildPart, BuildSketch, Circle, Cylinder, Locations,
    Mode, Plane, loft,
)
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from ocp_vscode import Camera, show

# 상수 (mm)
OUTER_D = 60.5          # 외경 지름
INNER_D = 58.5          # 내경 지름
HEIGHT = 7              # 실린더 높이
CONE_LEFT_ANGLE = 48.15     # 외부 원뿔 왼쪽 각도
CONE_RIGHT_ANGLE = 46.04   # 외부 원뿔 오른쪽 각도
SUB_D = 55                  # 빼는 원뿔 바닥 지름
SUB_LEFT_ANGLE = 52.9       # 빼는 원뿔 왼쪽 각도
SUB_RIGHT_ANGLE = 57.51     # 빼는 원뿔 오른쪽 각도
SPLIT_GAP = 3               # 반으로 가른 간격

# 계산값
OUTER_R = OUTER_D / 2
INNER_R = INNER_D / 2

a = math.tan(math.radians(CONE_LEFT_ANGLE))
b = math.tan(math.radians(CONE_RIGHT_ANGLE))
CONE_APEX_X = OUTER_R * (b - a) / (a + b)
CONE_H = a * (CONE_APEX_X + OUTER_R)

SUB_R = SUB_D / 2
sa = math.tan(math.radians(SUB_LEFT_ANGLE))
sb = math.tan(math.radians(SUB_RIGHT_ANGLE))
SUB_APEX_X = SUB_R * (sb - sa) / (sa + sb)
SUB_H = sa * (SUB_APEX_X + SUB_R)

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    # 실린더
    Cylinder(OUTER_R, HEIGHT, align=ALIGN_BOTTOM)
    Cylinder(INNER_R, HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

    # 비대칭 원뿔 (실린더 위에 올림)
    with BuildSketch(Plane.XY.offset(HEIGHT)) as base:
        Circle(OUTER_R)

    apex_plane = Plane(
        origin=(CONE_APEX_X, 0, HEIGHT + CONE_H),
        z_dir=(0, 0, 1),
    )
    with BuildSketch(apex_plane) as tip:
        Circle(0.01)

    loft([base.sketch, tip.sketch])

    # 빼는 비대칭 원뿔
    with BuildSketch(Plane.XY.offset(HEIGHT)) as sub_base:
        Circle(SUB_R)

    sub_apex_plane = Plane(
        origin=(SUB_APEX_X, 0, HEIGHT + SUB_H),
        z_dir=(0, 0, 1),
    )
    with BuildSketch(sub_apex_plane) as sub_tip:
        Circle(0.01)

    loft([sub_base.sketch, sub_tip.sketch], mode=Mode.SUBTRACT)

    # Y=0 기준으로 반을 가르기 (SPLIT_GAP 만큼 슬릿)
    max_dim = OUTER_R + CONE_H + 10
    Box(2 * max_dim, SPLIT_GAP, 2 * max_dim,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
        mode=Mode.SUBTRACT)

    # 두 반쪽을 Y방향으로 벌리기는 build123d에서 직접 이동이 어려우므로
    # 슬릿으로 간격을 만듦

result = part.part

# STL 내보내기
export_dir = Path(__file__).resolve().parent.parent.parent / "exports"
export_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
stl_path = export_dir / f"grider_{timestamp}.stl"
BRepMesh_IncrementalMesh(result.wrapped, 0.1)
writer = StlAPI_Writer()
writer.Write(result.wrapped, str(stl_path))
print(f"Exported: {stl_path}")

show(result, reset_camera=Camera.RESET)

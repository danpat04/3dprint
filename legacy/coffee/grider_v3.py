"""그라인더 v3."""

import math
from datetime import datetime
from pathlib import Path

from build123d import (
    Align, BuildPart, BuildSketch, Circle, Cylinder, Mode, Plane, loft,
)
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from ocp_vscode import Camera, show

# 상수 (mm)
OUTER_BASE = 59.5           # 외부 원뿔 밑변 (지름)
INNER_BASE = 55             # 내부 원뿔 밑변 (지름)
CYL_HEIGHT = 10             # 실린더 높이
CYL_OUTER_D = 59.5          # 실린더 외경
CYL_INNER_D = 58.5          # 실린더 내경
# 각도/절단 공용 상수
LEFT_DX = 22.55              # 왼쪽 수평 성분
LEFT_DZ = 29.7               # 왼쪽 수직 성분
RIGHT_DX = 8.1               # 오른쪽 수평 성분
RIGHT_DZ = 8.4               # 오른쪽 수직 성분
LEFT_TAN = LEFT_DZ / LEFT_DX
RIGHT_TAN = RIGHT_DZ / RIGHT_DX

# 외부 원뿔 계산
OUTER_R = OUTER_BASE / 2
OUTER_APEX_X = OUTER_R * (RIGHT_TAN - LEFT_TAN) / (LEFT_TAN + RIGHT_TAN)
OUTER_H = LEFT_TAN * (OUTER_APEX_X + OUTER_R)

# 내부 원뿔 계산 (같은 각도, 밑변만 다름)
INNER_R = INNER_BASE / 2
INNER_APEX_X = INNER_R * (RIGHT_TAN - LEFT_TAN) / (LEFT_TAN + RIGHT_TAN)
INNER_H = LEFT_TAN * (INNER_APEX_X + INNER_R)

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    # 실린더
    Cylinder(CYL_OUTER_D / 2, CYL_HEIGHT, align=ALIGN_BOTTOM)
    Cylinder(CYL_INNER_D / 2, CYL_HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

    # 외부 원뿔 (실린더 위에)
    with BuildSketch(Plane.XY.offset(CYL_HEIGHT)) as outer_base:
        Circle(OUTER_R)
    outer_apex_plane = Plane(
        origin=(OUTER_APEX_X, 0, CYL_HEIGHT + OUTER_H),
        z_dir=(0, 0, 1),
    )
    with BuildSketch(outer_apex_plane) as outer_tip:
        Circle(0.01)
    loft([outer_base.sketch, outer_tip.sketch])

    # 내부 원뿔 (파냄)
    with BuildSketch(Plane.XY.offset(CYL_HEIGHT)) as inner_base:
        Circle(INNER_R)
    inner_apex_plane = Plane(
        origin=(INNER_APEX_X, 0, CYL_HEIGHT + INNER_H),
        z_dir=(0, 0, 1),
    )
    with BuildSketch(inner_apex_plane) as inner_tip:
        Circle(0.01)
    loft([inner_base.sketch, inner_tip.sketch], mode=Mode.SUBTRACT)

    # 경사면으로 잘라내기
    cut_left = (-OUTER_R + LEFT_DX, 0, CYL_HEIGHT + LEFT_DZ)
    cut_right = (OUTER_R - RIGHT_DX, 0, CYL_HEIGHT + RIGHT_DZ)
    # 절단면 방향 벡터
    dx = cut_right[0] - cut_left[0]
    dz = cut_right[2] - cut_left[2]
    # 법선: 절단 방향 x Y축, 위쪽을 향하도록
    normal = (dz, 0, -dx)

from build123d import Axis, Part, Vector, Location
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepPrimAPI import BRepPrimAPI_MakeHalfSpace
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.gp import gp_Pnt, gp_Dir, gp_Pln

cut_pnt = gp_Pnt(cut_left[0], cut_left[1], cut_left[2])
cut_dir = gp_Dir(normal[0], normal[1], normal[2])
cut_plane = gp_Pln(cut_pnt, cut_dir)
cut_face = BRepBuilderAPI_MakeFace(cut_plane, -200, 200, -200, 200).Face()
half_space = BRepPrimAPI_MakeHalfSpace(cut_face, gp_Pnt(cut_left[0], 0, cut_left[2] + 100)).Solid()

result = Part(BRepAlgoAPI_Cut(part.part.wrapped, half_space).Shape())

# 절단면이 XY 평면이 되도록 회전
cut_angle = math.degrees(math.atan2(dz, dx))
result = result.rotate(Axis.Y, -cut_angle)
# 바닥을 z=0에 맞춤
bb = result.bounding_box()
result = result.move(Location(Vector(0, 0, -bb.min.Z)))

# STL 내보내기
export_dir = Path(__file__).resolve().parent.parent.parent / "exports"
export_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
stl_path = export_dir / f"grider_v4_{timestamp}.stl"
BRepMesh_IncrementalMesh(result.wrapped, 0.1)
writer = StlAPI_Writer()
writer.Write(result.wrapped, str(stl_path))
print(f"Exported: {stl_path}")

show(result, reset_camera=Camera.RESET)

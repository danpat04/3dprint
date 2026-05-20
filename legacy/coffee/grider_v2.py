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

from build123d import Compound, Location, Vector
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepPrimAPI import BRepPrimAPI_MakeHalfSpace, BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt, gp_Dir, gp_Pln
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace

# Y>0 반쪽과 Y<0 반쪽을 분리
cut_plane_pos = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0))
cut_face_pos = BRepBuilderAPI_MakeFace(cut_plane_pos, -100, 100, -100, 100).Face()
half_space_pos = BRepPrimAPI_MakeHalfSpace(cut_face_pos, gp_Pnt(0, 100, 0)).Solid()
half_space_neg = BRepPrimAPI_MakeHalfSpace(cut_face_pos, gp_Pnt(0, -100, 0)).Solid()

from build123d import Part
positive_half = Part(BRepAlgoAPI_Cut(part.part.wrapped, half_space_neg).Shape())
negative_half = Part(BRepAlgoAPI_Cut(part.part.wrapped, half_space_pos).Shape())

# 각 반쪽을 잘린 면이 위를 보도록 회전 후 나란히 배치
pos_rotated = positive_half.rotate(Axis.X, -90)
pos_bb = pos_rotated.bounding_box()
pos_z_offset = -pos_bb.min.Z
pos_rotated = pos_rotated.move(Location(Vector(0, OUTER_R + SPLIT_GAP, pos_z_offset)))

neg_rotated = negative_half.rotate(Axis.X, 90)
neg_bb = neg_rotated.bounding_box()
neg_z_offset = -neg_bb.min.Z
neg_rotated = neg_rotated.move(Location(Vector(0, -(OUTER_R + SPLIT_GAP), neg_z_offset)))

result = Compound(children=[pos_rotated, neg_rotated])

# STL 내보내기
export_dir = Path(__file__).resolve().parent.parent.parent / "exports"
export_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
stl_path = export_dir / f"grider_v2_{timestamp}.stl"
BRepMesh_IncrementalMesh(result.wrapped, 0.1)
writer = StlAPI_Writer()
writer.Write(result.wrapped, str(stl_path))
print(f"Exported: {stl_path}")

show(result, reset_camera=Camera.RESET)

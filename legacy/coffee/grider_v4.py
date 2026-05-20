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

    # 원기둥 곡면으로 윗부분 도려내기
    # 두 절단 꼭지점 (절대좌표)
    p1_x = -OUTER_R + LEFT_DX
    p1_z = CYL_HEIGHT + LEFT_DZ
    p2_x = OUTER_R - RIGHT_DX
    p2_z = CYL_HEIGHT + RIGHT_DZ
    # 두 점을 지름으로 하는 원
    cut_r = math.sqrt((p2_x - p1_x)**2 + (p2_z - p1_z)**2) / 2
    cut_cx = (p1_x + p2_x) / 2
    cut_cz = (p1_z + p2_z) / 2

from build123d import Part
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Fuse
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir

# 원기둥 축: P1→P2 방향에 수직이면서 XZ 평면 내 (Z 방향에 가까운 기울어진 축)
dir_x = p2_x - p1_x
dir_z = p2_z - p1_z
# P1→P2에 수직인 방향 (XZ 평면 내 90도 회전)
axis_x = -dir_z  # 21.3
axis_z = dir_x   # 28.85
axis_len = math.sqrt(axis_x**2 + axis_z**2)

ax = gp_Ax2(
    gp_Pnt(cut_cx, 0, cut_cz),
    gp_Dir(axis_x / axis_len, 0, axis_z / axis_len),
)
cutter_cyl = BRepPrimAPI_MakeCylinder(ax, cut_r, 200).Shape()

# 원기둥을 모델에 합치기 (시각화용)
result = Part(BRepAlgoAPI_Fuse(part.part.wrapped, cutter_cyl).Shape())

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

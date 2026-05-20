"""그라인더 v4."""

from datetime import datetime
from pathlib import Path

import math

from build123d import (
    Align, BuildPart, BuildSketch, Circle, Cylinder, Locations, Mode, Plane, loft,
)
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from ocp_vscode import Camera, show

# 상수 (mm)
CYL_HEIGHT = 10             # 실린더 높이
CYL_OUTER_D = 59.5          # 실린더 외경
CYL_INNER_D = 58.5          # 실린더 내경
SOLID_H = 30                # 원기둥 높이
INNER_BASE = 55             # 파내는 원뿔 밑변 (지름)
LEFT_DX = 22.55
LEFT_DZ = 29.7
RIGHT_DX = 8.1
RIGHT_DZ = 8.4
LEFT_TAN = LEFT_DZ / LEFT_DX
RIGHT_TAN = RIGHT_DZ / RIGHT_DX

INNER_R = INNER_BASE / 2
INNER_APEX_X = INNER_R * (RIGHT_TAN - LEFT_TAN) / (LEFT_TAN + RIGHT_TAN)
INNER_H = LEFT_TAN * (INNER_APEX_X + INNER_R)

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    Cylinder(CYL_OUTER_D / 2, CYL_HEIGHT, align=ALIGN_BOTTOM)
    Cylinder(CYL_INNER_D / 2, CYL_HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 솔리드 원기둥
    with Locations((0, 0, CYL_HEIGHT)):
        Cylinder(CYL_OUTER_D / 2, SOLID_H, align=ALIGN_BOTTOM)
    # 내부 원뿔 파냄 (v3와 동일)
    with BuildSketch(Plane.XY.offset(CYL_HEIGHT)) as inner_base:
        Circle(INNER_R)
    inner_apex_plane = Plane(
        origin=(INNER_APEX_X, 0, CYL_HEIGHT + INNER_H),
        z_dir=(0, 0, 1),
    )
    with BuildSketch(inner_apex_plane) as inner_tip:
        Circle(0.01)
    loft([inner_base.sketch, inner_tip.sketch], mode=Mode.SUBTRACT)

# STL 내보내기
export_dir = Path(__file__).resolve().parent.parent.parent / "exports"
export_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
stl_path = export_dir / f"grinder_v4_{timestamp}.stl"
BRepMesh_IncrementalMesh(part.part.wrapped, 0.1)
writer = StlAPI_Writer()
writer.Write(part.part.wrapped, str(stl_path))
print(f"Exported: {stl_path}")

show(part, reset_camera=Camera.RESET)

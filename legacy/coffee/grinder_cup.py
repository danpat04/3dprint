"""그라인더 컵."""

from datetime import datetime
from pathlib import Path

from build123d import (
    Align, Axis, Box, BuildPart, BuildSketch, Circle, Cylinder, Locations,
    Mode, Plane, export_step, fillet, loft,
)
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from ocp_vscode import Camera, show

# 상수 (mm)
SIDE = 62           # 정사각형 한 변
HEIGHT = 60         # 높이
EDGE_R = 10         # 모서리 둥글기 반경
TOP_HOLE_D = 64     # 상단 원기둥 파냄 지름
TOP_HOLE_H = 1.1    # 상단 원기둥 파냄 깊이
FRUSTUM_TOP_D = 53    # 원뿔대 위쪽 지름
FRUSTUM_BOTTOM_D = 44 # 원뿔대 아래쪽 지름
FRUSTUM_DEPTH = 58    # 원뿔대 깊이
CORNER_HOLE_OFFSET = 5.5  # 모서리에서 안쪽 오프셋
CORNER_HOLE_D = 4.95      # 모서리 구멍 지름
CORNER_HOLE_DEPTH = 2     # 모서리 구멍 깊이

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    Box(SIDE, SIDE, HEIGHT, align=ALIGN_BOTTOM)
    # 수직(Z축 평행) 4개 edge만 필렛
    vertical_edges = part.edges().filter_by(Axis.Z)
    fillet(vertical_edges, radius=EDGE_R)
    # 상단 원기둥 파내기
    with Locations((0, 0, HEIGHT - TOP_HOLE_H)):
        Cylinder(TOP_HOLE_D / 2, TOP_HOLE_H, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 역방향 원뿔대 파내기 (위가 넓음)
    with BuildSketch(Plane.XY.offset(HEIGHT)) as frustum_top:
        Circle(FRUSTUM_TOP_D / 2)
    with BuildSketch(Plane.XY.offset(HEIGHT - FRUSTUM_DEPTH)) as frustum_bottom:
        Circle(FRUSTUM_BOTTOM_D / 2)
    loft([frustum_top.sketch, frustum_bottom.sketch], mode=Mode.SUBTRACT)
    # 4 모서리 구멍 (원래 사각 기둥 기준)
    corner_xy = SIDE / 2 - CORNER_HOLE_OFFSET
    with Locations(
        (corner_xy, corner_xy, HEIGHT - CORNER_HOLE_DEPTH),
        (-corner_xy, corner_xy, HEIGHT - CORNER_HOLE_DEPTH),
        (corner_xy, -corner_xy, HEIGHT - CORNER_HOLE_DEPTH),
        (-corner_xy, -corner_xy, HEIGHT - CORNER_HOLE_DEPTH),
    ):
        Cylinder(CORNER_HOLE_D / 2, CORNER_HOLE_DEPTH, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

# STL 내보내기
export_dir = Path(__file__).resolve().parent.parent.parent / "exports"
export_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
stl_path = export_dir / f"grinder_cup_{timestamp}.stl"
BRepMesh_IncrementalMesh(part.part.wrapped, 0.1)
writer = StlAPI_Writer()
writer.Write(part.part.wrapped, str(stl_path))
print(f"Exported: {stl_path}")

# STEP 내보내기
step_path = export_dir / f"grinder_cup_{timestamp}.step"
export_step(part.part, str(step_path))
print(f"Exported: {step_path}")

show(part, reset_camera=Camera.RESET)

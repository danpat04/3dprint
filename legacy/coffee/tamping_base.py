"""탬핑 베이스 - 4개의 기둥 + 가로 보."""

from datetime import datetime
from pathlib import Path

from build123d import Align, Box, BuildPart, GridLocations, Locations
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from ocp_vscode import Camera, show

# 치수 (mm)
PILLAR_W = 10   # 기둥 가로/세로
PILLAR_H = 55   # 기둥 높이
GAP_X = 70 + PILLAR_W  # 가로 간격 (안쪽 edge 간 70mm)
GAP_Y = 30 + PILLAR_W  # 세로 간격 (안쪽 edge 간 30mm)
BEAM_X_BOTTOM = 20.6  # 가로 보 하단 ~ 바닥
BEAM_Y_BOTTOM = 39    # 세로 보 하단 ~ 바닥
BEAM_H = PILLAR_W     # 보 높이 (= 10mm)
BEAM_W = PILLAR_W     # 보 두께 (= 10mm)

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    # 기둥 4개
    with GridLocations(GAP_X, GAP_Y, 2, 2):
        Box(PILLAR_W, PILLAR_W, PILLAR_H, align=ALIGN_BOTTOM)
    # 가로 보 2개 (X방향, 72mm 간격 기둥 연결)
    beam_x_len = GAP_X - PILLAR_W  # 기둥 안쪽 간 거리 = 72mm
    with Locations((0, GAP_Y / 2, BEAM_X_BOTTOM), (0, -GAP_Y / 2, BEAM_X_BOTTOM)):
        Box(beam_x_len, BEAM_W, BEAM_H, align=ALIGN_BOTTOM)
    # 가로 보 중앙 보강 기둥 2개 (보 하단까지만)
    with Locations((0, GAP_Y / 2, 0), (0, -GAP_Y / 2, 0)):
        Box(PILLAR_W, PILLAR_W, BEAM_X_BOTTOM, align=ALIGN_BOTTOM)
    # 세로 보 2개 (Y방향, 30mm 간격 기둥 연결)
    beam_y_len = GAP_Y - PILLAR_W  # 기둥 안쪽 간 거리 = 30mm
    with Locations((GAP_X / 2, 0, BEAM_Y_BOTTOM), (-GAP_X / 2, 0, BEAM_Y_BOTTOM)):
        Box(BEAM_W, beam_y_len, BEAM_H, align=ALIGN_BOTTOM)

# STL 내보내기
export_dir = Path(__file__).resolve().parent.parent.parent / "exports"
export_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
stl_path = export_dir / f"tamping_base_{timestamp}.stl"
BRepMesh_IncrementalMesh(part.part.wrapped, 0.1)
writer = StlAPI_Writer()
writer.Write(part.part.wrapped, str(stl_path))
print(f"Exported: {stl_path}")

show(part, reset_camera=Camera.RESET)

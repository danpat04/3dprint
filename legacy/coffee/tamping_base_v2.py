"""탬핑 베이스 v2 - 링 형태 + 노치."""

from datetime import datetime
from pathlib import Path

from build123d import Align, Box, BuildPart, Cylinder, Locations, Mode
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from ocp_vscode import Camera, show

# 상수 (mm)
INNER_D = 70.2          # 1. 실린더 내경 지름
WALL = 5                # 2. 실린더 벽 두께
NOTCH_S_GAP = 20.29     # 3. 아래 노치 간격 (직선 거리)
NOTCH_S_DEPTH = 28.5    # 4. 아래 노치 깊이
NOTCH_LR_GAP = 26.6     # 5. 좌우 노치 간격 (직선 거리)
NOTCH_LR_DEPTH = 6      # 6. 좌우 노치 깊이

# 계산값
INNER_R = INNER_D / 2
OUTER_R = INNER_R + WALL
HEIGHT = NOTCH_S_DEPTH + 1.5  # 아래 노치 깊이 + 바닥 잔여
ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    Cylinder(OUTER_R, HEIGHT, align=ALIGN_BOTTOM)
    Cylinder(INNER_R, HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

    # 아래(정남) 노치
    with Locations((0, 0, HEIGHT - NOTCH_S_DEPTH)):
        Box(NOTCH_S_GAP, OUTER_R + 1, NOTCH_S_DEPTH,
            align=(Align.CENTER, Align.MAX, Align.MIN), mode=Mode.SUBTRACT)

    # 좌우(정동/정서) 노치
    with Locations((0, 0, HEIGHT - NOTCH_LR_DEPTH)):
        Box(OUTER_R + 1, NOTCH_LR_GAP, NOTCH_LR_DEPTH,
            align=(Align.MIN, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        Box(OUTER_R + 1, NOTCH_LR_GAP, NOTCH_LR_DEPTH,
            align=(Align.MAX, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

# STL 내보내기
export_dir = Path(__file__).resolve().parent.parent.parent / "exports"
export_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
stl_path = export_dir / f"tamping_base_v2_{timestamp}.stl"
BRepMesh_IncrementalMesh(part.part.wrapped, 0.1)
writer = StlAPI_Writer()
writer.Write(part.part.wrapped, str(stl_path))
print(f"Exported: {stl_path}")

show(part, reset_camera=Camera.RESET)

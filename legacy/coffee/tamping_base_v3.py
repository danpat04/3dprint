"""탬핑 베이스 v3 - 링 형태 + 사선 노치."""

from datetime import datetime
from pathlib import Path

import math

from build123d import (
    Align, Box, BuildLine, BuildPart, BuildSketch, CenterArc, Cylinder,
    Line, Locations, Mode, Plane, extrude, make_face,
)
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from ocp_vscode import Camera, show

# 상수 (mm)
INNER_D = 70.2              # 1. 실린더 내경 지름
WALL = 5                    # 2. 실린더 벽 두께
NOTCH_S_GAP = 20.29         # 3. 아래 노치 간격 (직선 거리)
NOTCH_S_DEPTH = 28.5        # 4. 아래 노치 내경 깊이
NOTCH_S_OUTER_DEPTH = 38.5  # 5. 아래 노치 외경 깊이
NOTCH_LR_GAP = 26.6         # 6. 좌우 노치 간격 (직선 거리)
NOTCH_LR_DEPTH = 6          # 7. 좌우 노치 깊이
CHAMFER = 1.5               # 8. 노치 모서리 챔퍼

# 계산값
INNER_R = INNER_D / 2
OUTER_R = INNER_R + WALL
HEIGHT = 40
ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    Cylinder(OUTER_R, HEIGHT, align=ALIGN_BOTTOM)
    Cylinder(INNER_R, HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

    # 아래(정남) 노치 — 내경/외경 깊이가 다른 사선 바닥
    notch_inner_z = HEIGHT - NOTCH_S_DEPTH        # 내경 쪽 바닥 z
    notch_outer_z = HEIGHT - NOTCH_S_OUTER_DEPTH   # 외경 쪽 바닥 z
    with BuildSketch(Plane.YZ):
        with BuildLine():
            # 위에서 본 단면 프로파일 (y, z)
            Line((0, HEIGHT), (-(OUTER_R + 1), HEIGHT))
            Line((-(OUTER_R + 1), HEIGHT), (-(OUTER_R + 1), notch_outer_z))
            Line((-(OUTER_R + 1), notch_outer_z), (-OUTER_R, notch_outer_z))
            Line((-OUTER_R, notch_outer_z), (-INNER_R, notch_inner_z))  # 사선
            Line((-INNER_R, notch_inner_z), (0, notch_inner_z))
            Line((0, notch_inner_z), (0, HEIGHT))
        make_face()
    extrude(amount=NOTCH_S_GAP / 2, both=True, mode=Mode.SUBTRACT)

    # 아래 노치 상단 모서리 45도 챔퍼
    half_gap_s = NOTCH_S_GAP / 2
    # 왼쪽 모서리 (x = -half_gap_s) — 바깥쪽으로 깎음
    with BuildSketch(Plane.XZ):
        with BuildLine():
            Line((-half_gap_s, HEIGHT), (-half_gap_s - CHAMFER, HEIGHT))
            Line((-half_gap_s - CHAMFER, HEIGHT), (-half_gap_s, HEIGHT - CHAMFER))
            Line((-half_gap_s, HEIGHT - CHAMFER), (-half_gap_s, HEIGHT))
        make_face()
    extrude(amount=OUTER_R + 1, mode=Mode.SUBTRACT)
    # 오른쪽 모서리 (x = +half_gap_s) — 바깥쪽으로 깎음
    with BuildSketch(Plane.XZ):
        with BuildLine():
            Line((half_gap_s, HEIGHT), (half_gap_s + CHAMFER, HEIGHT))
            Line((half_gap_s + CHAMFER, HEIGHT), (half_gap_s, HEIGHT - CHAMFER))
            Line((half_gap_s, HEIGHT - CHAMFER), (half_gap_s, HEIGHT))
        make_face()
    extrude(amount=OUTER_R + 1, mode=Mode.SUBTRACT)

    # B 영역 보강: 노치 부분의 내경 안쪽 초승달 영역을 채움
    half_gap = NOTCH_S_GAP / 2
    y_int = -math.sqrt(INNER_R**2 - half_gap**2)  # 직선 절단면과 내경 원의 교점 y
    angle_right = math.degrees(math.atan2(y_int, half_gap)) % 360
    angle_left = math.degrees(math.atan2(y_int, -half_gap)) % 360
    arc_span = angle_left - angle_right  # 시계 방향 (음수)
    with BuildSketch(Plane.XY):
        with BuildLine():
            CenterArc((0, 0), INNER_R, angle_right, arc_span)
            Line((-half_gap, y_int), (half_gap, y_int))
        make_face()
    extrude(amount=notch_inner_z)

    # 좌우(정동/정서) 노치
    with Locations((0, 0, HEIGHT - NOTCH_LR_DEPTH)):
        Box(OUTER_R + 1, NOTCH_LR_GAP, NOTCH_LR_DEPTH,
            align=(Align.MIN, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        Box(OUTER_R + 1, NOTCH_LR_GAP, NOTCH_LR_DEPTH,
            align=(Align.MAX, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    # 좌우 노치 상단 모서리 45도 챔퍼 (3mm)
    half_gap_lr = NOTCH_LR_GAP / 2
    # 앞쪽 모서리 (y = +half_gap_lr) — 바깥쪽으로 깎음
    with BuildSketch(Plane.YZ):
        with BuildLine():
            Line((half_gap_lr, HEIGHT), (half_gap_lr + CHAMFER, HEIGHT))
            Line((half_gap_lr + CHAMFER, HEIGHT), (half_gap_lr, HEIGHT - CHAMFER))
            Line((half_gap_lr, HEIGHT - CHAMFER), (half_gap_lr, HEIGHT))
        make_face()
    extrude(amount=OUTER_R + 1, both=True, mode=Mode.SUBTRACT)
    # 뒤쪽 모서리 (y = -half_gap_lr) — 바깥쪽으로 깎음
    with BuildSketch(Plane.YZ):
        with BuildLine():
            Line((-half_gap_lr, HEIGHT), (-half_gap_lr - CHAMFER, HEIGHT))
            Line((-half_gap_lr - CHAMFER, HEIGHT), (-half_gap_lr, HEIGHT - CHAMFER))
            Line((-half_gap_lr, HEIGHT - CHAMFER), (-half_gap_lr, HEIGHT))
        make_face()
    extrude(amount=OUTER_R + 1, both=True, mode=Mode.SUBTRACT)

# STL 내보내기
export_dir = Path(__file__).resolve().parent.parent.parent / "exports"
export_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
stl_path = export_dir / f"tamping_base_v3_{timestamp}.stl"
BRepMesh_IncrementalMesh(part.part.wrapped, 0.1)
writer = StlAPI_Writer()
writer.Write(part.part.wrapped, str(stl_path))
print(f"Exported: {stl_path}")

show(part, reset_camera=Camera.RESET)

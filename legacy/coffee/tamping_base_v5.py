"""탬핑 베이스 v5."""

from datetime import datetime
from pathlib import Path

import math

from build123d import (
    Align, Box, BuildLine, BuildPart, BuildSketch, CenterArc, Cylinder,
    Line, Locations, Mode, Plane, export_step, extrude, make_face,
)
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from ocp_vscode import Camera, show

# 상수 (mm)
INNER_D = 70.2              # 1. 실린더 내경 지름
WALL = 5                    # 2. 실린더 벽 두께
NOTCH_S_GAP = 21.29         # 3. 아래 노치 간격 (직선 거리)
NOTCH_S_DEPTH = 28.5        # 4. 아래 노치 내경 깊이
NOTCH_S_OUTER_DEPTH = 37.5  # 5. 아래 노치 외경 깊이
NOTCH_LR_GAP = 27.6         # 6. 좌우 노치 간격 (직선 거리)
NOTCH_LR_DEPTH = 6          # 7. 좌우 노치 깊이
CHAMFER = 1.5               # 8. 노치 모서리 챔퍼
OUTER_SHELL_D = 100         # 9. 외부 실린더 외경 지름
OUTER_SHELL_WALL = 2        # 10. 외부 실린더 벽 두께
OUTER_SHELL_H = 90          # 11. 외부 실린더 높이
STRUT_BASE = 5              # 12. 결속 기둥 삼각형 밑변
SHELL_NOTCH_S_DEPTH = 35.5  # 13. 외부 실린더 아래 노치 깊이

# 계산값
INNER_R = INNER_D / 2
OUTER_R = INNER_R + WALL
HEIGHT = 80
ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

SHELL_OUTER_R = OUTER_SHELL_D / 2
SHELL_INNER_R = SHELL_OUTER_R - OUTER_SHELL_WALL

with BuildPart() as part:
    # 외부 실린더 (감싸는 껍질)
    Cylinder(SHELL_OUTER_R, OUTER_SHELL_H, align=ALIGN_BOTTOM)
    Cylinder(SHELL_INNER_R, OUTER_SHELL_H, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 내부 실린더
    Cylinder(OUTER_R, HEIGHT, align=ALIGN_BOTTOM)
    Cylinder(INNER_R, HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

    # 외부 실린더 아래(정남) 노치
    with Locations((0, 0, OUTER_SHELL_H - SHELL_NOTCH_S_DEPTH)):
        Box(NOTCH_S_GAP, SHELL_OUTER_R + 1, SHELL_NOTCH_S_DEPTH,
            align=(Align.CENTER, Align.MAX, Align.MIN), mode=Mode.SUBTRACT)
    # 외부 노치 바닥 반원형 파냄
    shell_notch_bottom_z = OUTER_SHELL_H - SHELL_NOTCH_S_DEPTH
    semi_r = NOTCH_S_GAP / 2
    with BuildSketch(Plane.XZ.offset(SHELL_INNER_R - 3)):
        with BuildLine():
            Line((-semi_r, shell_notch_bottom_z), (semi_r, shell_notch_bottom_z))
            CenterArc((0, shell_notch_bottom_z), semi_r, 0, -180)
        make_face()
    extrude(amount=OUTER_SHELL_WALL + 5, mode=Mode.SUBTRACT)
    # 외부 노치 상단 모서리 45도 챔퍼
    half_gap_shell = NOTCH_S_GAP / 2
    with BuildSketch(Plane.XZ):
        with BuildLine():
            Line((-half_gap_shell, OUTER_SHELL_H), (-half_gap_shell - CHAMFER, OUTER_SHELL_H))
            Line((-half_gap_shell - CHAMFER, OUTER_SHELL_H), (-half_gap_shell, OUTER_SHELL_H - CHAMFER))
            Line((-half_gap_shell, OUTER_SHELL_H - CHAMFER), (-half_gap_shell, OUTER_SHELL_H))
        make_face()
    extrude(amount=SHELL_OUTER_R + 1, mode=Mode.SUBTRACT)
    with BuildSketch(Plane.XZ):
        with BuildLine():
            Line((half_gap_shell, OUTER_SHELL_H), (half_gap_shell + CHAMFER, OUTER_SHELL_H))
            Line((half_gap_shell + CHAMFER, OUTER_SHELL_H), (half_gap_shell, OUTER_SHELL_H - CHAMFER))
            Line((half_gap_shell, OUTER_SHELL_H - CHAMFER), (half_gap_shell, OUTER_SHELL_H))
        make_face()
    extrude(amount=SHELL_OUTER_R + 1, mode=Mode.SUBTRACT)

    # 내부 실린더 아래(정남) 노치 — 내경/외경 깊이가 다른 사선 바닥
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

    # X자 결속 기둥 (내부-외부 실린더 연결, 정삼각형 단면)
    strut_length = SHELL_INNER_R - OUTER_R
    tri_h = STRUT_BASE * math.sqrt(3) / 2
    for angle in [45, 135, 225, 315]:
        rad = math.radians(angle)
        origin = (OUTER_R * math.cos(rad), OUTER_R * math.sin(rad), 0)
        z_dir = (math.cos(rad), math.sin(rad), 0)  # 방사 방향
        x_dir = (0, 0, 1)  # 위 방향
        plane = Plane(origin=origin, z_dir=z_dir, x_dir=x_dir)
        with BuildSketch(plane):
            with BuildLine():
                Line((0, -STRUT_BASE / 2), (0, STRUT_BASE / 2))
                Line((0, STRUT_BASE / 2), (tri_h, 0))
                Line((tri_h, 0), (0, -STRUT_BASE / 2))
            make_face()
        extrude(amount=strut_length)

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
stl_path = export_dir / f"tamping_base_v5_{timestamp}.stl"
BRepMesh_IncrementalMesh(part.part.wrapped, 0.1)
writer = StlAPI_Writer()
writer.Write(part.part.wrapped, str(stl_path))
print(f"Exported: {stl_path}")

step_path = export_dir / f"tamping_base_v5_{timestamp}.step"
export_step(part.part, str(step_path))
print(f"Exported: {step_path}")

show(part, reset_camera=Camera.RESET)

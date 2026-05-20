"""계단형 내경이 있는 원통 (삼각형 물결 계단)."""

import math
from datetime import datetime
from pathlib import Path

from build123d import (
    Align, BuildLine, BuildPart, BuildSketch, CenterArc, Cylinder,
    Line, Locations, Mode, Plane, loft, make_face,
)
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from ocp_vscode import Camera, show

# 치수 (mm)
HEIGHT = 60
OUTER_R = 40          # 외경 80mm / 2
FIRST_BORE_R = 35     # 첫번째 내경 70mm / 2
SECOND_BORE_R = 29.25 # 두번째 내경 58.5mm / 2
STEP_HEIGHT = 10      # 산 꼭대기 ~ 원통 상단
BOTTOM = 10           # 바닥 두께
WAVE_HEIGHT = 10      # 산 높이 (꼭대기 - 골짜기)
N_WAVES = 10          # 산 개수

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)
WAVE_BASE_Z = HEIGHT - STEP_HEIGHT - WAVE_HEIGHT  # 골짜기 높이
WAVE_ANGLE = 360 / N_WAVES  # 산 하나당 각도 (36°)


def annular_sector_sketch(plane, inner_r, outer_r, start_angle, angle_span):
    """내경~외경 사이의 부채꼴 스케치를 생성한다."""
    a_start_rad = math.radians(start_angle)
    a_end_rad = math.radians(start_angle + angle_span)
    with BuildSketch(plane) as sk:
        with BuildLine():
            CenterArc((0, 0), inner_r, start_angle, angle_span)
            Line(
                (inner_r * math.cos(a_end_rad), inner_r * math.sin(a_end_rad)),
                (outer_r * math.cos(a_end_rad), outer_r * math.sin(a_end_rad)),
            )
            CenterArc((0, 0), outer_r, start_angle + angle_span, -angle_span)
            Line(
                (outer_r * math.cos(a_start_rad), outer_r * math.sin(a_start_rad)),
                (inner_r * math.cos(a_start_rad), inner_r * math.sin(a_start_rad)),
            )
        make_face()
    return sk


with BuildPart() as part:
    # 외부 원통
    Cylinder(OUTER_R, HEIGHT, align=ALIGN_BOTTOM)
    # 첫번째 내경 — 골짜기까지 확장
    with Locations((0, 0, WAVE_BASE_Z)):
        Cylinder(FIRST_BORE_R, HEIGHT - WAVE_BASE_Z, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 두번째 내경
    with Locations((0, 0, BOTTOM)):
        Cylinder(SECOND_BORE_R, WAVE_BASE_Z - BOTTOM, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

    # 삼각형 산 10개: 각 산을 loft로 생성
    for i in range(N_WAVES):
        peak_angle = i * WAVE_ANGLE
        base_start = peak_angle - WAVE_ANGLE / 2

        # 바닥면: 36° 부채꼴 (골짜기 높이)
        bottom = annular_sector_sketch(
            Plane.XY.offset(WAVE_BASE_Z),
            SECOND_BORE_R, FIRST_BORE_R, base_start, WAVE_ANGLE,
        )
        # 꼭대기면: 1° 얇은 부채꼴 (산 꼭대기 높이)
        top = annular_sector_sketch(
            Plane.XY.offset(WAVE_BASE_Z + WAVE_HEIGHT),
            SECOND_BORE_R, FIRST_BORE_R, peak_angle - 0.5, 1.0,
        )
        loft([bottom.sketch, top.sketch], ruled=True)

# STL 내보내기
export_dir = Path(__file__).resolve().parent.parent / "exports"
export_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
stl_path = export_dir / f"stepped_cylinder_{timestamp}.stl"
BRepMesh_IncrementalMesh(part.part.wrapped, 0.1)
writer = StlAPI_Writer()
writer.Write(part.part.wrapped, str(stl_path))
print(f"Exported: {stl_path}")

show(part, reset_camera=Camera.RESET)

"""퍽 스크린 홀더 - 핸들."""

from datetime import datetime
from pathlib import Path

from build123d import (
    Align, Box, BuildLine, BuildPart, BuildSketch, Line, Location, Locations, Mode,
    Plane, Spline, extrude, make_face,
)
from ocp_vscode import Camera, show

GRIP_X = 7
GRIP_Y = 7
GRIP_H = 4
PILLAR_X = 7
PILLAR_Y = 3
PILLAR_H = 16
TOTAL_H = GRIP_H + PILLAR_H  # 20

# YZ 단면 주요 좌표
# 평평한면(flat side): +Y 쪽 — 전체 높이 직선
# 곡선면: -Y 쪽 — 단차를 부드럽게 잇는 곡선
FLAT_SIDE_Y = GRIP_Y / 2          # +3.5 (평평한면 위치)
GRIP_CURVE_Y = -GRIP_Y / 2        # -3.5 (GRIP 곡선면 끝)
PILLAR_CURVE_Y = FLAT_SIDE_Y - PILLAR_Y  # 0.5 (PILLAR 곡선면 끝)

# 곡선 전이 영역 — Z 방향 시작/끝 위치 직접 지정
CURVE_Z_BOTTOM = 4
CURVE_Z_TOP = 12

# 아래쪽에서 파는 사각 기둥 구멍 (handle_pin 4x4 핀이 끼워질 자리)
TIGHT_TOL = 0.1  # 빡빡한 공차
HOLE_BASE = 4
HOLE_SIZE = HOLE_BASE + 2 * TIGHT_TOL  # 4.2
HOLE_GAP_FROM_FLAT = 3  # flat side에서 구멍 중심까지
HOLE_DEPTH = 7

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    with BuildSketch(Plane.YZ) as profile:
        with BuildLine():
            Line((GRIP_CURVE_Y, 0), (FLAT_SIDE_Y, 0))                # 바닥
            Line((FLAT_SIDE_Y, 0), (FLAT_SIDE_Y, TOTAL_H))           # 평평한면 (전체 높이)
            Line((FLAT_SIDE_Y, TOTAL_H), (PILLAR_CURVE_Y, TOTAL_H))  # 윗면
            Line((PILLAR_CURVE_Y, TOTAL_H), (PILLAR_CURVE_Y, CURVE_Z_TOP))  # PILLAR 곡선면 (위 직선부)
            Spline(
                (PILLAR_CURVE_Y, CURVE_Z_TOP),
                (GRIP_CURVE_Y, CURVE_Z_BOTTOM),
                tangents=((0, -1), (0, -1)),
            )                                                         # 부드러운 곡선 전이
            if CURVE_Z_BOTTOM > 0:
                Line((GRIP_CURVE_Y, CURVE_Z_BOTTOM), (GRIP_CURVE_Y, 0))   # GRIP 곡선면 (아래 직선부)
        make_face()
    extrude(amount=GRIP_X / 2, both=True)
    # 아래에서 위로 4.2x4.2 구멍 (깊이 HOLE_DEPTH, flat side로부터 HOLE_GAP_FROM_FLAT 떨어진 위치)
    with Locations((0, FLAT_SIDE_Y - HOLE_GAP_FROM_FLAT, 0)):
        Box(HOLE_SIZE, HOLE_SIZE, HOLE_DEPTH, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

HANDLE_GAP = 2
HANDLE_OFFSET = (GRIP_X + HANDLE_GAP) / 2  # 4.5

result_left = Location((-HANDLE_OFFSET, 0, 0)) * part.part
result_right = Location((HANDLE_OFFSET, 0, 0)) * part.part
result = result_left

# STEP 내보내기
# export_dir = Path(__file__).resolve().parent.parent.parent.parent / "exports"
# export_dir.mkdir(exist_ok=True)
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# step_path = export_dir / f"puck_screen_holder_handle_{timestamp}.step"
# export_step(result, str(step_path))
# print(f"Exported: {step_path}")

show(result_left, result_right, reset_camera=Camera.RESET)

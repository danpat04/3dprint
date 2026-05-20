"""내부 공간을 벽이 둘러싸는 상자 (바닥만 두껍게)."""

from build123d import (
    Align, Box, BuildPart, BuildSketch, Cylinder, Locations, Mode, Plane,
    Rectangle, chamfer, loft,
)
from ocp_vscode import Camera, show

# 치수 (mm)
WALL = 1.5      # 측면·천장 벽 두께
BOTTOM = 11.5   # 바닥 두께
INNER_W = 60.5   # 폭
INNER_D = 107.5  # 깊이
INNER_H = 26     # 높이

OUTER_W = INNER_W + WALL * 2
OUTER_D = INNER_D + WALL * 2
OUTER_H = BOTTOM + INNER_H + WALL

# 바닥에 파낼 원기둥 4개 (열린 +X 면에서 -X 방향으로 수평으로 파들어감)
HOLE_R = 10.5 / 2
HOLE_DEPTH = 45
HOLE_GAP = 1
HOLE_PITCH = HOLE_R * 2 + HOLE_GAP  # 중심 간 거리
HOLE_Z = BOTTOM / 2                  # 바닥 두께 중앙
HOLE_YS = [-1.5 * HOLE_PITCH, -0.5 * HOLE_PITCH,
            0.5 * HOLE_PITCH,  1.5 * HOLE_PITCH]

# 양 옆에 추가로 파낼 작은 원기둥 2개 (바닥, 기존 원기둥 가장자리에서 약 20mm 간격)
SMALL_HOLE_R = 4.97 / 2
SMALL_HOLE_DEPTH = 5.1
SMALL_HOLE_EDGE_GAP = 20
SMALL_HOLE_Y = 1.5 * HOLE_PITCH + HOLE_R + SMALL_HOLE_EDGE_GAP + SMALL_HOLE_R
LID_SMALL_HOLE_DEPTH = 2.05  # 뚜껑 쪽 같은 위치의 원기둥 구멍 깊이

# 슬라이딩 뚜껑 레일 — 트인 +X 면에서 위/앞/뒤 벽을 바깥쪽(+X)으로 연장
LID_LIP = 2.5        # 립 돌출 (슬롯 1.2 + 처마 두께 1.3)
# 립 바깥 끝에서 안쪽으로 말아내는 처마 (ㄷ자 슬롯 완성)
LID_HOOK_DEPTH = 3   # 안쪽으로 말리는 깊이 (벽 1.5mm 포함)
LID_HOOK_T = 1.3     # 처마의 두께 (X 방향)
LID_TIP_X = OUTER_W / 2 + LID_LIP  # 립의 +X 끝

# 슬라이딩 뚜껑 (계단 단면) — 닿는 면마다 0.15mm 여유
LID_TOL = 0.15
# 안쪽 층 — X,Y 양쪽 벽과 닿음(각 면 0.15), Z는 위쪽만 닿음, 바닥은 열림
LID_INNER_W = (LID_LIP - LID_HOOK_T) - 2 * LID_TOL    # 0.9
LID_INNER_D = INNER_D - 2 * LID_TOL                    # 107.2
LID_INNER_H = (OUTER_H - WALL) - LID_TOL               # 37.35
# 바깥쪽 층 — Y 양쪽 처마와 닿음, Z 위쪽 처마와 닿음, X는 안쪽 층 연결+외부 노출이라 간섭 없음
# 안쪽 층이 -X로 0.15mm 물러난 만큼 더 차지해서 처마 바깥 면까지 닿음 (뚜껑 전체 X = 2.35mm)
LID_OUTER_W = LID_HOOK_T + LID_TOL                     # 1.45
LID_OUTER_D = (OUTER_D - 2 * LID_HOOK_DEPTH) - 2 * LID_TOL  # 104.2
LID_OUTER_H = (OUTER_H - LID_HOOK_DEPTH) - LID_TOL     # 35.85

with BuildPart() as part:
    # 외부 박스 — 바닥을 Z=0에 정렬
    Box(
        OUTER_W, OUTER_D, OUTER_H,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # 바깥쪽 직육면체의 12 모서리 중 +X 면 쪽 4개는 립/처마가 덮으니 제외
    box_half_w = OUTER_W / 2
    outer_edges = [
        e for e in part.edges()
        if abs(e.center().X - box_half_w) > 1e-3
    ]
    chamfer(outer_edges, length=0.5)
    # 내부 공간 — 바닥에서 BOTTOM만큼 올라간 지점부터
    with Locations((0, 0, BOTTOM)):
        Box(
            INNER_W, INNER_D, INNER_H,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )

    # 오른쪽 벽(+X)에서 내부 공간과 통하는 부분만 제거 — 앞/뒤/위 벽은 남김
    with Locations((OUTER_W / 2, 0, BOTTOM)):
        Box(
            WALL, INNER_D, INNER_H,
            align=(Align.MAX, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )

    # 열린 +X 면에서 바닥 두께 중앙을 따라 Y축으로 4개의 원기둥 구멍
    with Locations(Plane.YZ.offset(OUTER_W / 2)):
        with Locations(*[(y, HOLE_Z) for y in HOLE_YS]):
            Cylinder(
                HOLE_R, HOLE_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
                mode=Mode.SUBTRACT,
            )

    # 추가 작은 원기둥 2개 (양 옆)
    with Locations(Plane.YZ.offset(OUTER_W / 2)):
        with Locations(
            (-SMALL_HOLE_Y, HOLE_Z),
            (SMALL_HOLE_Y, HOLE_Z),
        ):
            Cylinder(
                SMALL_HOLE_R, SMALL_HOLE_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
                mode=Mode.SUBTRACT,
            )

    # 슬라이딩 뚜껑이 +X 방향으로 빠지지 않도록 위/앞/뒤 벽을 바깥쪽으로 연장
    # 위쪽 벽 연장
    with Locations((OUTER_W / 2, 0, OUTER_H)):
        Box(
            LID_LIP, OUTER_D, WALL,
            align=(Align.MIN, Align.CENTER, Align.MAX),
        )
    # 앞쪽 벽 연장
    with Locations((OUTER_W / 2, -OUTER_D / 2, 0)):
        Box(
            LID_LIP, WALL, OUTER_H,
            align=(Align.MIN, Align.MIN, Align.MIN),
        )
    # 뒤쪽 벽 연장
    with Locations((OUTER_W / 2, OUTER_D / 2, 0)):
        Box(
            LID_LIP, WALL, OUTER_H,
            align=(Align.MIN, Align.MAX, Align.MIN),
        )

    # 처마 — loft로 사선 처리 (립 연장면에서 바깥쪽으로 갈수록 안쪽으로 돌출 증가)
    hook_near_x = LID_TIP_X - LID_HOOK_T   # 32.95 (처마 시작, 립 내부 경계)
    hook_far_x = LID_TIP_X                  # 34.25 (처마 끝, 립 바깥 면)

    # 위쪽 처마
    with BuildSketch(Plane.YZ.offset(hook_near_x)) as top_near:
        with Locations((0, OUTER_H - WALL)):
            Rectangle(OUTER_D, WALL, align=(Align.CENTER, Align.MIN))
    with BuildSketch(Plane.YZ.offset(hook_far_x)) as top_far:
        with Locations((0, OUTER_H - LID_HOOK_DEPTH)):
            Rectangle(OUTER_D, LID_HOOK_DEPTH, align=(Align.CENTER, Align.MIN))
    loft([top_near.sketch, top_far.sketch])

    # 앞쪽 처마
    with BuildSketch(Plane.YZ.offset(hook_near_x)) as front_near:
        with Locations((-OUTER_D / 2, 0)):
            Rectangle(WALL, OUTER_H, align=(Align.MIN, Align.MIN))
    with BuildSketch(Plane.YZ.offset(hook_far_x)) as front_far:
        with Locations((-OUTER_D / 2, 0)):
            Rectangle(LID_HOOK_DEPTH, OUTER_H, align=(Align.MIN, Align.MIN))
    loft([front_near.sketch, front_far.sketch])

    # 뒤쪽 처마
    with BuildSketch(Plane.YZ.offset(hook_near_x)) as back_near:
        with Locations((OUTER_D / 2, 0)):
            Rectangle(WALL, OUTER_H, align=(Align.MAX, Align.MIN))
    with BuildSketch(Plane.YZ.offset(hook_far_x)) as back_far:
        with Locations((OUTER_D / 2, 0)):
            Rectangle(LID_HOOK_DEPTH, OUTER_H, align=(Align.MAX, Align.MIN))
    loft([back_near.sketch, back_far.sketch])

with BuildPart() as lid:
    # 안쪽 층 (슬롯에 끼워지는 부분) — 기존 벽에서 0.15mm 떨어져 시작
    inner_x_start = OUTER_W / 2 + LID_TOL
    with Locations((inner_x_start, 0, 0)):
        Box(
            LID_INNER_W, LID_INNER_D, LID_INNER_H,
            align=(Align.MIN, Align.CENTER, Align.MIN),
        )
    # 바깥쪽 층 — loft로 사선 처리 (안쪽 층 단면에서 바깥쪽 층 단면으로 부드럽게 줄어듦)
    slope_near_x = inner_x_start + LID_INNER_W   # 32.80 (안쪽 층 +X 끝)
    slope_far_x = slope_near_x + LID_OUTER_W     # 34.25 (뚜껑 +X 끝)
    with BuildSketch(Plane.YZ.offset(slope_near_x)) as lid_near:
        Rectangle(LID_INNER_D, LID_INNER_H, align=(Align.CENTER, Align.MIN))
    with BuildSketch(Plane.YZ.offset(slope_far_x)) as lid_far:
        Rectangle(LID_OUTER_D, LID_OUTER_H, align=(Align.CENTER, Align.MIN))
    loft([lid_near.sketch, lid_far.sketch])

    # 바닥 작은 원기둥과 같은 (Y, Z) 위치에 뚜껑 쪽으로도 구멍 (-X 면에서 +X로 2.05mm)
    # 안쪽에서 파들어가고 바깥쪽에는 0.3mm 벽이 남도록
    with Locations(Plane.YZ.offset(inner_x_start)):
        with Locations(
            (-SMALL_HOLE_Y, HOLE_Z),
            (SMALL_HOLE_Y, HOLE_Z),
        ):
            Cylinder(
                SMALL_HOLE_R, LID_SMALL_HOLE_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

show(part, lid, reset_camera=Camera.RESET)

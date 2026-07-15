"""feimaobuk_a2_cup — feimaobuk A2 그라인더용 컵.

그라인더에 모서리 나사 4개로 장착. 내부는 역원뿔대(위가 넓고 아래가 좁음)로
가루를 모아 배출한다. 외형은 필렛된 사각 블록.
(legacy/coffee/grinder_cup.py 이관 + 파라미터 정리)
"""

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    Locations,
    Mode,
    Plane,
    fillet,
    loft,
)

from models._lib.iter import finalize_iteration

# ---- 외형 (필렛된 사각 블록) ----
SIDE = 62.0        # 정사각형 한 변
HEIGHT = 60.0      # 높이
EDGE_R = 10.0      # 수직 모서리 둥글기 반경

# ---- 상단 얕은 리세스 (그라인더 접합면 안착) ----
TOP_HOLE_D = 64.0  # 상단 원형 리세스 지름
TOP_HOLE_H = 1.1   # 리세스 깊이

# ---- 내부 컵 (역원뿔대: 위 넓고 아래 좁음) ----
FRUSTUM_TOP_D = 53.0     # 위쪽 지름 (입구)
FRUSTUM_BOTTOM_D = 44.0  # 아래쪽 지름 (배출)
FRUSTUM_DEPTH = 58.0     # 깊이

# ---- 모서리 나사 구멍 (그라인더 장착) ----
CORNER_HOLE_OFFSET = 5.5  # 모서리에서 안쪽 오프셋
CORNER_HOLE_D = 4.95      # 지름
CORNER_HOLE_DEPTH = 2.0   # 깊이

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    Box(SIDE, SIDE, HEIGHT, align=ALIGN_BOTTOM)
    # 수직(Z축 평행) 모서리 4개만 필렛
    fillet(part.edges().filter_by(Axis.Z), radius=EDGE_R)

    # 상단 얕은 원형 리세스
    with Locations((0, 0, HEIGHT - TOP_HOLE_H)):
        Cylinder(TOP_HOLE_D / 2, TOP_HOLE_H, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

    # 내부 컵 — 역원뿔대 파냄 (위가 넓음)
    with BuildSketch(Plane.XY.offset(HEIGHT)) as frustum_top:
        Circle(FRUSTUM_TOP_D / 2)
    with BuildSketch(Plane.XY.offset(HEIGHT - FRUSTUM_DEPTH)) as frustum_bottom:
        Circle(FRUSTUM_BOTTOM_D / 2)
    loft([frustum_top.sketch, frustum_bottom.sketch], mode=Mode.SUBTRACT)

    # 모서리 나사 구멍 4개
    corner_xy = SIDE / 2 - CORNER_HOLE_OFFSET
    with Locations(
        (corner_xy, corner_xy, HEIGHT - CORNER_HOLE_DEPTH),
        (-corner_xy, corner_xy, HEIGHT - CORNER_HOLE_DEPTH),
        (corner_xy, -corner_xy, HEIGHT - CORNER_HOLE_DEPTH),
        (-corner_xy, -corner_xy, HEIGHT - CORNER_HOLE_DEPTH),
    ):
        Cylinder(CORNER_HOLE_D / 2, CORNER_HOLE_DEPTH, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

finalize_iteration(part.part)

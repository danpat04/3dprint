"""버블 이너 — bubble_tube 내벽에 맞는 플러그 (뒤집힌 형태)."""


from build123d import (
    Align, BuildPart, BuildSketch, Circle, Cylinder, Mode, Part, Plane, loft,
)
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut

# bubble_tube 내부 치수 (뒤집어서 사용)
# tube: 아래(80) → 허리(25) → 위(40), 직선구간 10mm
TUBE_BOTTOM_INNER_D = 80
TUBE_WAIST_INNER_D = 25
TUBE_TOP_INNER_D = 40
TUBE_HEIGHT = 200
TUBE_STRAIGHT_H = 10
TUBE_WAIST_Z = 100

# 뒤집힌 bubble_head 치수 (tube 위→head 아래, tube 아래→head 위)
HEAD_BOTTOM_R = TUBE_TOP_INNER_D / 2        # z=0: 20mm (tube 위쪽)
HEAD_WAIST_R = TUBE_WAIST_INNER_D / 2       # z=100: 12.5mm (tube 허리)
HEAD_TOP_R = TUBE_BOTTOM_INNER_D / 2        # z=190: 40mm (tube 아래쪽)
CURVED_H = TUBE_HEIGHT - TUBE_STRAIGHT_H    # 곡선부 높이 190mm
WAIST_Z = TUBE_HEIGHT - TUBE_WAIST_Z        # 허리 위치 100mm
STRAIGHT_H = TUBE_STRAIGHT_H                # 직선부 높이 10mm
WALL = 1                                     # 벽 두께
TOLERANCE = 0.2                              # 공차

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    # 곡선부 (z=0 ~ 190)
    with BuildSketch(Plane.XY.offset(0)) as sk_bottom:
        Circle(HEAD_BOTTOM_R - TOLERANCE)
    with BuildSketch(Plane.XY.offset(WAIST_Z)) as sk_waist:
        Circle(HEAD_WAIST_R - TOLERANCE)
    with BuildSketch(Plane.XY.offset(CURVED_H)) as sk_top:
        Circle(HEAD_TOP_R - TOLERANCE)
    loft([sk_bottom.sketch, sk_waist.sketch, sk_top.sketch])

    # 내부 파냄 — 곡선부 (외부보다 WALL만큼 작은 반지름)
    with BuildSketch(Plane.XY.offset(0)) as inner_bottom:
        Circle(HEAD_BOTTOM_R - WALL)
    with BuildSketch(Plane.XY.offset(WAIST_Z)) as inner_waist:
        Circle(HEAD_WAIST_R - WALL)
    with BuildSketch(Plane.XY.offset(CURVED_H)) as inner_top:
        Circle(HEAD_TOP_R - WALL)
    loft([inner_bottom.sketch, inner_waist.sketch, inner_top.sketch], mode=Mode.SUBTRACT)

    # 아래쪽 잘라내기 — 위쪽 50mm만 남김
    KEEP_H = 50
    CUT_Z = CURVED_H - KEEP_H
    Cylinder(50, CUT_Z, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

from build123d import Vector, Location
bb = part.part.bounding_box()
result = part.part.move(Location(Vector(0, 0, -bb.min.Z)))

# 바닥 ring 반지름 추출 (스플라인 edge → 둘레로 계산)
import math
bottom_edges = [e for e in result.edges() if abs(e.center().Z) < 0.01]
radii = sorted(e.length / (2 * math.pi) for e in bottom_edges)
RING_INNER_R = radii[0]
RING_OUTER_R = radii[-1]
print(f"Bottom ring: inner={RING_INNER_R:.2f}, outer={RING_OUTER_R:.2f}")

# 바닥에 맞는 실린더 (높이 20mm)
CYL_H = 20
FLARE_H = 5
FLARE_EXTRA = 2.5  # 내경 반지름 +2.5mm (지름 +5mm)
WALL_T = RING_OUTER_R - RING_INNER_R
FLARE_TOP_INNER_R = RING_INNER_R + FLARE_EXTRA
FLARE_TOP_OUTER_R = FLARE_TOP_INNER_R + WALL_T
with BuildPart() as cyl:
    Cylinder(RING_OUTER_R, CYL_H, align=ALIGN_BOTTOM)
    Cylinder(RING_INNER_R, CYL_H, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
    # 나팔 — 3단면 loft로 곡선 (z=CYL_H ~ CYL_H+FLARE_H)
    from build123d import Locations
    MID_Z = CYL_H + FLARE_H * 0.4
    MID_OUTER_R = RING_OUTER_R + FLARE_EXTRA * 0.1
    MID_INNER_R = RING_INNER_R + FLARE_EXTRA * 0.1
    with BuildSketch(Plane.XY.offset(CYL_H)) as fb:
        Circle(RING_OUTER_R)
    with BuildSketch(Plane.XY.offset(MID_Z)) as fm:
        Circle(MID_OUTER_R)
    with BuildSketch(Plane.XY.offset(CYL_H + FLARE_H)) as ft:
        Circle(FLARE_TOP_OUTER_R)
    loft([fb.sketch, fm.sketch, ft.sketch])
    with BuildSketch(Plane.XY.offset(CYL_H)) as ib:
        Circle(RING_INNER_R)
    with BuildSketch(Plane.XY.offset(MID_Z)) as im:
        Circle(MID_INNER_R)
    with BuildSketch(Plane.XY.offset(CYL_H + FLARE_H)) as it:
        Circle(FLARE_TOP_INNER_R)
    loft([ib.sketch, im.sketch, it.sketch], mode=Mode.SUBTRACT)
result = result.fuse(cyl.part)

# V → ㄷ: 실린더 바깥벽과 메인 바디 안쪽벽(cavity) 사이 V자의 아래쪽을 채워 바닥을 평평하게
FILL_H = 15

# 메인 바디 내부 cavity 볼륨 재생성 (안쪽 벽에 맞는 속 채운 solid)
with BuildPart() as cavity_part:
    with BuildSketch(Plane.XY.offset(0)) as cb:
        Circle(HEAD_BOTTOM_R - WALL)
    with BuildSketch(Plane.XY.offset(WAIST_Z)) as cw:
        Circle(HEAD_WAIST_R - WALL)
    with BuildSketch(Plane.XY.offset(CURVED_H)) as ct:
        Circle(HEAD_TOP_R - WALL)
    loft([cb.sketch, cw.sketch, ct.sketch])
    Cylinder(50, CUT_Z, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
cavity = cavity_part.part.move(Location(Vector(0, 0, -bb.min.Z)))

# 넉넉한 슬랩 (z=0 ~ FILL_H) → cavity와 교차 → 내부 볼륨만 남음
with BuildPart() as slab:
    Cylinder(100, FILL_H, align=ALIGN_BOTTOM)
slab_in_cavity = BRepAlgoAPI_Common(slab.part.wrapped, cavity.wrapped).Shape()

# 실린더 부분(r < RING_OUTER_R) 빼기 → 링 형태의 쐐기
with BuildPart() as inner_sub:
    Cylinder(RING_OUTER_R, FILL_H, align=ALIGN_BOTTOM)
ring_shape = BRepAlgoAPI_Cut(slab_in_cavity, inner_sub.part.wrapped).Shape()
ring = Part(ring_shape)
result = result.fuse(ring)

from models._lib.iter import finalize_iteration
finalize_iteration(part.part)

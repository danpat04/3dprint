"""tarp_magnet_holder / top — bottom 위에 씌우는 캡.

bottom 포켓 실린더(외경 Ø27.3) 위로 슬라이딩 결합.
  z=0..4.2   : 스커트 링 (내경 Ø27.4 = bottom 외경 + 0.1 공차, 외경 Ø29.4, 벽 1mm), 아래로 열림
  z=4.2..5.2 : 윗 디스크 Ø33.4 (외경 Ø29.4 에서 처마 2mm 돌출), 둘레 0.3 챔퍼
  +X 쪽 처마는 스커트 외경 접선(x=14.7)에서 직선 절단 → D 형, 그쪽 실린더 노출
"""

from build123d import Align, Axis, Box, BuildPart, Cylinder, GeomType, Locations, Mode, SortBy, chamfer

from models._lib.iter import finalize_iteration


ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

# bottom 인터페이스
BOTTOM_OUTER_D = 27.3            # bottom 포켓 실린더 외경
FIT_TOL = 0.1                    # 슬라이딩 결합 공차

# top 스커트
WALL = 1.0
INNER_D = BOTTOM_OUTER_D + FIT_TOL    # 27.4
OUTER_D = INNER_D + 2 * WALL          # 29.4
SKIRT_H = 4.2                    # bottom 포켓 벽 높이(4.2)와 동일 (벽 전체 덮음)

# top 디스크
EAVE = 2.0                       # 외경에서 처마 돌출
DISC_D = OUTER_D + 2 * EAVE      # 33.4
DISC_H = 1.0
EAVE_CHAMFER = 0.3               # 처마(디스크) 바깥 둘레 위·아래 모서리 챔퍼
FIT_CHAMFER = 0.5                # 결합 lead-in 챔퍼 (스커트 하단 안쪽 모서리)


def build_top():
    with BuildPart() as top:
        # 스커트 링 (z=0..4.2), 아래로 열림
        Cylinder(radius=OUTER_D / 2, height=SKIRT_H, align=ALIGN_BOTTOM)
        Cylinder(radius=INNER_D / 2, height=SKIRT_H, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        # 윗 디스크 (z=4.2..5.2)
        with Locations((0, 0, SKIRT_H)):
            Cylinder(radius=DISC_D / 2, height=DISC_H, align=ALIGN_BOTTOM)
        # 처마 바깥 둘레 위·아래 모서리 챔퍼 (반경 최대 원형 엣지 2개 = Ø33.4 위/아래)
        eave_perim = top.edges().filter_by(GeomType.CIRCLE).sort_by(SortBy.RADIUS)[-2:]
        chamfer(eave_perim, length=EAVE_CHAMFER)
        # 스커트 하단 안쪽 모서리 챔퍼 — bottom 벽 결합 lead-in (최하단 엣지 중 최소 반경)
        skirt_bottom_inner = top.edges().group_by(Axis.Z)[0].sort_by(SortBy.RADIUS)[0]
        chamfer(skirt_bottom_inner, length=FIT_CHAMFER)
        # 처마 한쪽(+X)을 스커트 외경 접선(x=Ø29.4/2=14.7)에서 직선 절단 → 그쪽 실린더 노출
        with Locations((OUTER_D / 2, 0, 0)):
            Box(50, 50, 50, align=(Align.MIN, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
    return top.part


if __name__ == "__main__":
    finalize_iteration(build_top())

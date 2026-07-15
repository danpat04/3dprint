"""tarp_magnet_holder / bottom — 자석 포켓 실린더 + 바닥 디스크.

Ø25 × 4.5 자석을 담는 케이스 하부. 디스크 안쪽을 0.5mm 파내 자석 아래 바닥을 0.5mm 로.
  z=0..0.5   : 자석 아래 floor (Ø25.3 영역, 두께 0.5)
  z=0..1.0   : 디스크 외곽 Ø38 (두께 1.0)
  z=0.5..5.2 : 자석 cavity Ø25.3 (높이 4.7 유지)
  z=1.0..5.2 : 포켓 벽 (외경 Ø27.3 / 내경 Ø25.3)
"""

from build123d import Align, Axis, BuildPart, Cylinder, Locations, Mode, SortBy, chamfer

from models._lib.iter import finalize_iteration


ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

# 자석
MAGNET_D = 25.0
MAGNET_H = 4.5

# 포켓 (자석 + 여유)
WALL = 1.0
INNER_D = 25.3                # 자석 Ø25 + 0.3 여유
OUTER_D = INNER_D + 2 * WALL  # 27.3
CAVITY_H = 4.7                # 내부 공간(자석 4.5 + 0.2 여유) — 유지

# 바닥 디스크
DISC_D = 38.0
DISC_H = 1.0                  # 디스크 외곽 두께
RECESS_DEPTH = 0.5            # 실린더 안쪽으로 디스크를 파낸 깊이 (자석 아래 floor 1.0→0.5)
POCKET_WALL_H = CAVITY_H - RECESS_DEPTH  # 4.2 — cavity 유지 위해 벽을 0.5 낮춤
FIT_CHAMFER = 0.5            # 결합 lead-in 챔퍼 (포켓 벽 상단 바깥 모서리)


TOTAL_H = DISC_H + POCKET_WALL_H  # 5.2 — 포켓 벽 상단 높이


def build_bottom():
    with BuildPart() as bottom:
        # 바닥 디스크 (z=0..1.0, Ø38)
        Cylinder(radius=DISC_D / 2, height=DISC_H, align=ALIGN_BOTTOM)
        # 포켓 벽 (z=1.0..5.2)
        with Locations((0, 0, DISC_H)):
            Cylinder(radius=OUTER_D / 2, height=POCKET_WALL_H, align=ALIGN_BOTTOM)
        # 자석 cavity: 디스크 안쪽 recess(0.5) + 벽 bore 를 합쳐 z=0.5..5.2 Ø25.3 제거
        with Locations((0, 0, DISC_H - RECESS_DEPTH)):
            Cylinder(radius=INNER_D / 2, height=CAVITY_H, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        # 포켓 벽 상단 바깥 모서리 챔퍼 — top 스커트 결합 lead-in (최상단 엣지 중 최대 반경)
        wall_top_outer = bottom.edges().group_by(Axis.Z)[-1].sort_by(SortBy.RADIUS)[-1]
        chamfer(wall_top_outer, length=FIT_CHAMFER)
    return bottom.part


if __name__ == "__main__":
    finalize_iteration(build_bottom())

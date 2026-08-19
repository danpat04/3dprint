"""modular_rack — 통(bin) 파트. build_bin(units, height) 로 폭/높이 가변.

몸통은 개구보다 BIN_CLR 작게, 상단 플랜지가 틀 앞/뒷벽 위에 얹힌다.
  - Y 플랜지: 벽 위로 4mm 나감 (하중 지지). 밑면 45° 챔퍼 → 서포트리스
  - X 플랜지: 몸통과 면일치 (이웃 통과 간섭 없음)
출력: 세워서 (플랜지 챔퍼 45° 라 서포트 불필요).
"""

from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Locations,
    Mode,
    Plane,
    Rectangle,
    extrude,
    loft,
)

from models._lib.iter import finalize_iteration
from models.camping.modular_rack.params import (
    BIN_BASE, BIN_CLR, BIN_WALL, FLANGE_D, FLANGE_T, GROOVE_D, GROOVE_W,
    RIB_W, UNIT,
)

CCMIN = (Align.CENTER, Align.CENTER, Align.MIN)


def build_bin(units: int = 1, height: float = 80.0):
    """units: 유닛 폭 (1~3), height: 몸통 전체 높이 (플랜지 포함, 바닥 z=0)."""
    bw = units * UNIT - BIN_CLR   # 몸통 X
    bd = UNIT - BIN_CLR           # 몸통 Y
    cham = (FLANGE_D - bd) / 2    # 플랜지 Y 돌출량 = 45° 챔퍼 높이
    z_ch = height - FLANGE_T - cham   # 챔퍼 시작 높이

    with BuildPart() as part:
        # 몸통
        Box(bw, bd, height, align=CCMIN)
        # 플랜지: 몸통 단면 → 플랜지 단면 45° 로프트 + 플랜지 판
        with BuildSketch(Plane.XY.offset(z_ch)) as s0:
            Rectangle(bw, bd)
        with BuildSketch(Plane.XY.offset(z_ch + cham)) as s1:
            Rectangle(bw, FLANGE_D)
        loft([s0.sketch, s1.sketch])
        with Locations((0, 0, z_ch + cham)):
            Box(bw, FLANGE_D, FLANGE_T, align=CCMIN)

        # 내부 파냄 (벽 BIN_WALL, 바닥 BIN_BASE)
        Box(bw - 2 * BIN_WALL, bd - 2 * BIN_WALL, height, align=CCMIN,
            mode=Mode.SUBTRACT)
        Box(bw - 2 * BIN_WALL, bd - 2 * BIN_WALL, BIN_BASE, align=CCMIN)

        # 70mm 경계마다 세로 홈 (틀 리브가 물림). 경계 = 모서리 포함.
        # 내부 경계는 홈(1.1)으로 벽이 얇아지므로 안쪽에 살 보강.
        boundaries = [(-units / 2 + i) * UNIT for i in range(units + 1)]
        inner_bs = boundaries[1:-1]
        thick = GROOVE_D  # 보강살 = 홈 깊이 → 유효 벽 두께 = BIN_WALL 유지
        for gx in inner_bs:
            for wall_y, inward in ((bd / 2 - BIN_WALL, -1),
                                   (-bd / 2 + BIN_WALL, 1)):
                with Locations((gx, wall_y + inward * thick / 2, BIN_BASE)):
                    Box(RIB_W + 4, thick, z_ch - BIN_BASE, align=CCMIN)
        for gx in boundaries:
            for wall_y in (bd / 2, -bd / 2):
                with Locations((gx, wall_y, 0)):
                    Box(GROOVE_W, 2 * GROOVE_D, z_ch, align=CCMIN,
                        mode=Mode.SUBTRACT)

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_bin(units=1, height=80.0))

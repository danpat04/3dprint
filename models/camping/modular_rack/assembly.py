"""modular_rack — 조립: 틀 + S후크 3개 + 통 데모 (2유닛 + 1유닛).

통 안착 높이: 통 플랜지 챔퍼(45°)가 틀 개구 챔퍼(45°)에 얹히는 지점.
EXPLODE > 0 이면 부품을 결합 위치에서 빼서 분해도로 렌더. 0 = 완전 조립.
"""

from build123d import Pos

from models._lib.iter import finalize_iteration
from models.camping.modular_rack.bin import build_bin
from models.camping.modular_rack.frame import build_frame
from models.camping.modular_rack.hook import build_hook
from models.camping.modular_rack.params import (
    BIN_CLR, FLANGE_D, FLANGE_T, FRAME_CH, FRAME_H, HOOK_XS, UNIT,
)

EXPLODE = 0.0   # 분해도 거리(mm). 0 = 완전 조립

# 데모 구성: (유닛 폭, 높이, 슬롯 중심 X) — 2유닛(슬롯1-2) + 1유닛(슬롯3)
BINS = ((2, 80.0, -UNIT / 2), (1, 110.0, UNIT))


def bin_seat_z(height: float) -> float:
    """통 로컬 z=0(바닥)이 놓일 조립 z — 챔퍼끼리 맞닿는 높이."""
    cham = (FLANGE_D - (UNIT - BIN_CLR)) / 2
    z_ch = height - FLANGE_T - cham
    return FRAME_H - FRAME_CH - z_ch - BIN_CLR / 2


def build_assembly():
    asm = build_frame()
    hook = build_hook()
    for sx in HOOK_XS:
        asm += Pos(sx, -EXPLODE * 0.35, EXPLODE) * hook
    for units, h, cx in BINS:
        asm += Pos(cx, 0, bin_seat_z(h) + EXPLODE * 2) * build_bin(units, h)
    return asm


if __name__ == "__main__":
    finalize_iteration(build_assembly())

"""modular_rack — 바스켓(수저통형 통). build_basket(units, height).

bin 의 외피(플랜지 챔퍼 + 경계 홈 + 보강살)를 그대로 쓰고,
cutlery_holder 에서 검증된 요소를 얹는다:
  - 4면 ±45° 그물망 (상단 톱니 마감 — 서포트리스)
  - 바닥: 원뿔 깔때기 + 중앙 배수 구멍 (유닛당 1개 — 경사각 유지)
  - 하단 솔리드 밴드 (작은 것 이탈 방지 + 물 튐 방지)

그물망은 유닛 셀 단위로 나눠서, 유닛 경계마다 8mm 솔리드 기둥이 남아
경계 홈(4.2)이 항상 솔리드 위에 온다. 출력: 세워서, 서포트리스.
"""

import math

from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    GridLocations,
    Locations,
    Mode,
    Plane,
    Rectangle,
    add,
    extrude,
    loft,
)

from models._lib.iter import finalize_iteration
from models.camping.modular_rack.bin import build_bin
from models.camping.modular_rack.params import (
    BIN_BASE, BIN_CLR, BIN_WALL, UNIT,
)

CCMIN = (Align.CENTER, Align.CENTER, Align.MIN)

# ---- 그물망 (cutlery_holder 검증값) ----
# 개구 가장자리는 격자 마디(9mm 배수)에 맞춰야 다이아가 꼭짓점에서 잘려
# 리브가 벽에 깔끔하게 붙는다 (어긋나면 벽과 격자 사이 빈 슬롯 발생).
MESH_RIB = 2.5
MESH_P = 18.0
MESH_OPEN = 54.0         # 셀당 개구 폭 (반폭 27 = 9의 배수) — 경계 기둥 16mm
BOT_BAND = 25.0          # 하단 솔리드 밴드 (바닥에서 그물 시작까지)
TOP_BAND = 9.0           # 상단 솔리드 밴드 → h_open 126 = 18의 배수

# ---- 깔때기 바닥 (cutlery_holder 검증값) ----
FLOOR_RISE = 6.0         # 깔때기 깊이 (가장자리가 목보다 높음)
DRAIN_D = 10.0           # 배수 구멍 지름
THROAT_R = DRAIN_D / 2 + 1.5


def mesh_face(plane, w_open, h_open, wall):
    """벽면 하나를 그물망으로 (개구 SUBTRACT + 대각 리브 ADD, 상단 45° 톱니).

    격자 위상: 그리드 개수를 홀수로 강제(중앙 정렬 0, ±18, …)하면
    개구 반폭/반높이가 9의 홀수배(27, 63)일 때 네 모서리가 정확히
    격자 마디에 떨어진다 — 가장자리 다이아는 꼭짓점에서 반으로 잘리고
    톱니 다이아(0, ±18)는 모서리를 침범하지 않는다.
    리브는 개구보다 4mm 넓게 남겨(INTERSECT 확대) 벽 속에 묻어 붙인다.
    (4mm = 벽 마진/기둥 안, 몸체 밖으로 안 나가는 한도)
    """
    ext = 4.0
    n = int((w_open + h_open) / MESH_P) + 3
    if n % 2 == 0:
        n += 1
    nt = int(w_open / MESH_P) + 2
    if nt % 2 == 0:
        nt += 1
    side = MESH_P / math.sqrt(2)
    # 리브 길이: hypot+2P 로는 세로로 긴 개구에서 위아래 끝까지 못 닿는다
    # (세로 도달 = 길이/2/√2 ≥ h_open/2 필요). 넉넉히 2배로.
    diag = math.hypot(w_open, h_open) * 2

    with BuildSketch(plane) as opening:
        Rectangle(w_open, h_open)
        with Locations((0, h_open / 2)):
            with GridLocations(MESH_P, MESH_P, nt, 1):
                Rectangle(side, side, rotation=45, mode=Mode.SUBTRACT)
    extrude(opening.sketch, amount=-(wall + 0.6), mode=Mode.SUBTRACT)

    with BuildSketch(plane) as net:
        with GridLocations(MESH_P, MESH_P, n, 1):
            Rectangle(MESH_RIB, diag, rotation=45)
        with GridLocations(MESH_P, MESH_P, n, 1):
            Rectangle(MESH_RIB, diag, rotation=-45)
        Rectangle(w_open + 2 * ext, h_open + 2 * ext, mode=Mode.INTERSECT)
        with Locations((0, h_open / 2)):
            with GridLocations(MESH_P, MESH_P, nt, 1):
                Rectangle(side, side, rotation=45, mode=Mode.SUBTRACT)
    extrude(net.sketch, amount=-wall, mode=Mode.ADD)


def build_basket(units: int = 1, height: float = 160.0):
    bw = units * UNIT - BIN_CLR
    bd = UNIT - BIN_CLR
    iw = bw - 2 * BIN_WALL   # 내부 폭
    idp = bd - 2 * BIN_WALL  # 내부 깊이
    h_open = height - BOT_BAND - TOP_BAND
    z_open = BOT_BAND + h_open / 2

    with BuildPart() as part:
        add(build_bin(units, height))

        # 깔때기 블록: 바닥 위에 FLOOR_RISE 만큼 채우고 셀별 원뿔 홈 + 배수 구멍
        with Locations((0, 0, BIN_BASE)):
            Box(iw, idp, FLOOR_RISE, align=CCMIN)
        cw = iw / units
        for i in range(units):
            cx = (i - (units - 1) / 2) * cw
            with BuildSketch(Plane.XY.offset(BIN_BASE)) as throat:
                with Locations((cx, 0)):
                    Circle(THROAT_R)
            with BuildSketch(Plane.XY.offset(BIN_BASE + FLOOR_RISE)) as brim:
                with Locations((cx, 0)):
                    Rectangle(cw, idp)
            loft([throat.sketch, brim.sketch], mode=Mode.SUBTRACT)
            with Locations((cx, 0, -2)):
                Cylinder(DRAIN_D / 2, BIN_BASE + FLOOR_RISE + 4, align=CCMIN,
                         mode=Mode.SUBTRACT)

        # 그물망: 앞/뒤는 유닛 셀마다, 좌/우는 한 면씩.
        # 로컬 세로축이 모두 world +Z 가 되도록 x_dir/z_dir 고정 (톱니 방향 통일)
        for i in range(units):
            mx = (i - (units - 1) / 2) * UNIT
            front = Plane(origin=(mx, bd / 2, z_open),
                          x_dir=(-1, 0, 0), z_dir=(0, 1, 0))
            back = Plane(origin=(mx, -bd / 2, z_open),
                         x_dir=(1, 0, 0), z_dir=(0, -1, 0))
            mesh_face(front, MESH_OPEN, h_open, BIN_WALL)
            mesh_face(back, MESH_OPEN, h_open, BIN_WALL)
        right = Plane(origin=(bw / 2, 0, z_open),
                      x_dir=(0, 1, 0), z_dir=(1, 0, 0))
        left = Plane(origin=(-bw / 2, 0, z_open),
                     x_dir=(0, -1, 0), z_dir=(-1, 0, 0))
        mesh_face(right, MESH_OPEN, h_open, BIN_WALL)
        mesh_face(left, MESH_OPEN, h_open, BIN_WALL)

    return part.part


if __name__ == "__main__":
    from build123d import Pos

    # 1유닛 + 2유닛 나란히 렌더 (조립 아님, 형상 확인용)
    demo = build_basket(1, 160.0) + Pos(120, 0, 0) * build_basket(2, 160.0)
    finalize_iteration(demo)

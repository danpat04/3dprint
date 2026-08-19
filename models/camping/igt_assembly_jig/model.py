"""igt_assembly_jig — IGT 테이블 철판 유닛 인양 지그.

폭 8.5mm 슬롯이 길게 뚫린 얇은 철판(t2)을 꺼낼 때, 슬롯에 비스듬히
걸어 넣어 테두리를 U자 틈에 물리고 두 다리를 한손에 쥐고 들어올린다.

형상 (refs/sketch_01.png):
  - 측면 U자: 다리 2개(벽 4mm) + 아래 U바닥, 안쪽 틈 3mm (철판 2 + 여유 1)
  - 넓은 다리: 위 70mm 구간 폭 25(그립), 아래 50mm 구간 7.5로 테이퍼.
    테이퍼는 한쪽 변만 — 반대 변(x=0)은 두 다리가 면일치(정렬)
  - 좁은 다리: 폭 7.5 일정 (슬롯 평평한 폭에 맞춤), 위 안쪽 45° 챔퍼
    → 틈 입구가 깔때기로 벌어져 철판 테두리 유도
  - 하중: 철판 테두리 → U바닥 윗면 → 다리 → 손

출력: 정렬된 변(x=0 면)을 bed 에 뉘여서 — 서포트리스, 레이어가
다리 길이 방향이라 인장에 강함.
"""

from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Locations,
    Mode,
    Plane,
    Polygon,
    extrude,
)

from models._lib.iter import finalize_iteration

# ---- 철판 실측 ----
SLOT_W = 8.5       # 철판 슬롯 폭
PLATE_T = 2.0      # 철판 두께

# ---- 지그 ----
H = 120.0          # 전체 높이
GRIP_H = 70.0      # 그립 구간 (위) → 테이퍼 구간 = H - GRIP_H = 50
W_GRIP = 25.0      # 넓은 다리 그립 폭
W_TIP = 7.5        # 아래끝/좁은 다리 폭 (슬롯 평평한 폭)
WALL = 4.0         # 다리/U바닥 두께 (강도)
GAP = PLATE_T + 1.0   # 3.0 안쪽 틈
CHAMFER = WALL     # 좁은 다리 위 안쪽 45° 챔퍼 (틈 입구 깔때기)

# Y 배치: 넓은 다리 0~4, 틈 4~7, 좁은 다리 7~11
Y_NARROW = WALL + GAP          # 7
Y_OUT = WALL + GAP + WALL      # 11 U바닥 바깥 두께
Z_TAPER = H - GRIP_H           # 50 테이퍼 상단

# ---- 누름 가이드 요철 (넓은 다리 바깥면, 그립 구간 가운데) ----
# 요철 2줄 사이 3mm 홈에 철판 테두리를 물려 위에서 찍어누르는 가이드
# + 뽑을 때 손가락 걸리는 그립. 정렬변(x=0) 쪽에 붙여 뉘여 출력 시 베드 접지.
RIB_L = 15.0       # 요철 길이 (X, 정렬변에서 시작)
RIB_T = 4.0        # 요철 두께 (Z)
RIB_P = 10.0       # 돌출 (−Y)
RIB_CH = 2.0       # 홈 입구 45° 챔퍼 (철판 유도)
Z_RIB_C = (Z_TAPER + H) / 2    # 85 그립 구간 가운데


def build_jig():
    with BuildPart() as part:
        # 넓은 다리: 정면(XZ) 프로파일 — x=0 변은 수직 정렬, 반대 변만 테이퍼
        with BuildSketch(Plane.XZ):
            Polygon(
                (0.0, 0.0),
                (W_TIP, 0.0),
                (W_GRIP, Z_TAPER),
                (W_GRIP, H),
                (0.0, H),
                align=None,
            )
        extrude(amount=-WALL)   # y 0~4

        # 좁은 다리 (폭 7.5 일정)
        with Locations((0, Y_NARROW, 0)):
            Box(W_TIP, WALL, H, align=(Align.MIN, Align.MIN, Align.MIN))

        # U바닥 (다리 연결, z 0~WALL)
        Box(W_TIP, Y_OUT, WALL, align=(Align.MIN, Align.MIN, Align.MIN))

        # 좁은 다리 위 안쪽 45° 챔퍼 — 틈 입구를 3→7mm 로 벌리는 깔때기
        with BuildSketch(Plane.YZ) as ch:
            Polygon(
                (Y_NARROW, H),
                (Y_NARROW, H - CHAMFER),
                (Y_NARROW + CHAMFER, H),
                align=None,
            )
        extrude(ch.sketch, amount=W_TIP, mode=Mode.SUBTRACT)

        # 누름 가이드 요철 2줄 (아래/위), 사이 홈 = GAP(3mm)
        z_lo = Z_RIB_C - GAP / 2 - RIB_T   # 79.5 아래 요철 하단
        z_hi = Z_RIB_C + GAP / 2           # 86.5 위 요철 하단
        for z0 in (z_lo, z_hi):
            with Locations((0, -RIB_P, z0)):
                Box(RIB_L, RIB_P, RIB_T,
                    align=(Align.MIN, Align.MIN, Align.MIN))
        # 홈 입구(요철 끝, y=-RIB_P) 45° 챔퍼 — 홈이 3→7mm 로 벌어짐
        with BuildSketch(Plane.YZ) as rch:
            Polygon(   # 아래 요철의 홈쪽 모서리
                (-RIB_P, z_lo + RIB_T),
                (-RIB_P + RIB_CH, z_lo + RIB_T),
                (-RIB_P, z_lo + RIB_T - RIB_CH),
                align=None,
            )
            Polygon(   # 위 요철의 홈쪽 모서리
                (-RIB_P, z_hi),
                (-RIB_P + RIB_CH, z_hi),
                (-RIB_P, z_hi + RIB_CH),
                align=None,
            )
        extrude(rch.sketch, amount=RIB_L, mode=Mode.SUBTRACT)

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_jig())

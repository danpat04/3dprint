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
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Locations,
    Mode,
    Plane,
    Polygon,
    chamfer,
    extrude,
    fillet,
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

# ---- D-핸들 (넓은 다리 바깥면 −Y, 그립 구간) ----
# 출력 테스트 결과 누름 요철은 그립에 도움 안 돼 제거(v2). 손가락 2~3개를
# 면과 바 사이 틈에 끼워 감아쥐는 세로 바 — 수직 인양에 유리.
# 정렬변(x=0)에 붙여 뉘여 출력 시 베드 접지 (서포트리스).
HDL_W = 15.0       # 핸들 폭 (X, 정렬변에서 시작)
HDL_GAP = 30.0     # 손가락 틈 (면 ↔ 바 안쪽) — 장갑 고려
HDL_BAR = 4.0      # 바 두께 (Y) — 하중은 스트럿으로 빠지는 전단이라 얇게
HDL_Z0 = 52.0      # 핸들 하단
HDL_Z1 = 118.0     # 핸들 상단
HDL_STRUT = 8.0    # 위아래 연결 스트럿 두께 → 창(손가락) 높이 50
HDL_R_IN = 6.0     # 창 안쪽 코너 필렛
HDL_R_OUT = 1.5    # 바 바깥 코너 필렛 (바 4mm 안에서)
HDL_CH = 1.5       # 창 안쪽 테두리 챔퍼 (손가락 닿는 모서리)


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

        # D-핸들: YZ 프로파일 C자 (스트럿 2 + 바) → X로 HDL_W 압출
        y_bar_in = -HDL_GAP                 # 바 안쪽면
        y_out = -(HDL_GAP + HDL_BAR)        # 바 바깥면
        with BuildSketch(Plane.YZ) as hp:
            outline = Polygon(
                (0.0, HDL_Z0),
                (y_out, HDL_Z0),
                (y_out, HDL_Z1),
                (0.0, HDL_Z1),
                (0.0, HDL_Z1 - HDL_STRUT),
                (y_bar_in, HDL_Z1 - HDL_STRUT),
                (y_bar_in, HDL_Z0 + HDL_STRUT),
                (0.0, HDL_Z0 + HDL_STRUT),
                align=None,
            )
            near = lambda v, t: abs(v - t) < 0.01
            vs = hp.vertices()
            fillet([v for v in vs if near(v.X, y_bar_in)
                    and v.Y in (HDL_Z0 + HDL_STRUT, HDL_Z1 - HDL_STRUT)],
                   HDL_R_IN)
            fillet([v for v in vs if near(v.X, y_out)], HDL_R_OUT)
        extrude(hp.sketch, amount=HDL_W)

        # 창 안쪽 테두리(손가락 닿는 모서리) 챔퍼 — x=0/15 양쪽 면의
        # 창 경계 에지 중 몸체(y=0) 접합부·바깥 프로파일 제외
        near = lambda v, t: abs(v - t) < 0.01
        win = [e for e in part.edges()
               if (near(e.center().X, 0.0) or near(e.center().X, HDL_W))
               and -(HDL_GAP + 1) < e.center().Y < -1.0
               and HDL_Z0 + 3 < e.center().Z < HDL_Z1 - 3]
        chamfer(win, HDL_CH)

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_jig())

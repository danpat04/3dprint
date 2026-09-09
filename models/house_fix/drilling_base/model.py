"""drilling_base — 나무 판재에 가이드 구멍을 뚫을 때 바닥을 보호하는 드릴 지그.

groove_spacer 설치용 판재(34 × 4.6 × 1259)에 나사 가이드 구멍을 집 안에서 뚫어야 한다.
드릴이 판재를 관통해 바닥(마루)을 상하게 하는 것을 막는 받침.

구조:
  바닥판 위에 기둥 2개, 기둥 상면의 홈(폭 35)에 판재를 얹고 기둥 사이 100mm
  구간에서 드릴링한다. 홈은 Y 전체를 관통해 판재를 위에서 떨어뜨려 넣거나
  길이 방향으로 밀어 넣을 수 있다.

  드릴이 바닥에 닿으려면 판재 4.6 + 공기층 24 + 바닥판 8 = 36.6mm 를 파야 한다.
  1차 방어선은 공기층(기둥 높이), 2차가 바닥판이다.

  홈 폭 35 = 판재 34 + 공차 1.0 (사용자 확정) — 1259mm 판재를 끌어가며
  여러 지점을 뚫으므로 헐거운 쪽이 편하다. 좌우 0.5mm 씩 유격.

출력: 바닥판을 bed 에 — 모든 살이 수직이고 홈은 위로 열려 있어 서포트리스.
"""

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Locations,
    Mode,
    chamfer,
)

from models._lib.iter import finalize_iteration

# ---- 판재 (groove_spacer 설치용) ----
BOARD_W = 34.0     # 판재 폭
BOARD_T = 4.6      # 판재 두께

# ---- 홈 ----
SLOT_W = BOARD_W + 1.0   # 35.0 — 쉬운 슬라이드 공차 (사용자 확정)
SLOT_D = 6.0             # 홈 깊이 (판재 4.6 이 잠기고 1.4 여유)

# ---- 기둥 ----
GAP = 100.0        # 기둥 사이 간격 = 드릴 작업 구간
PILLAR_X = 60.0    # 기둥 폭 (홈 35 + 벽 12.5 × 2)
PILLAR_Y = 40.0    # 기둥 깊이 — 판재를 안정적으로 받침
PILLAR_H = 30.0    # 기둥 높이 (바닥판 위)
CLEAR = PILLAR_H - SLOT_D    # 24.0 — 판재 아랫면 ↔ 바닥판 윗면 공기층

# ---- 바닥판 ----
BASE_X = 90.0                    # 폭 — 드릴이 판재 밖으로 빗나가도 받아냄
BASE_Y = PILLAR_Y * 2 + GAP      # 180.0
BASE_T = 8.0                     # 두께 (사용자 확정)

LEAD_CH = 1.0      # 홈 상단 챔퍼 — 판재를 위에서 떨어뜨려 넣을 때 유도

MIN3 = (Align.MIN, Align.MIN, Align.MIN)


def build_jig():
    with BuildPart() as part:
        # 바닥판 — 바닥 보호 겸 전체 베이스
        Box(BASE_X, BASE_Y, BASE_T, align=MIN3)

        # 기둥 2개 — 양 끝, 사이 간격 GAP
        px = (BASE_X - PILLAR_X) / 2
        for y0 in (0.0, BASE_Y - PILLAR_Y):
            with Locations((px, y0, BASE_T)):
                Box(PILLAR_X, PILLAR_Y, PILLAR_H, align=MIN3)

        # 판재 홈 — Y 전체 관통 (판재가 길이 방향으로 지나감)
        with Locations(((BASE_X - SLOT_W) / 2, 0.0, BASE_T + CLEAR)):
            Box(SLOT_W, BASE_Y, SLOT_D, align=MIN3, mode=Mode.SUBTRACT)

        # 홈 상단 모서리 챔퍼 — 판재 진입 유도
        top_z = BASE_T + PILLAR_H
        x0, x1 = (BASE_X - SLOT_W) / 2, (BASE_X + SLOT_W) / 2
        near = lambda v, t: abs(v - t) < 1e-6
        lead = [e for e in part.edges().filter_by(Axis.Y)
                if near(e.center().Z, top_z)
                and (near(e.center().X, x0) or near(e.center().X, x1))]
        chamfer(lead, LEAD_CH)

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_jig())

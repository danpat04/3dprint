"""igt_press_tool — IGT 철판 유닛 누름(안착) 도구.

길쭉한 철판(t2)을 프레임에 길이 방향으로 끼울 때 위에서 찍어눌러 앉힌다.
손바닥 패드 바닥에 요철 2줄이 누르는 방향(아래)으로 돌출 (v1 요철 계승):
  - 한 요철은 철판 슬롯(폭 8.5) 안으로, 다른 요철은 철판 표면 위에
  - 슬롯 가장자리가 요철 사이 3mm 홈에 물려 미끄러짐 방지
  - 누름 힘: 손바닥 → 패드 → 바깥 요철 바닥면 → 철판

사용자 스케치: refs/sketch_01.png (요철이 위로 보이게 뒤집어 그림)
출력: 패드 윗면을 bed 에 (뒤집어서) — 요철이 위로, 서포트리스.
"""

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Locations,
    chamfer,
)

from models._lib.iter import finalize_iteration

# ---- 철판 실측 ----
PLATE_T = 2.0
SLOT_W = 8.5       # 철판 슬롯 폭 (요철 4mm 가 안으로 들어감)

# ---- 패드 (손바닥 면적) ----
PAD_L = 85.0
PAD_W = 55.0
PAD_T = 8.0
PAD_CH = 2.0       # 패드 위 테두리 챔퍼

# ---- 요철 (v1 스펙 계승, 아래로 돌출) ----
# 긴 변(y=0) 가장자리에 붙임 — 옆으로 뉘여(세로) 출력 시 요철이 베드 접지,
# 레이어가 힘 방향과 나란해 강함 (jig 와 같은 출력 방향 전략)
RIB_L = 30.0           # 길이 (Y, 가장자리에서 안쪽으로) — 슬롯 길이 방향
RIB_T = 4.0            # 두께 (X)
RIB_P = 20.0           # 돌출 (아래)
GAP = PLATE_T + 1.0    # 3.0 요철 사이 홈 (슬롯 가장자리 물림)
RIB_CH = 2.0           # 홈(가운데) 쪽 끝 챔퍼만 — 홈 입구 3→7 (v1 과 동일)


def build_tool():
    with BuildPart() as part:
        # 패드 (요철 위에 얹힘, z: RIB_P ~ RIB_P+PAD_T)
        with Locations((0, 0, RIB_P)):
            Box(PAD_L, PAD_W, PAD_T, align=(Align.MIN, Align.MIN, Align.MIN))

        # 요철 2줄 (긴 변 y=0 가장자리, X 중앙, 아래로 z 0~RIB_P)
        gx0 = PAD_L / 2 - GAP / 2   # 홈 왼쪽 경계
        gx1 = PAD_L / 2 + GAP / 2   # 홈 오른쪽 경계
        for x0 in (gx0 - RIB_T, gx1):
            with Locations((x0, 0, 0)):
                Box(RIB_T, RIB_L, RIB_P,
                    align=(Align.MIN, Align.MIN, Align.MIN))

        # 홈 쪽 끝 챔퍼만 (v1 과 동일) — 홈 입구 3→7 벌어짐
        near = lambda v, t: abs(v - t) < 0.01
        gap_edges = [e for e in part.edges().filter_by(Axis.Y)
                     if near(e.center().Z, 0.0)
                     and (near(e.center().X, gx0) or near(e.center().X, gx1))]
        chamfer(gap_edges, RIB_CH)

        # 패드 위 테두리 챔퍼 (손바닥)
        top = part.edges().group_by(Axis.Z)[-1]
        chamfer(top, PAD_CH)

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_tool())

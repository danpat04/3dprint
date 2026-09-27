"""groove_spacer — 천장 홈(34 × 38 × 2519)을 4.6mm 나무판으로 메울 때 쓰는 스페이서 블록.

홈 안쪽에 나사로 고정하고 그 아래에 나무판을 덧대면 33.4 + 4.6 = 38 로 홈 깊이와 맞는다.
나사 1개가 나무판 → 블록 → 천장을 관통하므로 블록에는 Ø5 관통 구멍만 있으면 된다
(카운터싱크는 나무판 쪽 별도 가공).

구조 — H 단면을 전 높이로 압출한 상하 대칭 형상 (속찬 사각기둥 대비 약 62% 절감):
  - 양 측벽 3 × 24 (X=0, X=34) — 홈 벽에 닿아 폭 34 를 정의하고 블록 자세를 유지.
    나무판은 이 두 벽의 끝면에 양 끝으로 얹히므로 흔들리지 않는다 (면을 채울 필요 없음)
  - 중앙 보스 Ø12 — 나사 구멍 주위. 압축 하중은 나사 축 주변에 집중되므로 여기 살을 남긴다
  - 리브 4 두께 — 보스와 양 측벽을 이어 측벽 좌굴을 막음
  Y 방향(홈 길이 방향)은 홈이 구속하지 않으므로 벽을 두지 않는다.

  상하가 동일하므로 뒤집어 끼워도 상관없다.
  하중 경로: 나사 장력 → 나무판 → 측벽/리브/보스 끝면 → 천장.

챔퍼 0.5 — 폭 34 를 만드는 바깥 면(X=0, X=34)의 위아래 모서리 양쪽:
  - 홈에 밀어 넣을 때 진입 유도
  - 코끼리발(첫 레이어 퍼짐)이 폭 34 를 넘겨 안 들어가는 것을 방지

출력: 34 × 24 면을 bed 에 — 모든 살이 수직이라 서포트리스.
"""

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Cylinder,
    Locations,
    Mode,
    chamfer,
)

from models._lib.iter import finalize_iteration

# ---- 천장 홈 실측 ----
CH_W = 34.0        # 홈 폭 = 블록 폭 (공차 0 — bracket_base 에서 fit 확인)
CH_DEPTH = 38.0    # 홈 깊이
BOARD_T = 4.6      # 덮을 나무판 두께

# ---- 블록 외형 ----
D = 24.0                     # 깊이 (홈 길이 방향)
H = CH_DEPTH - BOARD_T       # 높이 33.4 — 나무판과 합쳐 홈 깊이와 일치
SCREW_D = 5.0                # 나사 구멍 지름 (정중앙 관통)
CHAMFER = 0.5                # 진입 유도 / 코끼리발 방지

# ---- 절감 구조 (H 단면, 전 높이 동일) ----
WALL_T = 3.0                 # 양 측벽 두께 — 폭 34 를 정의하는 면
BOSS_OD = 12.0               # 중앙 보스 외경 (Ø5 구멍 주위 살 3.5)
RIB_T = 4.0                  # 보스 ↔ 측벽 리브 두께

MIN3 = (Align.MIN, Align.MIN, Align.MIN)
_CTR_MIN = (Align.CENTER, Align.CENTER, Align.MIN)


def build_spacer():
    with BuildPart() as part:
        # 양 측벽 — 폭 34 를 정의하고 홈 벽에 닿아 자세를 잡는다
        for x0 in (0.0, CH_W - WALL_T):
            with Locations((x0, 0, 0)):
                Box(WALL_T, D, H, align=MIN3)

        cx, cy = CH_W / 2, D / 2

        # 중앙 보스 — 나사 축 주변 압축 살
        with Locations((cx, cy, 0)):
            Cylinder(BOSS_OD / 2, H, align=_CTR_MIN)

        # 리브 — 보스와 양 측벽을 이어 좌굴 방지
        with Locations((cx, cy, 0)):
            Box(CH_W - 2 * WALL_T, RIB_T, H, align=_CTR_MIN)

        # 나사 구멍: 정중앙 Ø5 관통 (나무판 → 블록 → 천장을 한 나사로)
        with Locations((cx, cy, -1)):
            Cylinder(SCREW_D / 2, H + 2, align=_CTR_MIN, mode=Mode.SUBTRACT)

        # 챔퍼 — 바깥 면(X=0, X=34)의 위아래 모서리, 상하 대칭
        near = lambda v, t: abs(v - t) < 1e-6
        outer = [e for e in part.edges().filter_by(Axis.Y)
                 if (near(e.center().Z, 0.0) or near(e.center().Z, H))
                 and (near(e.center().X, 0.0) or near(e.center().X, CH_W))]
        chamfer(outer, CHAMFER)

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_spacer())

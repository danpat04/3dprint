"""bracket_base — 천장 홈(34×34×2519)에 나사로 박는 브라켓 베이스.

가운데 보스에 금속 브라켓을 끼우고, 거기에 다시 판재를 끼워 홈을 메꾼다
(금속 브라켓/판재 인터페이스는 별도 — 여기선 베이스 형상만).
나사 구멍은 실물 확인 후 추가 예정. 폭 공차 없음 (34 그대로, 테스트 후 결정).

프로파일 (사용자 스케치 refs/sketch_01.png):
  - 바닥판 34(폭) × 24(깊이) × 2
  - 중앙 보스 24 × 24 × 12 (바닥 위)
  - 양옆 날개 2(두께) × 4(높이) — 보스와 날개 사이 3mm 틈 × 2

출력: 바닥판을 bed 에 그대로 — 서포트리스.
"""

from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Cylinder,
    Locations,
    Mode,
    Plane,
    Rectangle,
    loft,
)

from models._lib.iter import finalize_iteration

# ---- 천장 홈 실측 ----
CH_W = 34.0        # 홈 폭 = 베이스 폭 (공차 없음, 테스트 후 결정)

# ---- 베이스 ----
D = 24.0           # 깊이 (홈 길이 방향)
BASE_T = 2.0       # 바닥판 두께
BOSS_W = 24.0      # 중앙 보스 폭
BOSS_H = 12.0      # 보스 높이 (바닥 위)
WING_T = 2.0       # 날개 두께
WING_H = 4.0       # 날개 높이 (바닥 위)
# 파생: 보스↔날개 틈 = (34-24)/2 - 2 = 3mm

# ---- 금속 클립 포켓 (보스 상면에서 파냄, 사용자 피드백 치수) ----
# LED 프로파일용 스프링 클립이 위에서 눌러 들어가 테이퍼 벽에 걸림
PKT_TOP_W = 17.8   # 위 개구 폭 (X)
PKT_BOT_W = 14.5   # 바닥 폭 (X) — 아래로 좁아지는 테이퍼
PKT_D = 18.1       # 깊이 방향 (Y, 상하 동일)
PKT_DEPTH = 4.0    # 파내는 깊이 (사용자 확정)
SCREW_D = 5.0      # 나사 구멍 지름 — 포켓(=베이스) 정중앙 관통

MIN3 = (Align.MIN, Align.MIN, Align.MIN)


def build_base():
    with BuildPart() as part:
        Box(CH_W, D, BASE_T, align=MIN3)                      # 바닥판
        with Locations(((CH_W - BOSS_W) / 2, 0, BASE_T)):
            Box(BOSS_W, D, BOSS_H, align=MIN3)                # 중앙 보스
        for x0 in (0.0, CH_W - WING_T):
            with Locations((x0, 0, BASE_T)):
                Box(WING_T, D, WING_H, align=MIN3)            # 날개

        # 클립 포켓: 위 17.8 → 아래 14.5 테이퍼 (Y 18.1 고정), 보스 중앙
        cx, cy = CH_W / 2, D / 2
        z_top = BASE_T + BOSS_H
        with BuildSketch(Plane.XY.offset(z_top)) as top_sk:
            with Locations((cx, cy)):
                Rectangle(PKT_TOP_W, PKT_D)
        with BuildSketch(Plane.XY.offset(z_top - PKT_DEPTH)) as bot_sk:
            with Locations((cx, cy)):
                Rectangle(PKT_BOT_W, PKT_D)
        loft([bot_sk.sketch, top_sk.sketch], mode=Mode.SUBTRACT)

        # 나사 구멍: 정중앙 Ø5 관통 (포켓 바닥 → 바닥판)
        with Locations((cx, cy, -1)):
            Cylinder(SCREW_D / 2, z_top + 2,
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)
    return part.part


if __name__ == "__main__":
    finalize_iteration(build_base())

"""juice_pack_holder — 아이용 음료수팩 홀더 (통 + 깔때기 + 림).

아이가 사각 기둥형 음료수팩(단면 38×48, 높이 ~120)을 쥘 때
손힘으로 음료가 뿜어지는 걸 막기 위해 단단한 통에 넣어 쥔다.

구조 (아래→위):
- 통 본체: 내부 39×49, 깊이 60 (팩 단면 + 여유 1mm)
- 깔때기: 입구에서 위로 사방 5mm 벌어짐 (높이 12)
    · 팩 끼움 유도 / 흘러내린 음료 모음 / 손 거치
- 림: 깔때기 윗단을 짧게 수직으로 연장 (높이 5)
    · 날카로운 경사 끝 대신 평평한 입구를 만들고 라운딩

세로 코너는 RectangleRounded(R3)로 전 구간 일관 라운딩,
입구 가장자리는 fillet(R0.5)로 마감.
"""

from build123d import (
    Axis, BuildPart, BuildSketch, Plane, RectangleRounded, extrude, fillet, loft,
    Mode,
)

from models._lib.iter import finalize_iteration


# --- 스펙 ---
INNER_X = 39          # 팩 38 + 여유 1
INNER_Y = 49          # 팩 48 + 여유 1
INNER_H = 60          # 통 내부 깊이
WALL = 1.5            # 측벽 두께
FLOOR = 2.0           # 바닥 두께 (안정성)

OUTER_X = INNER_X + 2 * WALL   # 42
OUTER_Y = INNER_Y + 2 * WALL   # 52
BODY_H = FLOOR + INNER_H       # 62  (통 본체 전체 높이)

FLARE_OUT = 5.0       # 깔때기가 사방으로 벌어지는 양
FLARE_H = 12.0        # 깔때기 높이
RIM_H = 5.0           # 윗단 수직 림 높이

# 깔때기/림 윗단 단면
TOP_OUTER_X = OUTER_X + 2 * FLARE_OUT   # 52
TOP_OUTER_Y = OUTER_Y + 2 * FLARE_OUT   # 62
TOP_INNER_X = INNER_X + 2 * FLARE_OUT   # 49
TOP_INNER_Y = INNER_Y + 2 * FLARE_OUT   # 59

# 코너 반경 (외곽 / 내곽 — 벽 두께 일정 유지)
CR = 3.0              # 외곽 세로 코너 반경
ICR = CR - WALL       # 1.5  내곽 세로 코너 반경

FLARE_TOP_Z = BODY_H + FLARE_H          # 74  (깔때기 윗면)
TOTAL_H = FLARE_TOP_Z + RIM_H           # 79  (입구 면)
RIM_FILLET = 0.5      # 입구 가장자리 라운딩


with BuildPart() as part:
    # ===== 외형 =====
    # 통 본체 (z=0..BODY_H)
    with BuildSketch(Plane.XY):
        RectangleRounded(OUTER_X, OUTER_Y, CR)
    extrude(amount=BODY_H)

    # 깔때기 외벽 (BODY_H → FLARE_TOP_Z, 사방 +5 벌어짐)
    with BuildSketch(Plane.XY.offset(BODY_H)):
        RectangleRounded(OUTER_X, OUTER_Y, CR)
    with BuildSketch(Plane.XY.offset(FLARE_TOP_Z)):
        RectangleRounded(TOP_OUTER_X, TOP_OUTER_Y, CR)
    loft()

    # 윗단 수직 림 (FLARE_TOP_Z → TOTAL_H)
    with BuildSketch(Plane.XY.offset(FLARE_TOP_Z)):
        RectangleRounded(TOP_OUTER_X, TOP_OUTER_Y, CR)
    extrude(amount=RIM_H)

    # ===== 내부 파내기 =====
    # 통 내부 (z=FLOOR..BODY_H)
    with BuildSketch(Plane.XY.offset(FLOOR)):
        RectangleRounded(INNER_X, INNER_Y, ICR)
    extrude(amount=INNER_H, mode=Mode.SUBTRACT)

    # 깔때기 내부 (BODY_H → FLARE_TOP_Z)
    with BuildSketch(Plane.XY.offset(BODY_H)):
        RectangleRounded(INNER_X, INNER_Y, ICR)
    with BuildSketch(Plane.XY.offset(FLARE_TOP_Z)):
        RectangleRounded(TOP_INNER_X, TOP_INNER_Y, ICR)
    loft(mode=Mode.SUBTRACT)

    # 림 내부 (FLARE_TOP_Z → 위로 관통)
    with BuildSketch(Plane.XY.offset(FLARE_TOP_Z)):
        RectangleRounded(TOP_INNER_X, TOP_INNER_Y, ICR)
    extrude(amount=RIM_H + 1, mode=Mode.SUBTRACT)

    # ===== 입구 가장자리 라운딩 =====
    fillet(part.edges().group_by(Axis.Z)[-1], radius=RIM_FILLET)


finalize_iteration(part.part)

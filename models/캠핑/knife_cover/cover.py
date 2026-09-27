"""knife_cover / cover — 식칼 보호 시스(sheath).

좌표계:
  X = 칼 두께 방향 (slot 두께)
  Y = 칼 길이 방향 (handle 입구 → tip 끝)
  Z = 칼 높이 방향 (edge 아래 → spine 위)

구조: U 채널 + 한쪽 Y 끝 막음.
  닫힘: 칼끝 (Y 끝), 칼날쪽 바닥 (Z 바닥), 양 옆 (X 양면)
  Open: 손잡이쪽 (Y), 칼등쪽 위 (Z)

작동: edge 벽이 hinge 베이스, 양 X 벽이 cantilever 로 동작.
칼 (두께 2mm) 이 slot 1mm 에 들어가면 양 벽이 각 0.5mm 휘면서 grip.
PETG-HF 기준 strain ~0.1% 로 elastic 영역 내.
"""

from build123d import Align, Box, BuildPart, Locations, Mode, chamfer

from models._lib.iter import finalize_iteration


ALIGN_CENTERED = (Align.CENTER, Align.CENTER, Align.CENTER)

# ============================================================
# 칼 스펙
# ============================================================
KNIFE_LEN = 137
KNIFE_THICK = 2.0
KNIFE_HEIGHT = 34

# ============================================================
# Slot
# ============================================================
SLOT_X = 1.0                # relaxed slot 폭 (칼 두께 - 1.0 → 양벽 각 0.5mm flex)
SLOT_Y = KNIFE_LEN + 1.0    # 138mm — 칼끝 여유 1mm
SLOT_Z = KNIFE_HEIGHT + 1.0  # 35mm — 칼등 위 여유 1mm (cover wall 안쪽 기준)

# ============================================================
# 벽 두께
# ============================================================
WALL_SIDE = 1.5    # 양 X 면 — cantilever 두께
WALL_TIP = 2.0     # 칼끝 막는 Y 벽
WALL_EDGE = 2.0    # 칼날쪽 바닥 — cantilever hinge base

# ============================================================
# 외부 치수
# ============================================================
OUTER_X = SLOT_X + 2 * WALL_SIDE    # 4.0
OUTER_Y = SLOT_Y + WALL_TIP         # 140
OUTER_Z = WALL_EDGE + SLOT_Z        # 37 (spine open — 천장 벽 없음)


CHAMFER = 0.3           # 모든 외부 + slot edge 일괄 적용


def build_cover():
    with BuildPart() as cover:
        # 외부 박스 — Y=0 (handle open), Y=OUTER_Y (tip), Z=0 (edge), Z=OUTER_Z (spine open)
        with Locations((0, 0, 0)):
            Box(OUTER_X, OUTER_Y, OUTER_Z,
                align=(Align.CENTER, Align.MIN, Align.MIN))

        # Slot — handle (Y=0) + spine (Z=OUTER_Z) open, tip (Y=SLOT_Y) + edge (Z=WALL_EDGE) 닫힘
        # Z 상단을 OUTER_Z 너머로 +5 확장해 spine 완전히 open
        with Locations((0, 0, WALL_EDGE)):
            Box(SLOT_X, SLOT_Y, SLOT_Z + 5,
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT)

        # 챔퍼 — 모든 edge 에 적용 (외부 손맛 + slot lead-in)
        chamfer(cover.edges(), length=CHAMFER)

    return cover.part


if __name__ == "__main__":
    finalize_iteration(build_cover())

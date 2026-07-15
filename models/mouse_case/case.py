"""mouse_case 본체 — 무선 마우스 여행용 보관 케이스.

마우스를 넣어 가방에서 노출/파손되지 않게 감싸는 상자. 오른쪽이 열려 마우스를
밀어 넣고, cover 로 막는다. 안쪽 기둥/구멍은 cover 와 핀으로 결합.
(legacy/etc/mousecase_v4.py 이관)
"""

from build123d import (
    Align,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Cylinder,
    Locations,
    Mode,
    Plane,
    Polyline,
    extrude,
    make_face,
)

from models._lib.iter import finalize_iteration

# ---- 벽 두께 (mm) ----
WALL = 1.5            # 왼쪽/위/바닥 벽
WALL_FB = 2.6         # 앞/뒤 벽 (두꺼움)
WALL_FB_THIN = 1.5    # 오른쪽 돌출 부분의 앞/뒤 벽 (얇음)

# ---- 내부 치수 (mm, 고정) ----
INNER_W = 63.5
INNER_D = 107.5
INNER_H = 26.0

# ---- 외부 치수 (mm) ----
OUTER_W = 65.0                     # 폭 (X)
OUTER_D = INNER_D + 2 * WALL_FB    # 깊이 112.7 (내부 유지, 앞/뒤로 확장)
OUTER_H = 29.0                     # 높이 (Z)

# ---- 사다리꼴 기둥 (오른쪽 개구 가장자리) ----
PILLAR_BASE = 2.0
PILLAR_ORIG_H = 1.5
PILLAR_CUT = 0.3
PILLAR_H = PILLAR_ORIG_H - PILLAR_CUT                  # 1.2
PILLAR_TOP = PILLAR_BASE * PILLAR_CUT / PILLAR_ORIG_H  # 0.4
PILLAR_LEN = 29.0                                      # 기둥 Z 길이
PILLAR_X = OUTER_W / 2                                 # 32.5
PILLAR_Y_FRONT = -OUTER_D / 2 + WALL_FB_THIN           # -54.85
PILLAR_Y_BACK = OUTER_D / 2 - WALL_FB_THIN             # +54.85

# ---- 안쪽 사각 기둥 (cover 결합, 앞/뒤 동일) ----
INNER_PILLAR_W = 60.5
INNER_PILLAR_D = 10.0
INNER_PILLAR_H = 8.0
INNER_PILLAR_X_END = -OUTER_W / 2 + WALL + INNER_PILLAR_W            # 29.5
INNER_PILLAR_CY_FRONT = -OUTER_D / 2 + WALL_FB + INNER_PILLAR_D / 2  # -48.75
INNER_PILLAR_CY_BACK = OUTER_D / 2 - WALL_FB - INNER_PILLAR_D / 2    # +48.75
INNER_PILLAR_CZ = OUTER_H - WALL - INNER_PILLAR_H / 2                # 23.5

# ---- 안쪽 기둥 핀 구멍 (+X 방향) ----
INNER_HOLE_R = 4.97 / 2
INNER_HOLE_DEPTH = 5.2

BMIN = (Align.CENTER, Align.CENTER, Align.MIN)


def build_case():
    with BuildPart() as part:
        Box(OUTER_W, OUTER_D, OUTER_H, align=BMIN)
        # 오른쪽 벽에서 안쪽으로 상자 파냄 (오른쪽만 뚫림)
        with Locations((-OUTER_W / 2 + WALL, 0, (OUTER_H - INNER_H) / 2)):
            Box(INNER_W, INNER_D, INNER_H, align=(Align.MIN, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        # 오른쪽 위 천장 일부 파냄
        with Locations((OUTER_W / 2, 0, OUTER_H)):
            Box(3, INNER_D, WALL, align=(Align.MAX, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
        # 오른쪽 돌출부 앞/뒤 벽을 얇게 (내부 1.1씩 확장)
        with Locations((INNER_PILLAR_X_END, -OUTER_D / 2 + WALL_FB_THIN, WALL)):
            Box(3, WALL_FB - WALL_FB_THIN, OUTER_H - WALL, align=(Align.MIN, Align.MIN, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((INNER_PILLAR_X_END, OUTER_D / 2 - WALL_FB_THIN, WALL)):
            Box(3, WALL_FB - WALL_FB_THIN, OUTER_H - WALL, align=(Align.MIN, Align.MAX, Align.MIN), mode=Mode.SUBTRACT)
        # 앞/뒤 위 내부 사각 기둥
        with Locations((-OUTER_W / 2 + WALL, -OUTER_D / 2 + WALL_FB, OUTER_H - WALL)):
            Box(INNER_PILLAR_W, INNER_PILLAR_D, INNER_PILLAR_H, align=(Align.MIN, Align.MIN, Align.MAX))
        with Locations((-OUTER_W / 2 + WALL, OUTER_D / 2 - WALL_FB, OUTER_H - WALL)):
            Box(INNER_PILLAR_W, INNER_PILLAR_D, INNER_PILLAR_H, align=(Align.MIN, Align.MAX, Align.MAX))

        # 앞/뒤 사다리꼴 기둥 (오른쪽 개구 가장자리)
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(
                    (PILLAR_X, PILLAR_Y_FRONT),
                    (PILLAR_X - PILLAR_BASE, PILLAR_Y_FRONT),
                    (PILLAR_X - PILLAR_TOP, PILLAR_Y_FRONT + PILLAR_H),
                    (PILLAR_X, PILLAR_Y_FRONT + PILLAR_H),
                    close=True,
                )
            make_face()
        extrude(amount=PILLAR_LEN)
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(
                    (PILLAR_X, PILLAR_Y_BACK),
                    (PILLAR_X - PILLAR_BASE, PILLAR_Y_BACK),
                    (PILLAR_X - PILLAR_TOP, PILLAR_Y_BACK - PILLAR_H),
                    (PILLAR_X, PILLAR_Y_BACK - PILLAR_H),
                    close=True,
                )
            make_face()
        extrude(amount=PILLAR_LEN)

        # 안쪽 기둥 핀 구멍 2개 (+X 방향)
        with Locations(Plane.YZ.offset(INNER_PILLAR_X_END)):
            with Locations(
                (INNER_PILLAR_CY_FRONT, INNER_PILLAR_CZ),
                (INNER_PILLAR_CY_BACK, INNER_PILLAR_CZ),
            ):
                Cylinder(INNER_HOLE_R, INNER_HOLE_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_case())

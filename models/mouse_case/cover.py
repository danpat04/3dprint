"""mouse_case 커버 — 무선 마우스 케이스 덮개.

case 오른쪽 개구를 막는 얇은 판. 앞/뒤 위 모서리 비대칭 챔퍼, 결합용 핀 구멍 2개.
(legacy/etc/mousehead_cover.py 이관)
"""

from build123d import Align, Box, BuildPart, Cylinder, Locations, Mode, chamfer

from models._lib.iter import finalize_iteration

# ---- 외부 치수 (mm) — 왼쪽 외곽 X=-31.75 고정 (구멍 위치 유지) ----
OUTER_W = 27.5
OUTER_D = 109.7   # case 돌출부 내부에 맞춰 확장 (내부 107.5 + 양쪽 1.1)
OUTER_H = 3.0
BOX_LEFT = -31.75
BOX_RIGHT = BOX_LEFT + OUTER_W          # -4.25
BOX_CENTER_X = BOX_LEFT + OUTER_W / 2   # -18

# ---- 앞-위 모서리 비대칭 챔퍼 ----
CHAMFER_TOP = 1.65    # 위쪽 면에서 앞쪽으로
CHAMFER_FRONT = 2.15  # 앞쪽 면에서 아래로

# ---- 면 공차 깎기 (챔퍼 영역 제외) ----
FACE_CUT = 0.15

# ---- 핀 구멍 (case 안쪽 기둥과 같은 Y 위치) ----
HOLE_R = 4.97 / 2
HOLE_DEPTH = 2.1
HOLE_X = BOX_LEFT + 5.5   # X=-26.25
HOLE_Y = 48.75            # ±48.75


def build_cover():
    with BuildPart() as part:
        with Locations((BOX_CENTER_X, 0, 0)):
            Box(OUTER_W, OUTER_D, OUTER_H, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 앞쪽-위쪽 모서리 챔퍼 (비대칭)
        top_front = [e for e in part.edges()
                     if abs(e.center().Y - (-OUTER_D / 2)) < 1e-3 and abs(e.center().Z - OUTER_H) < 1e-3]
        chamfer(top_front, length=CHAMFER_FRONT, length2=CHAMFER_TOP)
        # 뒤쪽-위쪽 모서리 챔퍼 (반전 대칭)
        top_back = [e for e in part.edges()
                    if abs(e.center().Y - OUTER_D / 2) < 1e-3 and abs(e.center().Z - OUTER_H) < 1e-3]
        chamfer(top_back, length=CHAMFER_TOP, length2=CHAMFER_FRONT)

        # 앞/뒤/오른쪽/상단 면 공차 깎기
        with Locations((BOX_CENTER_X, -OUTER_D / 2, 0)):
            Box(OUTER_W, FACE_CUT, OUTER_H, align=(Align.CENTER, Align.MIN, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((BOX_CENTER_X, OUTER_D / 2, 0)):
            Box(OUTER_W, FACE_CUT, OUTER_H, align=(Align.CENTER, Align.MAX, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((BOX_RIGHT, 0, 0)):
            Box(FACE_CUT, OUTER_D, OUTER_H, align=(Align.MAX, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((BOX_CENTER_X, 0, OUTER_H)):
            Box(OUTER_W, OUTER_D, FACE_CUT, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

        # 핀 구멍 2개 (아랫면에서 위로)
        with Locations((HOLE_X, -HOLE_Y, 0), (HOLE_X, HOLE_Y, 0)):
            Cylinder(HOLE_R, HOLE_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_cover())

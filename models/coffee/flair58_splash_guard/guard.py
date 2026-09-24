"""flair58_splash_guard — ㄱ자 파트 2개.

ㄷ 자 가드를 뒷벽 중앙에서 반으로 쪼개, **옆벽 + 뒷벽 절반을 한 파트로** 만든다.
코너가 일체라 자립 안정성이 높고, 세워서 출력하므로 발판도 일체로 붙는다.

두 파트는 미러가 아니다:
  x=300 쪽 (사용자 기준 **왼쪽**) — 전원선 홈 + 그루브
  x=0   쪽 (사용자 기준 오른쪽)  — 텅

중앙 이음은 **역사다리꼴(도브테일)** — 끝이 뿌리보다 넓어 x 방향으로 빠지지 않는다.
조립은 위에서 아래로 수직 슬라이드.

출력: 세워서(사용 자세 그대로) bed 에. 두 벽이 모두 수직이고 발 플랜지가 bed 에
깔리며, 옆벽 사다리꼴은 위로 갈수록 짧아질 뿐이라 **서포트가 전혀 필요 없다**.
"""

from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Compound,
    Locations,
    Mode,
    Plane,
    Polygon,
    Rectangle,
    add,
    extrude,
    loft,
    mirror,
)

from models._lib.iter import finalize_iteration
from models.coffee.flair58_splash_guard.params import *  # noqa: F403

MIN3 = (Align.MIN, Align.MIN, Align.MIN)


def _box(x0, x1, y0, y1, z0, z1, mode=Mode.ADD):
    """전역 좌표 (x0..x1, y0..y1, z0..z1) 로 박스. 읽기 쉬우라고 감싼다."""
    with Locations((x0, y0, z0)):
        Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3, mode=mode)


def _l_base():
    """이음 특징 없는 ㄱ자 기본 형상 (x=0 쪽). 벽 + 발."""
    with BuildPart() as part:
        # ---- 벽 ----
        _box(-WALL_T, SPLIT_X, -WALL_T, 0.0, 0.0, WALL_H)     # 뒷벽 절반

        # 옆벽 — TAPER_Y~SIDE_L 구간이 WALL_H→FRONT_H 로 낮아짐
        with BuildSketch(Plane.YZ.offset(-WALL_T)):
            Polygon((-WALL_T, 0.0), (SIDE_L, 0.0), (SIDE_L, FRONT_H),
                    (TAPER_Y, WALL_H), (-WALL_T, WALL_H), align=None)
        extrude(amount=WALL_T)

        # ---- 발: 바깥 플랜지 ----
        # 뒤쪽만 남긴다. 옆쪽(FOOT_SIDE)은 눈에 보여서 제거했다.
        x0 = -WALL_T - FOOT_SIDE
        if FOOT_BACK > 0:
            # 쐐기 단면 — 뿌리 FOOT_OUT_T, 끝 FOOT_TIP_T
            y_tip = -WALL_T - FOOT_BACK
            with BuildSketch(Plane.YZ.offset(x0)):
                Polygon((y_tip, 0.0), (-WALL_T, 0.0),
                        (-WALL_T, FOOT_OUT_T), (y_tip, FOOT_TIP_T), align=None)
            extrude(amount=SPLIT_X - x0)
        if FOOT_SIDE > 0:
            _box(x0, -WALL_T, -WALL_T - FOOT_BACK, SIDE_L, 0.0, FOOT_OUT_T)

        # ---- 발: 안쪽 혀 (매트 밑) ----
        # L 자 단면을 위아래 두 장으로 loft 해서 끝 램프를 만든다.
        # 쐐기 2개를 따로 빼면 코너에서 서로를 파먹어 과절삭된다 (iter_001 버그).
        w = FOOT_IN - FOOT_RAMP
        with BuildSketch(Plane.XY):
            Polygon((0.0, 0.0), (SPLIT_X, 0.0), (SPLIT_X, FOOT_IN),
                    (FOOT_IN, FOOT_IN), (FOOT_IN, SIDE_L), (0.0, SIDE_L),
                    align=None)
        with BuildSketch(Plane.XY.offset(FOOT_IN_T)):
            Polygon((0.0, 0.0), (SPLIT_X, 0.0), (SPLIT_X, w),
                    (w, w), (w, SIDE_L), (0.0, SIDE_L), align=None)
        loft()

    return part.part


def _dovetail(half_root, half_tip, x0, x1):
    """도브테일 사다리꼴 폴리곤 (XY 평면). x0=뿌리, x1=끝."""
    return Polygon((x0, BOSS_Y - half_root), (x1, BOSS_Y - half_tip),
                   (x1, BOSS_Y + half_tip), (x0, BOSS_Y + half_root),
                   align=None)


def build_right():
    """x=0 쪽 = 사용자 기준 오른쪽. 텅."""
    with BuildPart() as part:
        add(_l_base())

        # 이음부 보강 — 바깥으로만 두껍게 (안쪽 면은 평평하게 유지)
        _box(SPLIT_X - BOSS_L, SPLIT_X, -BOSS_T, -WALL_T, 0.0, WALL_H)

        # 텅 (역사다리꼴)
        with BuildSketch(Plane.XY):
            _dovetail(TONGUE_ROOT / 2, TONGUE_TIP / 2,
                      SPLIT_X, SPLIT_X + TONGUE_L)
        extrude(amount=WALL_H)

    return part.part


def build_left():
    """x=300 쪽 = 사용자 기준 왼쪽. 그루브 + 전원선 홈."""
    with BuildPart() as part:
        add(mirror(_l_base(), about=Plane.YZ.offset(SPLIT_X)))

        # 이음부 보강
        _box(SPLIT_X, SPLIT_X + BOSS_L, -BOSS_T, -WALL_T, 0.0, WALL_H)

        # 그루브 — 텅 자리 (공차 FIT). 발까지 관통해야 텅이 끝까지 내려온다
        with BuildSketch(Plane.XY.offset(-1.0)):
            _dovetail(GROOVE_ROOT / 2, GROOVE_TIP / 2,
                      SPLIT_X - 0.01, SPLIT_X + GROOVE_L)
        extrude(amount=WALL_H + 2, mode=Mode.SUBTRACT)

        # 전원선 홈 — 사용자 왼쪽 옆벽(x=300 쪽), 상단에서 아래로. 바닥은 반원
        r = CORD_W / 2
        z_c = WALL_H - CORD_DEPTH + r
        x_face = INNER_W          # 이 벽은 x=300 ~ 302.5
        with BuildSketch(Plane.YZ.offset(x_face - 1)):
            with Locations((CORD_Y, z_c)):
                Circle(r)
            with Locations((CORD_Y, (z_c + WALL_H + 5) / 2)):
                Rectangle(CORD_W, WALL_H + 5 - z_c)
        extrude(amount=WALL_T + 2, mode=Mode.SUBTRACT)

    return part.part


def build_assembly():
    left, right = build_left(), build_right()
    left.label, right.label = "left", "right"
    return Compound(children=[left, right])


if __name__ == "__main__":
    finalize_iteration(build_assembly())

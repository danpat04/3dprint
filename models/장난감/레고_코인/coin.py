"""레고_코인 — 투명 PLA 놀이용 코인.

    uv run python -m models.장난감.레고_코인.coin

앞·뒷면은 매끈하고, **숫자는 속에 빈 공간으로 묻는다.** 투명 재료라
그 공간의 면이 빛을 산란시켜 숫자가 안에 떠 있는 것처럼 보인다.
불투명 재료로는 안 되는 효과다.

눕혀서(면을 bed 에) 뽑는다. 앞뒤가 평평하고 테두리가 수직이라 서포트가
없고, 공동 위를 덮는 브리지는 **글자 획 폭**(1~2mm)만 건너면 된다.
"""

from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Cylinder,
    Mode,
    Plane,
    Text,
    chamfer,
    extrude,
)

from models._lib.iter import finalize_iteration
from models.장난감.레고_코인.params import (
    COIN_D,
    COIN_T,
    EDGE_CH,
    FONT,
    TEXT_H,
    TEXT_MARGIN,
    VOID_COVER,
    VOID_T,
)

BOT = (Align.CENTER, Align.CENTER, Align.MIN)

VOID_BOT = VOID_COVER                    # 공동 아랫면 — 1.8
VOID_TOP = VOID_BOT + VOID_T             # 공동 윗면 — 4.4


def _fit_text(label):
    """코인 안에 들어가도록 폰트 크기를 줄인 스케치를 돌려준다.

    한 자리는 TEXT_H 그대로, 두 자리('10')는 그대로 두면 14.4mm 라
    ⌀15.7 코인을 넘는다. 넘치는 만큼만 줄인다 — 줄이면 획도 같이
    가늘어지므로 꼭 필요한 만큼만.
    """
    avail = COIN_D - 2 * TEXT_MARGIN
    size = TEXT_H
    for _ in range(6):
        with BuildSketch() as sk:
            Text(label, font_size=size, font=FONT)
        w = sk.sketch.bounding_box().size.X
        if w <= avail:
            return sk.sketch, size
        size *= avail / w * 0.98
    return sk.sketch, size


def build_coin(label="5"):
    """코인 한 개. label 을 속에 빈 공간으로 묻는다."""
    txt, _ = _fit_text(label) if label else (None, 0)
    with BuildPart() as part:
        Cylinder(COIN_D / 2, COIN_T, align=BOT)
        # 테두리 모따기 — 손에 닿는 곳이고, 빛을 받는 면이 하나 더 생긴다
        chamfer(part.edges().filter_by(Axis.Z, reverse=True), EDGE_CH)

        if label:
            extrude(Plane.XY.offset(VOID_BOT) * txt, VOID_T, mode=Mode.SUBTRACT)
    return part.part


if __name__ == "__main__":
    finalize_iteration(build_coin(None))


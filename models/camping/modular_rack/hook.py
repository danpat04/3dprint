"""modular_rack — S후크 (별도 부품, 동일 3개).

cutlery_holder 에서 검증된 후크 구조 그대로, 틀 치수에 맞춤:
  - 더브테일 레일(목=틀 뒷면, 넓은+seat=벽 안) z 0~SLOT_TOP
  - 보강판: 레일 목을 따라 바닥~후크 상단 전체
  - 걸이: 브릿지(얇게) + 안쪽 하강(두껍고 길게) + 끝 벌림
출력: YZ 프로파일이 bed 에 눕도록 뉘여 출력.
"""

from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Locations,
    Plane,
    Polygon,
    Rectangle,
    extrude,
    loft,
)

from models._lib.iter import finalize_iteration
from models.camping.modular_rack.params import (
    BOX_WALL, CLAMP_T, DT_DEPTH, DT_NECK, DT_SEAT, DT_W, FLARE, FLARE_LEN,
    FRAME_H, HOOK_CLR, HOOK_DROP, HOOK_RISE, HOOK_T, HOOK_WIDTH,
    SLOT_TOP, Y_BACK,
)

CCMAX = (Align.CENTER, Align.CENTER, Align.MAX)

Y0 = Y_BACK                           # 틀 뒷면 (보강판이 이 바깥에 붙음)
Y_BOX_IN = Y0 - HOOK_T - BOX_WALL     # 박스 안쪽면 — 박스 바깥면은 보강판에 닿음
Y_CLAMP_IN = Y_BOX_IN - HOOK_CLR      # 클램프 안쪽 하강벽의 안쪽면
Y_CLAMP_FACE = Y_CLAMP_IN - HOOK_T
TOP = FRAME_H + HOOK_RISE             # 후크 최상단 (틀 상단보다 HOOK_RISE 위)


def build_hook():
    with BuildPart() as hook:
        # 1) 더브테일 레일 (목=Y0, 넓은+seat=+Y). z 0~SLOT_TOP
        with BuildSketch(Plane.XY):
            with Locations((0, Y0)):
                Polygon(
                    (-DT_NECK / 2, 0.0),
                    (DT_NECK / 2, 0.0),
                    (DT_W / 2, DT_DEPTH),
                    (DT_W / 2, DT_DEPTH + DT_SEAT),
                    (-DT_W / 2, DT_DEPTH + DT_SEAT),
                    (-DT_W / 2, DT_DEPTH),
                    align=None,
                )
        extrude(amount=SLOT_TOP)

        # 2) 보강판: 레일 목(Y0)을 따라 바닥~후크 상단 전체
        with Locations((0, Y0, 0)):
            Box(HOOK_WIDTH, HOOK_T, TOP,
                align=(Align.CENTER, Align.MAX, Align.MIN))

        # 3) 걸이 브릿지 (박스 위를 가로지름) — 얇게(CLAMP_T)
        with Locations((0, (Y0 + Y_CLAMP_FACE) / 2, TOP)):
            Box(HOOK_WIDTH, Y0 - Y_CLAMP_FACE, CLAMP_T, align=CCMAX)

        # 4) 걸이 안쪽 하강 (박스 안쪽면, 두께 HOOK_T, 길게)
        cy = Y_CLAMP_IN - HOOK_T / 2
        straight = HOOK_DROP - FLARE_LEN
        with Locations((0, cy, TOP)):
            Box(HOOK_WIDTH, HOOK_T, straight, align=CCMAX)
        # 4b) 끝 벌림 (lead-in)
        z_mid = TOP - straight
        z_bot = TOP - HOOK_DROP
        with BuildSketch(Plane.XY.offset(z_mid)) as fa:
            with Locations((0, cy)):
                Rectangle(HOOK_WIDTH, HOOK_T)
        with BuildSketch(Plane.XY.offset(z_bot)) as fb:
            with Locations((0, cy - FLARE)):
                Rectangle(HOOK_WIDTH, HOOK_T)
        loft([fb.sketch, fa.sketch])

    return hook.part


if __name__ == "__main__":
    finalize_iteration(build_hook())

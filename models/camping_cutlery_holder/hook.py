"""camping_cutlery_holder — S후크 (별도 부품, 좌우 2개 동일).

재설계 (통이 박스 바깥에 걸림):
  - 통 뒷면(y=Y0)이 박스 바깥면에 밀착. 박스 벽은 통 뒤(-Y).
  - 레일(더브테일 수)은 목=Y0(통 뒷면), 넓은=통 안(+Y). 통 뒷벽 홈에 끼움.
  - 클램프는 목(Y0)에서 -Y 로 박스 테두리를 감쌈.
  - [A안] 레일 상단(z=SLOT_TOP, 박스 테두리 높이)이 통 슬롯 천장에 얹혀 통 무게 지지.

조립: 후크를 박스에 걸고, 통을 박스 바깥에서 위→아래로 레일에 끼운다.
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
from models.camping_cutlery_holder.params import (
    BOX_WALL,
    DT_DEPTH,
    DT_NECK,
    DT_W,
    CLAMP_T,
    DT_SEAT,
    FLARE,
    FLARE_LEN,
    HOOK_CLR,
    HOOK_DROP,
    HOOK_RISE,
    HOOK_T,
    HOOK_WIDTH,
    OUT_D,
    OUT_H,
    SLOT_TOP,
)

CCMIN = (Align.CENTER, Align.CENTER, Align.MIN)
CCMAX = (Align.CENTER, Align.CENTER, Align.MAX)

Y0 = -OUT_D / 2                       # 통 뒷면 = 박스 바깥면
Y_BOX_IN = Y0 - BOX_WALL              # 박스 안쪽면
Y_CLAMP_IN = Y_BOX_IN - HOOK_CLR      # 클램프 안쪽 하강벽의 안쪽면
Y_CLAMP_FACE = Y_CLAMP_IN - HOOK_T    # 안쪽 하강 두께 = HOOK_T (앞쪽과 맞춤)
TOP = OUT_H + HOOK_RISE               # 후크 최상단 (통 상단보다 HOOK_RISE 위)


def build_hook():
    with BuildPart() as hook:
        # 1) 더브테일 레일 (목=Y0 통 뒷면, 넓은=통 안 +Y). z 0~SLOT_TOP
        #    넓은 끝(통 안)에 직사각형 seat: 폭=DT_W(=보강판)라 뉘여 출력 시 옆면이 평평.
        with BuildSketch(Plane.XY):
            with Locations((0, Y0)):
                Polygon(
                    (-DT_NECK / 2, 0.0),                  # 목 (통 뒷면)
                    (DT_NECK / 2, 0.0),
                    (DT_W / 2, DT_DEPTH),                 # 넓은 (경사 45° 끝)
                    (DT_W / 2, DT_DEPTH + DT_SEAT),       # seat (통 안쪽으로)
                    (-DT_W / 2, DT_DEPTH + DT_SEAT),
                    (-DT_W / 2, DT_DEPTH),
                    align=None,
                )
        extrude(amount=SLOT_TOP)

        # 2) 클램프 지지판: 레일 목(Y0)을 따라 바닥(z=0)~후크 상단(TOP) 전체로 연장.
        #    레일과 전체 높이로 붙어(면접촉) 하중을 분산 + 통 상단 위로 HOOK_RISE 연장.
        with Locations((0, Y0, 0)):
            Box(HOOK_WIDTH, HOOK_T, TOP,
                align=(Align.CENTER, Align.MAX, Align.MIN))

        # 3) 클램프 브릿지 (후크 상단 z=TOP, 박스 위를 가로질러 안쪽 넘어까지) — 얇게(CLAMP_T)
        with Locations((0, (Y0 + Y_CLAMP_FACE) / 2, TOP)):
            Box(HOOK_WIDTH, Y0 - Y_CLAMP_FACE, CLAMP_T, align=CCMAX)

        # 4) 클램프 안쪽 하강 (박스 안쪽면을 따라, 두께 HOOK_T=앞쪽 맞춤, 길게)
        cy = Y_CLAMP_IN - HOOK_T / 2
        straight = HOOK_DROP - FLARE_LEN
        with Locations((0, cy, TOP)):
            Box(HOOK_WIDTH, HOOK_T, straight, align=CCMAX)
        # 4b) 끝 벌림 (lead-in): 하단이 박스 안쪽(-Y)으로 FLARE 벌어져 끼움 안내
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

"""modular_rack — 틀(frame) 파트.

박스에 후크로 걸리는 직사각 링. 내부 개구 210×70 에 통을 drop-in.
뒷벽(12mm)이 더브테일 슬롯(암) 3개를 벽 안에 품는다 — 개구쪽 돌출 없음.
출력: 사용 방향 그대로 (링이 bed 에 평평, 슬롯 천장 20×7 은 짧은 브릿지).
"""

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Locations,
    Mode,
    Plane,
    Polygon,
    Rectangle,
    chamfer,
    extrude,
    loft,
)

from models._lib.iter import finalize_iteration
from models.camping.modular_rack.params import (
    BACK_CLR, DT_CLR, DT_DEPTH, DT_NECK, DT_SEAT, DT_W, FRAME_CH, FRAME_H,
    HOOK_WIDTH, HOOK_XS, OPEN_D, OPEN_W, OUT_W, RIB_P, RIB_TAPER, RIB_TOP,
    RIB_W, SLOT_TOP, SLOTS, UNIT, Y_BACK, Y_FRONT,
)

CCMIN = (Align.CENTER, Align.CENTER, Align.MIN)


def build_frame():
    with BuildPart() as part:
        # 링 몸체: 외곽 - 개구 (개구 중심 = 원점, 뒷벽만 두꺼워 Y 비대칭)
        with Locations((0, (Y_FRONT + Y_BACK) / 2, 0)):
            Box(OUT_W, Y_FRONT - Y_BACK, FRAME_H, align=CCMIN)
        Box(OPEN_W, OPEN_D, FRAME_H + 1, align=CCMIN, mode=Mode.SUBTRACT)

        # 개구 위 모서리 45° 챔퍼 — 통 플랜지 챔퍼가 여기 얹혀 안착(self-centering)
        top_edges = part.edges().group_by(Axis.Z)[-1]
        inner = [e for e in top_edges
                 if abs(e.center().Y) < OPEN_D / 2 + 0.1
                 and abs(e.center().X) < OPEN_W / 2 + 0.1]
        chamfer(inner, length=FRAME_CH)

        # 유닛 경계 리브: 앞/뒷벽 안쪽면 x=±35, 상단은 테이퍼(삽입 유도).
        # 통의 경계 홈에 물려 X 위치 고정. 리브 상단 36 < 플랜지 챔퍼 안착면.
        boundaries = [(-SLOTS / 2 + i) * UNIT for i in range(1, SLOTS)]
        straight_top = RIB_TOP - RIB_TAPER
        for bx in boundaries:
            for wall_y, inward in ((OPEN_D / 2, -1), (-OPEN_D / 2, 1)):
                with Locations((bx, wall_y + inward * RIB_P / 2, 0)):
                    Box(RIB_W, RIB_P, straight_top, align=CCMIN)
                with BuildSketch(Plane.XY.offset(straight_top)) as r0:
                    with Locations((bx, wall_y + inward * RIB_P / 2)):
                        Rectangle(RIB_W, RIB_P)
                with BuildSketch(Plane.XY.offset(RIB_TOP)) as r1:
                    with Locations((bx, wall_y + inward * 0.01)):
                        Rectangle(RIB_W * 0.2, 0.02)
                loft([r0.sketch, r1.sketch])

        # 더브테일 슬롯(암) 3개: 목=틀 뒷면, 넓은+seat=벽 안쪽 (+Y).
        # z 0~SLOT_TOP — 슬롯 천장이 레일 상단에 얹혀 틀 무게 지지.
        neck = DT_NECK + DT_CLR
        wide = DT_W + DT_CLR
        seat_y = DT_DEPTH + DT_SEAT + DT_CLR  # Y공차: 경사면이 먼저 물리게
        for sx in HOOK_XS:
            with BuildSketch(Plane.XY) as slot:
                with Locations((sx, Y_BACK)):
                    Polygon(
                        (-neck / 2, 0.0),
                        (neck / 2, 0.0),
                        (wide / 2, DT_DEPTH),
                        (wide / 2, seat_y),
                        (-wide / 2, seat_y),
                        (-wide / 2, DT_DEPTH),
                        align=None,
                    )
            extrude(slot.sketch, amount=SLOT_TOP, mode=Mode.SUBTRACT)

        # 보강판 공차: 틀 뒷면을 BACK_CLR 얕게 리세스 (후크 보강판 자리)
        for sx in HOOK_XS:
            with Locations((sx, Y_BACK + BACK_CLR / 2, 0)):
                Box(HOOK_WIDTH + 1, BACK_CLR + 0.01, FRAME_H,
                    align=CCMIN, mode=Mode.SUBTRACT)

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_frame())

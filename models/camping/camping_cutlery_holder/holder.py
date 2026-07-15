"""camping_cutlery_holder — 통(holder) 파트.

그물망 통 + 원뿔 깔때기 바닥 + 뒷면 더브테일 슬롯(암) 2개.
일체형 후크는 없음 (후크는 별도 부품 hook.py). 통은 세워서 출력.
"""

import math

from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    GridLocations,
    Locations,
    Mode,
    Plane,
    Polygon,
    Rectangle,
    extrude,
    loft,
)

from models._lib.iter import finalize_iteration
from models.camping.camping_cutlery_holder.params import (
    BACK_CLR, BASE, BOSS_D, BOSS_W, DRAIN_D, DT_CLR, DT_DEPTH, DT_NECK,
    DT_SEAT, DT_W, FLOOR_RISE, H_OPEN, HOOK_WIDTH, HOOK_X, IN_D, IN_H, IN_W,
    MESH_P, MESH_RIB, OUT_D, OUT_H, OUT_W, SLOT_CAP, SLOT_TOP, THROAT_R,
    WALL, Z_OPEN,
)

CCMIN = (Align.CENTER, Align.CENTER, Align.MIN)


def mesh_face(plane, w_open):
    """벽면 하나를 그물망으로 (개구부 SUBTRACT + 대각 리브 ADD, 상단 45° 톱니)."""
    n = int((w_open + H_OPEN) / MESH_P) + 3
    n += n % 2
    nt = int(w_open / MESH_P) + 2
    nt += nt % 2
    side = MESH_P / math.sqrt(2)
    diag = math.hypot(w_open, H_OPEN) + 2 * MESH_P

    with BuildSketch(plane) as opening:
        Rectangle(w_open, H_OPEN)
        with Locations((0, H_OPEN / 2)):
            with GridLocations(MESH_P, MESH_P, nt, 1):
                Rectangle(side, side, rotation=45, mode=Mode.SUBTRACT)
    extrude(opening.sketch, amount=-(WALL + 0.6), mode=Mode.SUBTRACT)

    with BuildSketch(plane) as net:
        with GridLocations(MESH_P, MESH_P, n, 1):
            Rectangle(MESH_RIB, diag, rotation=45)
        with GridLocations(MESH_P, MESH_P, n, 1):
            Rectangle(MESH_RIB, diag, rotation=-45)
        Rectangle(w_open, H_OPEN, mode=Mode.INTERSECT)
        with Locations((0, H_OPEN / 2)):
            with GridLocations(MESH_P, MESH_P, nt, 1):
                Rectangle(side, side, rotation=45, mode=Mode.SUBTRACT)
    extrude(net.sketch, amount=-WALL, mode=Mode.ADD)


# 그물망용 4면 (법선 바깥, 로컬 세로축 모두 world +Z)
FRONT = Plane(origin=(0, OUT_D / 2, Z_OPEN), x_dir=(-1, 0, 0), z_dir=(0, 1, 0))
BACK = Plane(origin=(0, -OUT_D / 2, Z_OPEN), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
RIGHT = Plane(origin=(OUT_W / 2, 0, Z_OPEN), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
LEFT = Plane(origin=(-OUT_W / 2, 0, Z_OPEN), x_dir=(0, -1, 0), z_dir=(-1, 0, 0))


def build_holder():
    with BuildPart() as part:
        # 통 외곽
        Box(OUT_W, OUT_D, OUT_H, align=CCMIN)

        # 내부 파냄 (바닥 BASE+RISE 두께)
        with Locations((0, 0, BASE + FLOOR_RISE)):
            Box(IN_W, IN_D, IN_H + 10, align=CCMIN, mode=Mode.SUBTRACT)

        # 원뿔 깔때기 홈 (위 사각 → 아래 원)
        with BuildSketch(Plane.XY.offset(BASE)) as throat:
            Circle(THROAT_R)
        with BuildSketch(Plane.XY.offset(BASE + FLOOR_RISE)) as brim:
            Rectangle(IN_W, IN_D)
        loft([throat.sketch, brim.sketch], mode=Mode.SUBTRACT)

        # 중앙 배수 구멍
        with Locations((0, 0, -2)):
            Cylinder(DRAIN_D / 2, BASE + FLOOR_RISE + 4, align=CCMIN, mode=Mode.SUBTRACT)

        # 벽면 그물망 4면
        mesh_face(FRONT, IN_W)
        mesh_face(BACK, IN_W)
        mesh_face(RIGHT, IN_D)
        mesh_face(LEFT, IN_D)

        # 뒷면 더브테일 기둥 + 슬롯(암) 좌우 2개 — 통 뒷벽과 겹쳐 통 안쪽(+Y)으로 두껍게
        # [A안] 통 무게는 슬롯 천장(z=SLOT_TOP, 박스 테두리 높이)이 레일 상단에 얹혀 지지.
        # 더브테일 목(좁은)=통 뒷면(y_back, 박스 바깥면), 넓은쪽=통 안(+Y). 후크 레일이 통 쪽.
        # 겹치는 영역은 그물 대신 솔리드 기둥.
        y_back = -OUT_D / 2
        neck = DT_NECK + DT_CLR
        wide = DT_W + DT_CLR
        depth = DT_DEPTH + DT_CLR
        for sx in (-HOOK_X, HOOK_X):
            # 솔리드 기둥: 통 뒷면(y_back)에서 통 안(+Y)으로. z 0~SLOT_TOP+CAP
            with Locations((sx, y_back + BOSS_D / 2, 0)):
                Box(BOSS_W, BOSS_D, SLOT_TOP + SLOT_CAP, align=CCMIN)
        for sx in (-HOOK_X, HOOK_X):
            # 더브테일 슬롯 (암): 목=통 뒷면(y_back), 넓은+seat=통 안(+Y). z 0~SLOT_TOP 천장
            # Y방향 공차: seat 바닥을 레일보다 DT_CLR 깊게 파서 경사면(X)이 먼저 물리게 함
            seat_y = DT_DEPTH + DT_SEAT + DT_CLR
            with BuildSketch(Plane.XY) as slot:
                with Locations((sx, y_back)):
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
        for sx in (-HOOK_X, HOOK_X):
            # 보강판 공차: 통 뒷면(기둥 앞면)을 BACK_CLR 얕게 리세스 → 보강판이 밀착 안 함
            with Locations((sx, y_back + BACK_CLR / 2, 0)):
                Box(HOOK_WIDTH + 1, BACK_CLR + 0.01, SLOT_TOP + SLOT_CAP,
                    align=CCMIN, mode=Mode.SUBTRACT)

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_holder())

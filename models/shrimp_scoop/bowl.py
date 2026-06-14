"""shrimp_scoop / bowl — 망 안착 컵 + 핸들 소켓 boss.

Ø30.7 × 9.5 의 작은 컵.
  z=0..1.0   : 바닥 floor (Ø30.7 OD, Ø25 mesh 노출 hole)
  z=1.0..9.5 : cavity Ø27.7 (벽 1.5mm, 안쪽으로 두꺼워짐)
  z=1.0..3.0 : ring 안착 영역 (cavity 내, floor 위, 2mm 두께)
  z=0..9.5   : +X 안쪽 핸들 boss (floor 까지 일체)
  z=1.0..9.5 : 그 안의 socket hole (1.05 R × 3.55 T, 외벽 1.0 잔여, 깊이 8.5mm)
               ring 영역(z=1~3)을 관통 — handle 이 ring 안쪽까지 깊게 박힘
"""

import math

from build123d import Align, Box, BuildPart, Cone, Cylinder, Locations, Mode

from models._lib.iter import finalize_iteration


ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

# 볼 본체
OUTER_D = 30.7
HEIGHT = 9.5
WALL = 1.5                       # 안쪽으로 두꺼워짐 (외경 유지)
INNER_D = OUTER_D - 2 * WALL    # 27.7
FLOOR_H = 1.0

# 망 / 링
MESH_D = 25.0                   # 망 노출 영역
RING_H = 2.0                    # ring 두께(높이) — 큰 cone 수용 위해 증가
RING_TOP_Z = FLOOR_H + RING_H   # 3.0

# 핸들 단면 (90° 회전: thin radial × wide tangential)
H_RECT_RADIAL = 1.0             # 핸들 radial (얇음)
H_RECT_TANG = 3.5               # 핸들 tangential (넓음)
FIT_TOL = 0.05                  # 빡빡 끼움

# 소켓 (handle + 0.05, 회전된 방향)
SOCKET_R_SIZE = H_RECT_RADIAL + FIT_TOL   # 1.05 (radial)
SOCKET_T_SIZE = H_RECT_TANG + FIT_TOL     # 3.55 (tangential)
SOCKET_OUTER_X = OUTER_D / 2 - 1.0        # 14.35 — 외벽 1.0 잔여 (slice 견고, was 0.4)
SOCKET_INNER_X = SOCKET_OUTER_X - SOCKET_R_SIZE  # 13.3
SOCKET_BOTTOM_Z = FLOOR_H                 # 1.0 (was RING_TOP_Z=3.0) — handle 이 floor 까지 깊게
SOCKET_DEPTH = HEIGHT - SOCKET_BOTTOM_Z   # 8.5 (was 6.5) — handle column 이 ring 영역 관통

# Boss (얕고 넓적: radial 1mm 돌출, tangential 5.55mm)
BOSS_WALL = 1.0
BOSS_INNER_X = SOCKET_INNER_X             # 13.30 (socket inner 와 동일, 추가 돌출 없음)
                                          #   → notch 가 덜 안쪽까지 침범 → ring 의 boss 쪽 벽 두꺼워짐 (0.3→0.75mm)
                                          #   trade-off: socket 안쪽 면이 cavity 에 노출 (handle 보임)
BOSS_OUTER_X = INNER_D / 2 + 0.1          # 13.95 — 벽과 약간 겹쳐 union
BOSS_T_HALF = SOCKET_T_SIZE / 2 + BOSS_WALL  # 2.775

# 망 클램프 cone 돌기 (수, floor 위로 솟음 — ring 의 암 recess 와 매칭)
# 슬라이스 견고 위해 사이즈 키움 (was Ø0.5×0.5)
N_CLAMP = 12
CLAMP_D = 0.8                              # 기저 지름 (1.6x)
CLAMP_H = 0.6                              # 높이 (1.2x)
CLAMP_R = 13.15                            # 새 annular 중간 ((25+27.65)/4)
CLAMP_ANG_OFFSET = math.pi / 12            # 15° offset → notch 회피


def build_bowl():
    with BuildPart() as bowl:
        # 1) 외형 실린더
        Cylinder(radius=OUTER_D / 2, height=HEIGHT, align=ALIGN_BOTTOM)
        # 2) cavity (floor 위, 끝까지)
        with Locations((0, 0, FLOOR_H)):
            Cylinder(radius=INNER_D / 2, height=HEIGHT - FLOOR_H,
                     align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        # 3) 망 노출 hole (floor 관통)
        Cylinder(radius=MESH_D / 2, height=FLOOR_H, align=ALIGN_BOTTOM,
                 mode=Mode.SUBTRACT)
        # 4) 핸들 소켓 boss (+X, 얕고 넓적, floor 바닥부터 탑까지 — 깔끔히 일체)
        boss_x_center = (BOSS_INNER_X + BOSS_OUTER_X) / 2
        boss_x_size = BOSS_OUTER_X - BOSS_INNER_X
        with Locations((boss_x_center, 0, 0)):
            Box(boss_x_size, BOSS_T_HALF * 2, HEIGHT, align=ALIGN_BOTTOM)
        # 5) 소켓 hole (회전된 1.05 R × 3.55 T, 외벽 0.4 남김)
        socket_x_center = (SOCKET_INNER_X + SOCKET_OUTER_X) / 2
        with Locations((socket_x_center, 0, SOCKET_BOTTOM_Z)):
            Box(SOCKET_R_SIZE, SOCKET_T_SIZE, SOCKET_DEPTH,
                align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        # 6) 망 클램프 cone 돌기 (수, 10개 — N_CLAMP 중 boss 양옆 i=0(15°)·i=11(345°) 제외)
        for i in range(N_CLAMP):
            if i in (0, N_CLAMP - 1):
                continue                  # boss 와 너무 가까워 슬라이스 간섭
            ang = 2 * math.pi * i / N_CLAMP + CLAMP_ANG_OFFSET
            cx = CLAMP_R * math.cos(ang)
            cy = CLAMP_R * math.sin(ang)
            with Locations((cx, cy, FLOOR_H)):
                Cone(bottom_radius=CLAMP_D / 2, top_radius=0,
                     height=CLAMP_H,
                     align=ALIGN_BOTTOM)
    return bowl.part


if __name__ == "__main__":
    finalize_iteration(build_bowl())

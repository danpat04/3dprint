"""light_baton — 미니 손전등에 끼우는 장난감 경광봉.

유색(불투명) PLA 도 얇으면 투광되는 성질 이용:
  - 소켓(하단 15mm): 벽 2mm 두껍게 — 손전등을 마찰로 잡는 부위
  - 봉(그 위): 벽 0.8mm(라인 2줄) — 안쪽 빛이 비쳐 경광봉 효과
  - 상단: 돔 마감 (0.8mm 쉘)
소켓과 봉의 외경은 동일 (소켓 외경에서 봉이 그대로 뻗음).

손전등은 단차가 없으므로 소켓 천장에 45° 걸림턱(lip)을 둬서
밀어 넣으면 턱에 걸려 멈춘다. 턱 구멍(LIP_D)으로 빛이 나간다.

출력: 소켓이 bed, 세워서 서포트리스 (턱 45°, 돔은 쉘 마감).
"""

from build123d import Align, BuildPart, Cone, Cylinder, Locations, Mode, Sphere

from models._lib.iter import finalize_iteration

CCMIN = (Align.CENTER, Align.CENTER, Align.MIN)

# ---- 손전등 실측 / 결합 ----
HEAD_D = 15.4      # 손전등 헤드 바깥지름 (실측)
FIT_CLR = 0.2      # 직경 공차 — 실측 fit 반영 (0.3 헐거움, 0.15 → 0.2 확정)
SOCKET_H = 15.0    # 끼움 깊이
SOCKET_WALL = 2.0  # 소켓 벽 (잡는 부위, 두껍게)
CHAMFER = 0.8      # 입구 챔퍼 (끼움 lead-in)

# ---- 걸림턱 (소켓 천장) ----
LIP_D = 13.0       # 턱 구멍 지름 — 헤드(15.4)는 걸리고 빛은 통과
LIP_LAND = 0.8     # 턱 평탄 구간

# ---- 봉 (투광부) ----
TOTAL_H = 95.0     # 전체 높이 (소켓 15 + 봉 80, 돔 포함)
BATON_WALL = 0.8   # 라인 2줄 — 유색 PLA 투광 두께

# ---- 파생 ----
BORE_D = HEAD_D + FIT_CLR              # 15.7 소켓 내경
OUT_D = BORE_D + 2 * SOCKET_WALL       # 19.7 외경 (소켓=봉 공통)
BATON_ID = OUT_D - 2 * BATON_WALL      # 18.1 봉 내경
LIP_CONE_H = (BORE_D - LIP_D) / 2      # 45° 턱 높이
DOME_Z = TOTAL_H - OUT_D / 2           # 돔 시작 높이 (돔 정점 = TOTAL_H)


def build_baton():
    with BuildPart() as part:
        # 외형: 원통 + 상단 돔
        Cylinder(OUT_D / 2, DOME_Z, align=CCMIN)
        with Locations((0, 0, DOME_Z)):
            Sphere(OUT_D / 2)

        # 소켓 보어 + 45° 걸림턱 + 턱 평탄부
        Cylinder(BORE_D / 2, SOCKET_H, align=CCMIN, mode=Mode.SUBTRACT)
        with Locations((0, 0, SOCKET_H)):
            Cone(BORE_D / 2, LIP_D / 2, LIP_CONE_H, align=CCMIN,
                 mode=Mode.SUBTRACT)
        z_lip = SOCKET_H + LIP_CONE_H
        with Locations((0, 0, z_lip)):
            Cylinder(LIP_D / 2, LIP_LAND, align=CCMIN, mode=Mode.SUBTRACT)

        # 봉 내부 (0.8 쉘) + 돔 내부
        z_baton = z_lip + LIP_LAND
        with Locations((0, 0, z_baton)):
            Cylinder(BATON_ID / 2, DOME_Z - z_baton, align=CCMIN,
                     mode=Mode.SUBTRACT)
        with Locations((0, 0, DOME_Z)):
            Sphere(BATON_ID / 2, mode=Mode.SUBTRACT)

        # 입구 챔퍼 (아래에서 끼우기 쉽게)
        Cone(BORE_D / 2 + CHAMFER, BORE_D / 2, CHAMFER, align=CCMIN,
             mode=Mode.SUBTRACT)

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_baton())

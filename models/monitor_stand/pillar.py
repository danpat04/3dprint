"""monitor_stand / pillar — 두 T 를 잇는 가로기둥.

축: X 방향 (두 T 의 column 을 잇는 방향)
단면 (Y×Z): 15×15mm
길이 (X): 74.4mm = M4 홀 간격 (양 끝 10mm 가 T 슬롯에 삽입)
양 끝(±X) 면 중심에 Ø5×5mm 자석 매립 홈 (X 방향 안쪽으로 깊이)

build_pillar() — 1개. monitor_stand 에서 2개 사용 (상단/하단).
"""

from build123d import Align, Box, BuildPart, Cylinder, Locations, Mode

from models._lib.iter import finalize_iteration


ALIGN_CENTERED = (Align.CENTER, Align.CENTER, Align.CENTER)

# 단면
PILLAR_LEN = 74.2                # X 길이 (M4 홀 간격 74.4 - 0.2 여유, 출력 변동 흡수)
PILLAR_W = 15.0                  # Y 단면 폭
PILLAR_H = 15.0                  # Z 단면 높이

# 자석
MAGNET_D = 5.0                   # 자석 직경
MAGNET_H = 5.0                   # 자석 높이
MAGNET_HOLE_TOL = 0.1            # 자석 끼움 여유
MAGNET_HOLE_DIA = MAGNET_D + MAGNET_HOLE_TOL    # 5.1
MAGNET_HOLE_DEPTH = MAGNET_H + MAGNET_HOLE_TOL  # 5.1


def build_pillar():
    with BuildPart() as p:
        # 본체 — 원점 중심
        Box(PILLAR_LEN, PILLAR_W, PILLAR_H, align=ALIGN_CENTERED)
        # 자석 홈 — +X 끝
        with Locations((PILLAR_LEN / 2 - MAGNET_HOLE_DEPTH / 2, 0, 0)):
            # rotation=(0,90,0) → 원기둥 Z축이 X 방향으로
            Cylinder(radius=MAGNET_HOLE_DIA / 2,
                     height=MAGNET_HOLE_DEPTH,
                     align=ALIGN_CENTERED,
                     rotation=(0, 90, 0),
                     mode=Mode.SUBTRACT)
        # 자석 홈 — -X 끝
        with Locations((-PILLAR_LEN / 2 + MAGNET_HOLE_DEPTH / 2, 0, 0)):
            Cylinder(radius=MAGNET_HOLE_DIA / 2,
                     height=MAGNET_HOLE_DEPTH,
                     align=ALIGN_CENTERED,
                     rotation=(0, 90, 0),
                     mode=Mode.SUBTRACT)
    return p.part


if __name__ == "__main__":
    finalize_iteration(build_pillar())

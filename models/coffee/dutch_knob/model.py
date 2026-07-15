"""dutch_knob — 더치(콜드브루) 기구 노브 확장 클램프.

기구의 작은 노브를 바깥에서 감싸 손잡이를 크게 확장한다.
두 반쪽(클램쉘)이 노브를 감싸고 자석으로 결합. 좌우 대칭 2피스가
한 파트에 포함되어 함께 출력된다.
(legacy/etc/dutch_nobe.py 이관, 오타 교정 nobe→knob + 파라미터 정리)
"""

from build123d import (
    Align,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Cylinder,
    Locations,
    Mode,
    Plane,
    Polyline,
    extrude,
    make_face,
    mirror,
)

from models._lib.iter import finalize_iteration

# ---- 외형 (반쪽 블록) ----
OUTER_W = 17.5     # 폭 (X)
OUTER_D = 45.0     # 깊이 (Y)
OUTER_H = 12.5     # 높이 (Z)

# ---- 앞/뒤 사선 깎기 (X방향 기둥, 단면 직각삼각형) ----
SLOPE_Z = 10.0     # 앞면(-Y)에서 사선 시작 Z
SLOPE_LEN_Y = 30.0 # Y방향 깎는 길이

# ---- 감싸는 노브 (X축 원기둥) ----
KNOB_D = 13.5      # 노브 지름
KNOB_LEN = 12.0    # 노브 폭

# ---- 축 (Y축 원기둥) ----
SHAFT_D = 5.3
SHAFT_LEN = 42.0

# ---- 자석 구멍 (Z방향, Ø5 자석 압입) ----
MAGNET_D = 4.98
MAGNET_DEPTH = 5.3   # 주 구멍 깊이
MAGNET_DEPTH_END = 2.2  # 끝(단독) 구멍 깊이
MAGNET_POS = [(8.5, 10), (8.5, -10)]  # 주 자석 위치 (미러로 반대쪽도 생성)
MAGNET_POS_END = (0, -26)             # 앞 끝 자석

# ---- 박스 배치 계산 ----
BOX_FRONT_Y = -SLOPE_LEN_Y
BOX_BACK_Y = OUTER_D - SLOPE_LEN_Y
BOX_CENTER_Y = (BOX_FRONT_Y + BOX_BACK_Y) / 2  # -10
BOX_CENTER_X = OUTER_W / 2 - 5                 # 3.75 (왼쪽 5mm만 남김)
BOX_BOTTOM_Z = -OUTER_H


def build_knob():
    with BuildPart() as part:
        with Locations((BOX_CENTER_X, BOX_CENTER_Y, BOX_BOTTOM_Z)):
            Box(OUTER_W, OUTER_D, OUTER_H, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 앞쪽 사선 (직각삼각형 컷)
        with BuildSketch(Plane.YZ.offset(BOX_CENTER_X)):
            with BuildLine():
                Polyline(
                    (BOX_FRONT_Y, BOX_BOTTOM_Z + SLOPE_Z),
                    (BOX_FRONT_Y, BOX_BOTTOM_Z),
                    (0, BOX_BOTTOM_Z),
                    close=True,
                )
            make_face()
        extrude(amount=OUTER_W / 2 + 1, both=True, mode=Mode.SUBTRACT)
        # 뒤쪽 사선 (Y=0 기준 미러 대칭)
        with BuildSketch(Plane.YZ.offset(BOX_CENTER_X)):
            with BuildLine():
                Polyline(
                    (SLOPE_LEN_Y, BOX_BOTTOM_Z + SLOPE_Z),
                    (SLOPE_LEN_Y, BOX_BOTTOM_Z),
                    (0, BOX_BOTTOM_Z),
                    close=True,
                )
            make_face()
        extrude(amount=OUTER_W / 2 + 1, both=True, mode=Mode.SUBTRACT)

        # 노브 감싸는 반원 홈 (X축 원기둥)
        with Locations(Plane.YZ):
            Cylinder(KNOB_D / 2, KNOB_LEN, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
        # 축 채널 (Y축 원기둥)
        with Locations(Plane.XZ):
            Cylinder(SHAFT_D / 2, SHAFT_LEN, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # 자석 구멍 (위에서 아래로)
        with Locations(*[(x, y, 0) for x, y in MAGNET_POS]):
            Cylinder(MAGNET_D / 2, MAGNET_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
        with Locations((MAGNET_POS_END[0], MAGNET_POS_END[1], 0)):
            Cylinder(MAGNET_D / 2, MAGNET_DEPTH_END, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

        # X=-10 기준 미러 → 반대쪽 반쪽 생성 (두 클램쉘)
        mirror(about=Plane.YZ.offset(-10))

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_knob())

"""shrimp_scoop / handle — ㄱ자 분리형 손잡이.

기둥: 1(radial) × 3.5(tangential) × 40(Z), 단면 회전된 형태
grip: 기둥 윗부분 +X 면에서 +X(외측 radial)로 10mm 뻗는 가로 슬랩
      column 단면(1 thin × 3.5 wide)이 그대로 유지: thin=vertical(Z=1), wide=tangential(Y=3.5)

native frame (사용 자세):
  column: X=±0.5 (radial 얇음), Y=±1.75 (tangential 넓음), Z=0..40
  grip  : X=0.5..10.5, Y=±1.75 (column 과 동일 폭), Z=39..40 (top-flush, 1mm 두께)
"""

from build123d import Align, Box, BuildPart, Locations

from models._lib.iter import finalize_iteration


# 단면 1×3.5 (column)
RECT_RADIAL = 1.0               # 단면 radial (얇음, 사용 시 X)
RECT_TANG = 3.5                 # 단면 tangential (넓음, 사용 시 Y)

# 수직 column
COL_HEIGHT = 40.0

# 수평 grip (+X 외측 radial, 가로 슬랩 — column 단면 그대로 꺾임)
GRIP_LEN = 10.0                 # +X 길이
GRIP_THIN_Z = 1.0               # grip 의 vertical 두께 (column 의 thin 유지)


def build_handle():
    with BuildPart() as handle:
        # 수직 column (X=±0.5, Y=±1.75, Z=0..40)
        Box(RECT_RADIAL, RECT_TANG, COL_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        # 수평 grip: column +X 면(X=+0.5)에서 +X 로 10mm, top-flush
        # wide(3.5) 가 tangential 유지, thin(1) 이 vertical 로 회전
        with Locations((RECT_RADIAL / 2, 0, COL_HEIGHT - GRIP_THIN_Z)):
            Box(GRIP_LEN, RECT_TANG, GRIP_THIN_Z,
                align=(Align.MIN, Align.CENTER, Align.MIN))
    return handle.part


if __name__ == "__main__":
    finalize_iteration(build_handle())

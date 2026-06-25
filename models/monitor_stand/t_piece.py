"""monitor_stand / t_piece — 뒤집힌 T (세로 기둥 + 가로 받침).

좌표계: X=좌우, Y=깊이(모니터→뒤), Z=수직(책상=0).
기둥은 X 중심(0), 받침은 X 중심+기둥 앞 Y 옵셋.

  z=0..FOOT_H        : 받침 (X=±FOOT_W/2, Y=0..FOOT_D)
  z=0..COL_TOP_Z     : 기둥 (X=±COL_W/2, Y=COL_Y_FRONT..COL_Y_FRONT+COL_D)
                       — 두 박스의 union 으로 ⊥ 형태

추가 feature:
  M4 through-hole + counterbore: 모니터 결합 (Y 관통)
  슬롯 (+X 면) × 2: 기둥/받침에 각각 1개, pillar 가 끼움
  자석 홈: 각 슬롯 깊은 면에 1개

좌측 T 는 그대로, 우측 T 는 X 미러 + 평행이동으로 사용.
"""

from build123d import Align, Box, BuildPart, Cylinder, Locations, Mode

from models._lib.iter import finalize_iteration


ALIGN_CENTERED = (Align.CENTER, Align.CENTER, Align.CENTER)

# ============================================================
# 치수 파라미터
# ============================================================

# 기둥
COL_W = 20                # X 폭
COL_D = 20                # Y 깊이
COL_TOP_Z = 142           # 기둥 top z

# 받침 — 23.8" 모니터(2.15kg). 출력 시 측면 lying 위해 X 두께를 column 과 통일
FOOT_W = COL_W            # X 폭 = 20 (기둥과 같음 — 측면 lying 출력 시 평면 정렬)
FOOT_D = 200              # Y 깊이 (앞으로 길게 — 앞 140, 뒤 60)
FOOT_H = 20               # Z 두께

# 기둥의 받침 위 Y 위치 (받침 앞=0)
COL_Y_FRONT = 140         # 기둥 앞면 Y (받침 앞으로 140mm 돌출)
COL_Y_BACK = COL_Y_FRONT + COL_D   # 160
COL_Y_CENTER = (COL_Y_FRONT + COL_Y_BACK) / 2   # 150

# M4 결합
MONITOR_BOTTOM_Z = FOOT_H + 20            # 모니터 바닥 z (foot 위로 20mm 클리어런스) = 40
M4_HOLE_Z = MONITOR_BOTTOM_Z + 87         # 모니터 나사홀 위치 = 127
M4_HOLE_DIA = 5.0                         # M4 free fit — 위치 오차 ±0.5mm radial 흡수
# M4×15 반구머리 십자홈 (PH2, head 두께 2.4) + 평와셔 Ø9×0.5 사용 가정.
# 깊은 counterbore 로 shaft 끝이 모니터에 4.1mm 진입하도록 column 안에 dead-space 형성.
M4_COUNTERBORE_DIA = 9.5                  # 와셔 Ø9 + 0.5 여유
M4_COUNTERBORE_DEPTH = 9.1                # 20 - 4.1 - (15-shaft 진입) = 9.1

# 슬롯
SLOT_DEPTH = 10           # X 깊이 (slot opens at +X face, extends -X)
SLOT_TOL = 0.2            # 슬롯 ↔ pillar 총 슬랙 (FDM 변동 흡수 + 손쉬운 삽입)
SLOT_W = 15.0 + SLOT_TOL  # Y (pillar 단면 + tol)
SLOT_H = 15.0 + SLOT_TOL  # Z

# 슬롯 위치
COL_SLOT_Z_CENTER = 100   # 기둥 슬롯의 z 중심
FOOT_SLOT_Y_CENTER = 180  # 받침 슬롯의 y 중심 (기둥 뒤 160 과 받침 뒤 200 사이)
FOOT_SLOT_Z_CENTER = FOOT_H / 2  # = 10

# 자석 (5×5mm)
MAGNET_HOLE_DIA = 5.1     # 5 + 0.1 TOL
MAGNET_HOLE_DEPTH = 5.1


def _add_slot_with_magnet(slot_x_face_x, slot_y_center, slot_z_center):
    """+X 면(x = slot_x_face_x)에서 -X 방향으로 깊이 SLOT_DEPTH 슬롯 + 자석 홈."""
    # 슬롯
    with Locations((slot_x_face_x, slot_y_center, slot_z_center)):
        Box(SLOT_DEPTH, SLOT_W, SLOT_H,
            align=(Align.MAX, Align.CENTER, Align.CENTER),
            mode=Mode.SUBTRACT)
    # 자석 홈 — 슬롯 깊은 면(x = slot_x_face_x - SLOT_DEPTH)에서 -X 방향으로 추가
    magnet_x = slot_x_face_x - SLOT_DEPTH - MAGNET_HOLE_DEPTH / 2
    with Locations((magnet_x, slot_y_center, slot_z_center)):
        Cylinder(radius=MAGNET_HOLE_DIA / 2,
                 height=MAGNET_HOLE_DEPTH,
                 align=ALIGN_CENTERED,
                 rotation=(0, 90, 0),
                 mode=Mode.SUBTRACT)


def build_t_piece():
    with BuildPart() as t:
        # 받침 — y=0..FOOT_D, x=±FOOT_W/2, z=0..FOOT_H
        with Locations((0, FOOT_D / 2, FOOT_H / 2)):
            Box(FOOT_W, FOOT_D, FOOT_H, align=ALIGN_CENTERED)
        # 기둥 — y=COL_Y_FRONT..COL_Y_BACK, x=±COL_W/2, z=0..COL_TOP_Z
        with Locations((0, COL_Y_CENTER, COL_TOP_Z / 2)):
            Box(COL_W, COL_D, COL_TOP_Z, align=ALIGN_CENTERED)

        # M4 through-hole — 기둥 Y 방향 관통
        with Locations((0, COL_Y_CENTER, M4_HOLE_Z)):
            Cylinder(radius=M4_HOLE_DIA / 2,
                     height=COL_D + 2,
                     align=ALIGN_CENTERED,
                     rotation=(-90, 0, 0),     # Z축 → Y축
                     mode=Mode.SUBTRACT)
        # Counterbore — 기둥 뒷면(+Y 끝)에서 -Y 방향으로
        cb_y_center = COL_Y_BACK - M4_COUNTERBORE_DEPTH / 2
        with Locations((0, cb_y_center, M4_HOLE_Z)):
            Cylinder(radius=M4_COUNTERBORE_DIA / 2,
                     height=M4_COUNTERBORE_DEPTH,
                     align=ALIGN_CENTERED,
                     rotation=(-90, 0, 0),
                     mode=Mode.SUBTRACT)

        # 기둥 슬롯 (+X 면, 기둥 Y 중심, z=COL_SLOT_Z_CENTER)
        _add_slot_with_magnet(COL_W / 2, COL_Y_CENTER, COL_SLOT_Z_CENTER)

        # 받침 슬롯 (+X 면, 받침 뒤쪽 y, 받침 z 중심)
        _add_slot_with_magnet(FOOT_W / 2, FOOT_SLOT_Y_CENTER, FOOT_SLOT_Z_CENTER)

    return t.part


if __name__ == "__main__":
    finalize_iteration(build_t_piece())

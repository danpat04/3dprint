"""monitor_stand / assembly — 2 T + 2 pillar 결합 상태.

좌측 T: t_piece 그대로 (column center x=0)
우측 T: X 미러 + 평행이동 (column center x=M4_SPACING=74.4)
상단 pillar: y=COL_Y_CENTER, z=COL_SLOT_Z_CENTER (기둥 슬롯에 끼움)
하단 pillar: y=FOOT_SLOT_Y_CENTER, z=FOOT_SLOT_Z_CENTER (받침 슬롯에 끼움)
"""

from build123d import Plane, Pos, mirror

from models._lib.iter import finalize_iteration
from models.monitor_stand.pillar import build_pillar
from models.monitor_stand.t_piece import (
    COL_SLOT_Z_CENTER,
    COL_Y_CENTER,
    FOOT_SLOT_Y_CENTER,
    FOOT_SLOT_Z_CENTER,
    build_t_piece,
)


# M4 홀 간격 = 두 column center 간격
M4_SPACING = 74.4

left_t = build_t_piece()
# 우측 T: X 미러 후 +M4_SPACING 이동
right_t = Pos(M4_SPACING, 0, 0) * mirror(build_t_piece(), Plane.YZ)

# Pillar — center at x=M4_SPACING/2 (두 column 중심 사이)
PILLAR_X = M4_SPACING / 2

top_pillar = Pos(PILLAR_X, COL_Y_CENTER, COL_SLOT_Z_CENTER) * build_pillar()
foot_pillar = Pos(PILLAR_X, FOOT_SLOT_Y_CENTER, FOOT_SLOT_Z_CENTER) * build_pillar()

assembly = left_t + right_t + top_pillar + foot_pillar

finalize_iteration(assembly)

"""tarp_magnet_holder / assembly — bottom + top 좌우 분리 배치 (출력/export 용).

두 파츠를 각자 standalone 자세(z=0)로 좌우 나란히 배치.
  bottom: 좌측 (x=-22.5), top: 우측 (x=+22.5)
결합(안착) 뷰로 보려면 하단 주석 참고.
"""

from build123d import Pos

from models._lib.iter import finalize_iteration
from models.camping.tarp_magnet_holder.bottom import TOTAL_H as BOTTOM_TOP_Z, build_bottom
from models.camping.tarp_magnet_holder.top import SKIRT_H, build_top


bottom = build_bottom()
top = build_top()

# 좌우 분리 배치 (중심 간격 45mm)
GAP = 45.0
layout = Pos(-GAP / 2, 0, 0) * bottom + Pos(GAP / 2, 0, 0) * top

finalize_iteration(layout)

# --- 결합(안착) 뷰로 보고 싶을 때 ---
# seat_z = BOTTOM_TOP_Z - SKIRT_H  # 5.2 - 4.2 = 1.0
# finalize_iteration(bottom + Pos(0, 0, seat_z) * top)

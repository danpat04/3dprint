"""shrimp_scoop / assembly — bowl + ring + handle 좌우 분리 배치 (출력/export 용).

기본: 좌우 분리 (각 파츠 standalone 자세, z=0). exports 의 .step 도 분리 상태.
결합 뷰는 하단 주석 참고.
"""

from build123d import Pos

from models._lib.iter import finalize_iteration
from models.shrimp_scoop.bowl import (
    FLOOR_H, RING_TOP_Z, SOCKET_BOTTOM_Z, SOCKET_INNER_X, SOCKET_OUTER_X, build_bowl,
)
from models.shrimp_scoop.handle import build_handle
from models.shrimp_scoop.ring import build_ring


bowl = build_bowl()
ring = build_ring()
handle = build_handle()

# 좌우 분리 배치 (bowl 중앙, ring 좌측, handle 우측)
layout = bowl + Pos(-45, 0, 0) * ring + Pos(45, 0, 0) * handle

finalize_iteration(layout)

# --- 결합(안착) 뷰로 보고 싶을 때 ---
# socket_x_center = (SOCKET_INNER_X + SOCKET_OUTER_X) / 2
# ring_seated = Pos(0, 0, FLOOR_H) * ring
# handle_seated = Pos(socket_x_center, 0, SOCKET_BOTTOM_Z) * handle  # floor 까지 깊이 삽입
# finalize_iteration(bowl + ring_seated + handle_seated)

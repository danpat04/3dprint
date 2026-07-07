"""camping_cutlery_holder — 조립: 통(holder) + S후크 2개.

hook 은 조립 좌표(절대)로 만들어지므로 x(±HOOK_X) 로만 배치한다.
EXPLODE > 0 이면 후크를 결합 위치에서 위로 빼서 분해도(결합 구조 확인)로 렌더.
실제 export/조립 확인은 EXPLODE = 0.
"""

from build123d import Pos

from models._lib.iter import finalize_iteration
from models.camping_cutlery_holder.holder import build_holder
from models.camping_cutlery_holder.hook import build_hook
from models.camping_cutlery_holder.params import HOOK_X

EXPLODE = 0.0    # 분해도 거리(mm). 0 = 완전 조립

holder = build_holder()
hook = build_hook()

asm = holder
for sx in (-HOOK_X, HOOK_X):
    # 위로 빼고(+Z) 뒤로 살짝(-Y) → 통이 위에서 내려와 끼워지는 방향을 보여줌
    asm += Pos(sx, -EXPLODE * 0.35, EXPLODE) * hook

finalize_iteration(asm)

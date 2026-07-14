"""tamper_stand — 커피 탬퍼 거치대.

탬퍼를 올려두는 단순 링. 외경/내경 원통 차집합.
(legacy/coffee/tamper.py 를 자율 워크플로로 이관)
"""

from build123d import Align, BuildPart, Cylinder, Mode

from models._lib.iter import finalize_iteration

# ---- 치수 (mm) ----
OUTER_D = 70.0     # 외경
INNER_D = 59.5     # 내경 (탬퍼 안착)
HEIGHT = 10.0      # 높이

OUTER_R = OUTER_D / 2
INNER_R = INNER_D / 2
ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    Cylinder(OUTER_R, HEIGHT, align=ALIGN_BOTTOM)
    Cylinder(INNER_R, HEIGHT, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)

finalize_iteration(part.part)

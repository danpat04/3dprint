"""shrimp_scoop / ring — 망 클램프 링 (슬로프 + 망 안착 돌기 + boss notch).

cavity Ø27.7 에 0.05 공차로 안착, 망(Ø25 노출)을 floor 에 누름 고정.
위쪽 면이 외경(높음 z=2.0)에서 내경(낮음 z=LIP_H)으로 흘러내리는 cone 슬로프.
아래쪽 면에 12개 원뿔 음각(암) — 볼의 수와 맞물려 망을 꽉 잡음.
+X 쪽에 핸들 boss 통과용 notch — 삽입 경로 클리어런스.
  z=0..0.3   : 내경 쪽 직벽 lip
  z=0.3..2.0 : 위쪽 cone 슬로프
  z=0..0.65  : 망 클램프 cone 음각 12개 (15°/45°/.../345°, notch 회피)
  +X notch   : 새 boss 위치(x≥12.8, y=±2.825) 전체 z 관통
"""

import math

from build123d import Align, Box, BuildPart, Cone, Cylinder, Locations, Mode

from models._lib.iter import finalize_iteration


ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

CAVITY_D = 27.7                  # bowl wall 1.5mm 로 두꺼워져 cavity 축소
FIT_TOL = 0.05
OUTER_D = CAVITY_D - FIT_TOL    # 27.65
INNER_D = 25.0                   # 망 노출 Ø와 일치
HEIGHT = 2.0                     # 큰 cone 수용 위해 증가 (was 1.5)
LIP_H = 1.7                      # 내경 직벽 — 슬로프 매우 완만(~12.8°), boss 쪽 벽 수직 두께 ↑

# 망 클램프 cone (암, recess) — bowl 의 수 와 매칭, 12개 15° offset
N_CLAMP = 12
CLAMP_D = 0.8 + FIT_TOL          # 기저 지름 (bowl 수 0.8 + 0.05 = 0.85)
CLAMP_H = 0.6 + FIT_TOL          # 깊이 (bowl 수 0.6 + 0.05 = 0.65)
CLAMP_R = 13.15                  # 새 annular 중간 (bowl 과 동일)
CLAMP_ANG_OFFSET = math.pi / 12  # 15° offset → notch 회피

# 핸들 boss 통과 notch (+X 측, 삽입 경로용)
# 새 boss inner = 13.30 (socket inner 와 동일, 추가 돌출 없음) → notch 도 적게 침범
NOTCH_X_MIN = 13.25              # 13.30 - 0.05 (was 12.80)
NOTCH_Y_HALF = 2.825             # 2.775 + 0.05


def build_ring():
    with BuildPart() as ring:
        # 기본 annular ring (full height)
        Cylinder(radius=OUTER_D / 2, height=HEIGHT, align=ALIGN_BOTTOM)
        Cylinder(radius=INNER_D / 2, height=HEIGHT,
                 align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        # 위쪽 cone 슬로프: lip 위에서 외경 top 으로 깎아 내려감
        # 결과: top 면이 외경(z=1.5) 에서 내경(z=LIP_H) 으로 흘러내림
        with Locations((0, 0, LIP_H)):
            Cone(bottom_radius=INNER_D / 2, top_radius=OUTER_D / 2,
                 height=HEIGHT - LIP_H, align=ALIGN_BOTTOM, mode=Mode.SUBTRACT)
        # 망 클램프 cone 음각 (10개 — N_CLAMP 중 boss 양옆 i=0(15°)·i=11(345°) 제외)
        for i in range(N_CLAMP):
            if i in (0, N_CLAMP - 1):
                continue                  # boss 와 너무 가까워 (0.225mm 간격) 슬라이스 간섭
            ang = 2 * math.pi * i / N_CLAMP + CLAMP_ANG_OFFSET
            cx = CLAMP_R * math.cos(ang)
            cy = CLAMP_R * math.sin(ang)
            with Locations((cx, cy, 0)):
                Cone(bottom_radius=CLAMP_D / 2, top_radius=0,
                     height=CLAMP_H,
                     align=ALIGN_BOTTOM,
                     mode=Mode.SUBTRACT)
        # +X 측 핸들 boss 통과용 notch (전체 ring 높이 관통)
        with Locations((NOTCH_X_MIN, 0, 0)):
            Box(20, NOTCH_Y_HALF * 2, HEIGHT,
                align=(Align.MIN, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT)
    return ring.part


if __name__ == "__main__":
    finalize_iteration(build_ring())

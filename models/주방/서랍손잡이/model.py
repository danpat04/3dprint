"""서랍손잡이 — 앞판 윗 모서리에 끼우는 클립형 손잡이.

나사 없이 형상만으로 버틴다. 당기는 힘은 앞으로 작용하는데 안쪽 다리가 앞판 뒤에
걸려 있어 그 방향으로는 빠지지 않는다. 빠지려면 위로 들어 올려야 한다.

**그래서 U 자가 위로 열려야 한다.** 손가락이 위에서 내려와 팔을 아래로 누르며 앞으로
당기게 되고, 누르는 힘이 클립을 앉혀준다. 반대로(팔이 위, 립이 아래) 만들면 손가락이
팔 아랫면을 밀어 올리게 되어 **쓰는 동작이 곧 빠지는 동작**이 된다.

옆모습(단면)을 좌우 폭만큼 압출한 형태다. 눕혀서 출력하면 모든 면이 수직이라
서포트가 필요 없고, 당기는 힘이 단면 안쪽 방향이라 압출선이 그대로 받는다.

좌표: 앞판 윗-앞 모서리가 원점.
  x 좌우 (가운데 0)   y 앞뒤 (**앞이 음수**, 앞판이 0~15)   z 위아래 (앞판 위가 0)
"""

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Locations,
    fillet,
)

from models._lib.iter import finalize_iteration

# ---- 서랍 앞판 (실측) ----
PANEL_T = 15.0         # 앞판 두께
FIT = 0.1              # 슬롯 여유 (한쪽 0.05) — 끼운 뒤 안 움직여야 하는 자리라 조였다

# ---- 전체 ----
WIDTH = 100.0          # 좌우 폭
REACH = 50.0           # 앞판 앞면에서 앞으로

# ---- 클립 ----
WALL = 4.0             # 클립 살 두께
BRIDGE_T = 5.0         # 윗 모서리를 덮는 두께
INNER_DROP = 60.0      # 안쪽 다리가 앞판 뒤로 내려오는 길이 — 이게 걸림쇠다.
                       # 길면 빠지기까지 들어올려야 하는 거리가 늘고, 앞으로 당길 때
                       # 앞판을 무는 힘이 27N→8N 으로 줄어 자국이 안 남는다.
OUTER_DROP = 30.0      # 바깥 다리. 회전을 막고 U 자의 뒤쪽 벽이 된다

# ---- 손잡이 ----
ARM_T = 6.0            # 손가락을 받치는 팔 두께
LIP_T = 6.0            # 앞쪽 립 두께
LIP_UP = 16.0          # 립이 **위로** 솟는 높이 — 손가락이 여기를 앞으로 민다
GRIP_R = 2.0           # 손이 닿는 모서리 라운드

# ---- 파생 ----
Y_IN = -FIT / 2                    # 바깥 다리 안쪽 면
Y_OUT = PANEL_T + FIT / 2          # 안쪽 다리 안쪽 면
ARM_TOP = -OUTER_DROP              # 팔 윗면 = 손가락이 닿는 바닥
ARM_BOT = ARM_TOP - ARM_T          # 팔 아랫면 = 전체 최하단
LIP_TOP = ARM_TOP + LIP_UP         # 립 윗면

MIN3 = (Align.MIN, Align.MIN, Align.MIN)


def _box(y0, y1, z0, z1):
    """좌우 폭 전체를 가로지르는 박스. 옆모습 단면을 그대로 옮긴다."""
    with Locations((-WIDTH / 2, y0, z0)):
        Box(WIDTH, y1 - y0, z1 - z0, align=MIN3)


def build_handle():
    with BuildPart() as part:
        # ---- 클립 ----
        _box(Y_IN - WALL, Y_OUT + WALL, 0.0, BRIDGE_T)      # 윗 모서리 덮개
        _box(Y_OUT, Y_OUT + WALL, -INNER_DROP, 0.0)         # 안쪽 다리 (걸림쇠)
        _box(Y_IN - WALL, Y_IN, -OUTER_DROP, 0.0)           # 바깥 다리

        # ---- 손잡이 (위로 열린 U) ----
        _box(-REACH, Y_IN, ARM_BOT, ARM_TOP)                # 손가락을 받치는 팔
        _box(-REACH, -REACH + LIP_T, ARM_TOP, LIP_TOP)      # **위로** 솟는 립

        # 손이 닿는 모서리만 둥글린다 — 매일 쥐는 곳이라
        near = lambda v, t: abs(v - t) < 1e-6
        grip = [e for e in part.edges().filter_by(Axis.X)
                if near(e.center().Z, LIP_TOP)                    # 립 윗면
                or near(e.center().Z, ARM_BOT)                    # 팔 아랫면
                or (near(e.center().Y, -REACH) and e.center().Z < ARM_TOP)]
        fillet(grip, GRIP_R)

    return part.part


if __name__ == "__main__":
    finalize_iteration(build_handle())

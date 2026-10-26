from build123d import *
from models._lib.iter import finalize_iteration

# 참고: feedback 사진의 클립 (짧은 말굽형, 윗막대 슬롯, 입구 벌어짐). 팔은 얇게 해 휘기 쉽게 함
HOSE_D = 7.5             # 클립이 끼워지는 부속 목 외경
CLEAR = 0.15
T = 1.0                       # 끼워지는 틈 두께
SLOT_D = HOSE_D + 2 * CLEAR   # 7.8 구멍
MOUTH = 6.5                   # 입구 최소 폭 (딸깍 고정)
WALL = 3.3                    # 둘레 벽 두께
W = SLOT_D + 2 * WALL         # 외폭 ≈14.4
GRIP = 4.0                    # 잡기 쉽게 위쪽 연장
TOP = SLOT_D / 2 + WALL + GRIP  # 중심에서 윗면까지
BOT = 6.5                     # 중심에서 팔 끝까지
FLARE_X = 4.6                 # 입구 벌어짐 끝 반폭
FLARE_Y = 3.0                 # 벌어짐 시작 높이(중심 아래)
ARM_W = 2.0                   # 팔 두께(휘는 부분)

with BuildPart() as part:
    with BuildSketch():
        with Locations((0, (TOP - BOT) / 2)):
            Rectangle(W, TOP + BOT)
        fillet(vertices().filter_by_position(Axis.Y, TOP - 0.01, TOP + 0.01), 2.0)
        Circle(SLOT_D / 2, mode=Mode.SUBTRACT)
        with Locations((0, -BOT / 2)):
            Rectangle(MOUTH, BOT + 0.01, mode=Mode.SUBTRACT, align=(Align.CENTER, Align.CENTER))
        # 삽입부 벌어짐
        with Locations((-FLARE_X, -FLARE_Y)):
            h = BOT + 1 - FLARE_Y
            yc = (-FLARE_Y - BOT - 1) / 2   # Polygon 은 bbox 중심 기준으로 놓인다
        with Locations((0, yc)):
            Polygon((-MOUTH / 2, -FLARE_Y - yc), (-FLARE_X, -BOT - 1 - yc),
                    (FLARE_X, -BOT - 1 - yc), (MOUTH / 2, -FLARE_Y - yc), mode=Mode.SUBTRACT)
        # 팔을 얇게: 중심 아래 바깥쪽을 깎아 휘기 쉽게 (위는 두껍게 유지)
        ARM_OUT = SLOT_D / 2 + ARM_W
        for sx in (-1, 1):
            with Locations((sx * (ARM_OUT + W / 2 + 0.5) / 2, -1.0 - (BOT + 2) / 2)):
                Rectangle(W / 2 - ARM_OUT + 0.5, BOT + 2, mode=Mode.SUBTRACT)
        # 윗막대 슬롯
        with Locations((0, SLOT_D / 2 + WALL / 2 + GRIP / 2)):
            SlotOverall(9.0, 1.1, mode=Mode.SUBTRACT)
        # 둥글리기: 계단 모서리(오목/볼록) + 팔 끝
        eps = 0.01
        step = vertices().filter_by_position(Axis.Y, -1.0 - eps, -1.0 + eps)
        concave = step.filter_by(lambda v: abs(abs(v.X) - ARM_OUT) < eps)
        convex = step.filter_by(lambda v: abs(abs(v.X) - W / 2) < eps)
        fillet(concave, 0.9)
        fillet(convex, 0.3)
        fillet(vertices().filter_by_position(Axis.Y, -BOT - eps, -BOT + eps), 0.5)
    extrude(amount=T)

p = part.part
assert abs(p.bounding_box().size.Z - T) < 1e-3
print(p.bounding_box().size)
finalize_iteration(p)

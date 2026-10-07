"""어린이변기커버_고리 — 고리판 / 받침판 / 관통 핀.

    uv run python -m models.화장실.어린이변기커버_고리.hook     조립 렌더
    uv run python -m models.화장실.어린이변기커버_고리.export   부품별 STEP

고리 면은 커버 면과 **평행**하다. 수직으로 세우면 커버를 변기에 올렸을 때
어른 변기나 앉은 아이와 부딪힌다.

## 핀을 왜 따로 뽑는가

갈래가 휠 때 생기는 인장은 핀 **축 방향**이다. 핀을 고리판에 붙여 세워 뽑으면
그 인장이 층을 가로질러 흐르고, 층간 결합은 재료 자체보다 훨씬 약하고
부러지듯 깨진다. 실제로 스냅이 걸리기 전에 갈래가 부러졌다.
핀만 떼어 **눕혀서** 뽑으면 인장이 압출선을 따라 흐른다.

## 왜 원통이 아니라 각기둥인가

눕힌 원통은 아랫배가 둥글어 반드시 서포트가 필요하다. 단면을 **수직 벽을 가진
각기둥**으로 만들면 눕혔을 때 위아래가 평평하고 옆면이 전부 수직이라
서포트가 한 군데도 필요 없다. 미늘이 벌어지는 방향도, 갈래가 휘는 방향도
전부 베드 평면 안쪽이라 오버행이 생기지 않는다.

갈래는 원통을 쪼갠 4 개가 아니라 납작한 **2 개**다. 버티는 힘은 401N → 204N
으로 줄지만, 세게 당기는 50N 에 대해 4 배 여유라 충분하다.

## 출력 방향

  고리판   판 면을 bed 에. 힘이 고리 → 목 → 원반 으로 **판 면 안쪽**을 흐른다
  받침판   **카운터보어가 위로** (평평한 면을 bed 에). 구멍이 넓어지며 올라가
           오버행이 없다
  핀       **눕혀서**. 조립 좌표는 축이 z 라, 슬라이서에서 눕히거나
           export 가 내보내는 print 방향 STEP 을 쓴다
"""

from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    Polygon,
    Circle,
    Compound,
    Cylinder,
    Location,
    Locations,
    Mode,
    Plane,
    Rectangle,
    chamfer,
    extrude,
    fillet,
    loft,
)

from models._lib.iter import finalize_iteration
from models.화장실.어린이변기커버_고리.params import (
    BASE_D,
    BASE_LEDGE_T,
    BASE_R,
    BASE_RECESS_W,
    BASE_SLOT_W,
    BASE_T,
    DETENT_H,
    DETENT_RAMP_IN,
    DETENT_RAMP_OUT,
    DETENT_Y,
    RELIEF_END,
    RELIEF_W,
    RELIEF_X,
    BLADE_CH,
    BLADE_T,
    BLADE_W,
    BOSS_BOT,
    COVER_T,
    DISC_D,
    EDGE_CH,
    EDGE_DIST,
    EDGE_R,
    GROOVE_D,
    GROOVE_H_END,
    GROOVE_H_OPEN,
    GROOVE_TOP,
    HOLE_D,
    LID_FIT,
    LID_FLOOR,
    LID_LEAD,
    LID_SKIRT,
    LID_WALL,
    NECK_W,
    PIN_HEAD_T,
    PIN_HEAD_W,
    PIN_SHANK_TOP,
    PLATE_BORE,
    PLATE_CB_D,
    PLATE_CB_T,
    PLATE_T,
    RING_CTR,
    RING_ID,
    RING_OD,
)

TOP = (Align.CENTER, Align.CENTER, Align.MAX)
BOT = (Align.CENTER, Align.CENTER, Align.MIN)


def build_ring_plate():
    """고리판 ① — 납작한 패들. 핀이 지나는 구멍과 머리 자리만 있다."""
    with BuildPart() as part:
        with BuildSketch() as sk:
            Circle(DISC_D / 2)                                   # 핀 둘레 원반
            with Locations((RING_CTR / 2, 0)):
                Rectangle(RING_CTR, NECK_W)                      # 목
            with Locations((RING_CTR, 0)):
                Circle(RING_OD / 2)                              # 고리 바깥
                Circle(RING_ID / 2, mode=Mode.SUBTRACT)          # 고리 구멍
        extrude(sk.sketch, amount=PLATE_T)

        # 목과 원반/고리가 만나는 오목 모서리 — 응력 집중을 없앤다
        inner = [e for e in part.edges().filter_by(Axis.Z)
                 if 0 < e.center().X < RING_CTR and abs(e.center().Y) > NECK_W / 2 - 0.01]
        if inner:
            fillet(inner, 3.0)

        # 윗 둘레는 라운드 — 손가락이 닿는 면이다
        fillet([e for e in part.edges() if abs(e.center().Z - PLATE_T) < 1e-6], EDGE_R)
        # 아랫 둘레는 모따기 — 이 면이 bed 다. 라운드면 1 층이 허공으로 나가 처진다
        chamfer([e for e in part.edges() if abs(e.center().Z) < 1e-6], EDGE_CH)

        # 핀이 지나는 구멍 + 머리 자리
        with Locations((0, 0, PLATE_T)):
            Cylinder(PLATE_BORE / 2, PLATE_T, align=TOP, mode=Mode.SUBTRACT)
            Cylinder(PLATE_CB_D / 2, PLATE_CB_T, align=TOP, mode=Mode.SUBTRACT)
    return part.part


def _sect(w, t, ch, z):
    """z 높이에 놓인 모따기 사각(팔각) 스케치."""
    with BuildSketch(Plane.XY.offset(z)) as sk:
        Rectangle(w, t)
        chamfer(sk.vertices(), ch)
    return sk.sketch


def build_pin():
    """관통 핀 ③ — 머리 + 날 + **홈** + 아래 턱. 조립 좌표(축 = z).

    홈은 받침판이 들어오는 +y 쪽이 깊고 −y 로 갈수록 얕아지는 **쐐기**다.
    밀어 넣을수록 받침판이 조여 축 유격이 0 이 된다.
    """
    with BuildPart() as part:
        # 머리
        extrude(_sect(PIN_HEAD_W, BLADE_T, BLADE_CH, PIN_SHANK_TOP), PIN_HEAD_T)
        # 날 + 아래 턱을 통짜로
        extrude(_sect(BLADE_W, BLADE_T, BLADE_CH, BOSS_BOT), PIN_SHANK_TOP - BOSS_BOT)

        # 홈 — YZ 평면의 사다리꼴을 x 로 밀어 깎는다.
        # 사다리꼴 윗변이 GROOVE_TOP 에 있어 날은 건드리지 않는다.
        # (스케치 local x = global y, local y = global z)
        # 높이 1.75 / 2.10 은 **핀 가장자리(y = ∓2.8)** 에서의 값이다.
        # 스케치는 ±5 까지 그리므로 같은 기울기로 연장해 둔다
        half = BLADE_T / 2
        slope = (GROOVE_H_OPEN - GROOVE_H_END) / BLADE_T
        mid = (GROOVE_H_OPEN + GROOVE_H_END) / 2
        h_far, h_near = mid + slope * 5, mid - slope * 5
        with BuildSketch(Plane.YZ) as gs:
            Polygon((-5, GROOVE_TOP),
                    (5, GROOVE_TOP),
                    (5, GROOVE_TOP - h_far),
                    (-5, GROOVE_TOP - h_near),
                    align=None)
        extrude(gs.sketch, 12, both=True, mode=Mode.SUBTRACT)

        # 홈 바닥 기둥을 되살린다 — 받침판 슬롯이 물릴 자리
        with BuildSketch(Plane.XY.offset(BOSS_BOT)) as cs:
            Circle(GROOVE_D / 2)
        extrude(cs.sketch, GROOVE_TOP - BOSS_BOT)
    return part.part


def _slot(width, depth, z):
    """+y 쪽으로 열린 U 자 슬롯 스케치. 닫힌 끝은 원점의 반원."""
    with BuildSketch(Plane.XY.offset(z)) as sk:
        with Locations((0, depth / 2)):
            Rectangle(width, depth)
        Circle(width / 2)
    return sk.sketch


def build_base_plate():
    """받침판 ② — 자체 좌표: z=0 바깥면, z=BASE_T 가 커버 쪽.

    윗 구간(BASE_LEDGE_T)에 좁은 슬롯, 아래 구간에 넓은 통로.
    커버 밑에서 **옆으로 밀어** 핀의 홈에 끼운다. 핀의 아래 턱이
    좁은 슬롯의 아랫면을 밀어 올리는 것이 유일한 하중 경로다.
    """
    with BuildPart() as part:
        Cylinder(BASE_D / 2, BASE_T, align=BOT)
        # 좁은 슬롯 — 홈에 물리는 자리
        extrude(_slot(BASE_SLOT_W, BASE_D, BASE_T - BASE_LEDGE_T),
                BASE_LEDGE_T, mode=Mode.SUBTRACT)
        # 넓은 통로 — 아래 턱이 지나간다
        extrude(_slot(BASE_RECESS_W, BASE_D, 0.0),
                BASE_T - BASE_LEDGE_T, mode=Mode.SUBTRACT)

        # 릴리프 슬롯 — 양쪽 턱을 외팔보(스프링 핑거)로 만든다.
        # 이게 없으면 통원반이라 돌기를 넘어갈 수가 없다
        for sx in (1, -1):
            with BuildSketch(Plane.XY) as rs:
                with Locations((sx * RELIEF_X, (BASE_D - RELIEF_END) / 2 + RELIEF_END)):
                    Rectangle(RELIEF_W, BASE_D - RELIEF_END)
                with Locations((sx * RELIEF_X, RELIEF_END)):
                    Circle(RELIEF_W / 2)
            extrude(rs.sketch, BASE_T, mode=Mode.SUBTRACT)

        # 걸림 돌기 — 윗 구간(슬롯 쪽)에만. 아래 통로를 막으면 턱이 못 지나간다.
        # 양쪽 다 경사지되 각도가 다르다. 램프를 넘는 힘은 N·tan(경사각) 이라
        # 들어오는 쪽 30도(쉽게), 나가는 쪽 60도(잘 안 빠지게)
        half = BASE_SLOT_W / 2
        for sx in (1, -1):
            with BuildSketch(Plane.XY.offset(BASE_T - BASE_LEDGE_T)) as ds:
                Polygon((sx * half, DETENT_Y + DETENT_RAMP_IN),
                        (sx * (half - DETENT_H), DETENT_Y),
                        (sx * half, DETENT_Y - DETENT_RAMP_OUT),
                        align=None)
            extrude(ds.sketch, BASE_LEDGE_T)

        # 바깥 둘레만 둥글린다. 슬롯 때문에 직선 모서리가 섞여 있어
        # e.radius 가 터지므로 중심에서의 거리로 고른다
        bot = [e for e in part.edges().filter_by(Axis.Z, reverse=True)
               if abs(e.center().Z) < 1e-6
               and abs(e.center().to_tuple()[0] ** 2 + e.center().to_tuple()[1] ** 2
                       - (BASE_D / 2) ** 2) < 1.0]
        # 릴리프 슬롯이 둘레를 토막내서 필렛이 안 걸릴 수 있다. 미관용이라 건너뛴다
        if bot:
            try:
                fillet(bot, BASE_R)
            except Exception:
                pass
    return part.part


def build_lid():
    """마감 뚜껑 ④ — 받침판 옆면을 물는 얕은 컵. **기능 없음, 미관용.**

    자체 좌표: z=0 이 바깥(변기 시트 쪽) 바닥, 위가 받침판 쪽.
    받침판 설계는 건드리지 않고 바깥에서 씌운다.
    """
    inner = BASE_D - LID_FIT                     # 치마 안지름 — 간섭 끼움
    with BuildPart() as part:
        Cylinder((inner + 2 * LID_WALL) / 2, LID_FLOOR + LID_SKIRT, align=BOT)
        with Locations((0, 0, LID_FLOOR)):
            Cylinder(inner / 2, LID_SKIRT, align=BOT, mode=Mode.SUBTRACT)
        # 입구 모따기 — 받침판을 겨누기 쉽게
        mouth = [e for e in part.edges().filter_by(Axis.Z, reverse=True)
                 if abs(e.center().Z - (LID_FLOOR + LID_SKIRT)) < 1e-6
                 and abs(e.center().X) < 1e-6 and abs(e.center().Y) < 1e-6]
        inner_edges = [e for e in mouth if abs(e.radius - inner / 2) < 1e-6]
        if inner_edges:
            chamfer(inner_edges, LID_LEAD)
        # 바깥 아래 모서리 — 변기 시트에 닿는 면
        bot = [e for e in part.edges().filter_by(Axis.Z, reverse=True)
               if abs(e.center().Z) < 1e-6]
        if bot:
            fillet(bot, 0.6)
    return part.part


def build_pin_print():
    """핀을 **출력 방향**으로 눕힌 것. 축이 x, 날 두께가 z 가 된다."""
    laid = build_pin().rotate(Axis.Y, 90).rotate(Axis.X, 90)
    bb = laid.bounding_box()
    return laid.moved(Location((-bb.min.X, 0, -bb.min.Z)))


def build_cover_mock():
    """조립 확인용 커버 조각 (출력물 아님). 가장자리가 EDGE_DIST 에 있다."""
    with BuildPart() as part:
        with Locations((EDGE_DIST - 40, 0, 0)):
            Cylinder(40.0, COVER_T, align=TOP)
        Cylinder(HOLE_D / 2, COVER_T, align=TOP, mode=Mode.SUBTRACT)
    return part.part


def build_assembly(with_cover=True):
    ring = build_ring_plate()
    ring.label = "ring_plate"
    base = build_base_plate().moved(Location((0, 0, BOSS_BOT)))
    base.label = "base_plate"
    pin = build_pin()
    pin.label = "pin"
    lid = build_lid().moved(Location((0, 0, BOSS_BOT - LID_FLOOR)))
    lid.label = "lid"
    parts = [ring, base, pin, lid]
    if with_cover:
        cover = build_cover_mock()
        cover.label = "cover_mock"
        parts.append(cover)
    return Compound(children=parts)


if __name__ == "__main__":
    finalize_iteration(build_assembly())

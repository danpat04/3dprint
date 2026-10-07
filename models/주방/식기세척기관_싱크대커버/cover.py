"""식기세척기관_싱크대커버 — 커버(상부) / 너트(하부).

    uv run python -m models.주방.식기세척기관_싱크대커버.cover

통로는 **큰 원 하나**다. 배수 호스 끝이 ⌀25.5 로 굵어져 두 관을 동시에
통과시킬 수 없으므로, 굵은 쪽을 먼저 넣고 급수관을 나중에 끼운다.
⌀22 와 ⌀6.35 를 함께 담는 최소 원이 28.35 라 ⌀28.5 보어면 둘 다 들어간다.

구멍 안(칼라)은 **수직이어야 한다.** 비스듬히 자르면 단면이 28.5/cos θ 로
커져 10도만 기울여도 구멍 31.5 를 못 지난다. 꺾임은 상판 위 엘보에서만 한다.
"""

import math

from build123d import (
    add,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    Helix,
    Polygon,
    Compound,
    Cone,
    Cylinder,
    Location,
    Locations,
    Mode,
    Plane,
    Vector,
    extrude,
    fillet,
    revolve,
    sweep,
)

from models._lib.iter import finalize_iteration
from models.주방.식기세척기관_싱크대커버.params import (
    BORE_D,
    COLLAR_LEN,
    COLLAR_PILOT,
    COLLAR_ROOT,
    COLLAR_OD,
    DECK_T,
    ELBOW_BORE,
    ELBOW_R,
    ELBOW_RAMP,
    ELBOW_TURN,
    FLANGE_D,
    FLANGE_R,
    FLANGE_T,
    HOLE_D,
    MOUTH_FLARE,
    NECK_WALL,
    NUT_H,
    NUT_FLUTE_R,
    NUT_FLUTES,
    NUT_OD,
    THREAD_DEPTH,
    THREAD_FIT,
    THREAD_LEN,
    THREAD_PITCH,
    ORING_DEPTH,
    ORING_MEAN,
    ORING_W,
)

BOT = (Align.CENTER, Align.CENTER, Align.MIN)
TOP = (Align.CENTER, Align.CENTER, Align.MAX)

ELBOW_AXIS_PT = None


def build_cover():
    """커버 ① — 칼라 + 플랜지 + 엘보. 조립 좌표(상판 윗면 = z 0).

    엘보는 **회전체**다. 관 단면(수평 원)을 곡률 중심을 지나는 y 축 둘레로
    돌린다. 로프트로 만들면 단면이 꼬여 뿔 모양이 된다.

    프로파일은 **빌더 밖에서** 만들어 넘긴다. BuildSketch 로 만들면 revolve 에
    넘겨도 pending 에 남아, 뒤따르는 연산이 그 면까지 같이 집어 형상이 끊긴다.
    """
    axis = Axis((ELBOW_R, 0, FLANGE_T), (0, 1, 0))
    prof_out = Plane.XY.offset(FLANGE_T) * Circle(ELBOW_BORE / 2 + NECK_WALL)
    prof_in = Plane.XY.offset(FLANGE_T) * Circle(ELBOW_BORE / 2)
    thread = _thread()
    oring = (Plane.XY * Circle((ORING_MEAN + ORING_W) / 2)
             - Plane.XY * Circle((ORING_MEAN - ORING_W) / 2))

    with BuildPart() as part:
        # 칼라 — 맨 위 2mm 는 ⌀31.0 (구멍 안에서 중심을 잡는다),
        # 그 아래는 나사 골지름 ⌀30.2
        Cylinder(COLLAR_OD / 2, COLLAR_PILOT, align=TOP)
        with Locations((0, 0, -COLLAR_PILOT)):
            Cylinder(COLLAR_ROOT / 2, COLLAR_LEN - COLLAR_PILOT, align=TOP)
        Cylinder(FLANGE_D / 2, FLANGE_T, align=BOT)         # 플랜지 (상판 위)
        revolve(prof_out, axis=axis, revolution_arc=ELBOW_TURN)
        add(thread)                                         # 나사산

        # ---- 통로 ----
        # 칼라는 28.5 (구멍 제약). 플랜지 안에서 33 으로 벌어진다 —
        # 굵은 부분(25.5)이 휜 구간을 지날 여유를 벌기 위해서다
        Cylinder(BORE_D / 2, COLLAR_LEN, align=TOP, mode=Mode.SUBTRACT)
        Cone(BORE_D / 2, ELBOW_BORE / 2, FLANGE_T, align=BOT, mode=Mode.SUBTRACT)
        revolve(prof_in, axis=axis, revolution_arc=ELBOW_TURN, mode=Mode.SUBTRACT)

        # 오링 홈 — 플랜지 아랫면. 홈 안쪽이 ⌀35.9 라 구멍(31.5) 바깥
        # 단단한 상판 위에 온전히 앉는다
        extrude(oring, ORING_DEPTH, mode=Mode.SUBTRACT)

        # 출구 나팔 — 호스가 꺾이는 지점의 날카로운 모서리를 없앤다.
        # 출구 면은 **법선이 엘보 끝 접선과 같은 평면**이다. 그것으로 고른다
        th = math.radians(ELBOW_TURN)
        tang = Vector(math.sin(th), 0, math.cos(th))
        mouth_faces = [f for f in part.faces()
                       if abs(f.normal_at(f.center()).dot(tang) - 1.0) < 1e-3]
        if mouth_faces:
            edges = mouth_faces[0].edges()
            for r in (MOUTH_FLARE, 1.5, 0.8):
                try:
                    fillet(edges, r)
                    break
                except Exception:
                    continue
    return part.part


THREAD_TOP = -COLLAR_PILOT                 # 나사 시작 (상판 바로 아래)
THREAD_BOT = THREAD_TOP - THREAD_LEN


def _thread(grow=0.0):
    """칼라 나사산 한 줄. grow 를 주면 너트 쪽 여유 있는 짝이 된다.

    **빌더 밖에서** 만든다. 프로파일 평면의 x 축을 반지름 방향으로 고정해야
    골 깊이가 의도대로 나온다 — 자동으로 두면 축 방향이 반지름이 되어
    깊이가 pitch 만큼 깊어진다.
    """
    rmid = COLLAR_ROOT / 2 + THREAD_DEPTH / 2
    path = Helix(pitch=THREAD_PITCH, height=THREAD_LEN, radius=rmid,
                 center=(0, 0, THREAD_BOT))
    pl = Plane(origin=path @ 0, x_dir=(1, 0, 0), z_dir=path % 0)
    d, a, b = THREAD_DEPTH / 2 + grow, THREAD_PITCH * 0.35 + grow, THREAD_PITCH * 0.18 + grow
    prof = pl * Polygon((-d, -a), (d, -b), (d, b), (-d, a), align=None)
    return sweep(prof, path=path, is_frenet=True)


def build_nut():
    """너트 ② — 아래에서 칼라에 끼워 올려 조인다. 상판을 커버와 사이에 물고
    오링을 눌러준다. 조일 수 있으므로 상판 두께 편차를 그대로 흡수한다."""
    mate = _thread(THREAD_FIT)
    with BuildPart() as part:
        Cylinder(NUT_OD / 2, NUT_H, align=BOT)
        Cylinder(COLLAR_ROOT / 2 + THREAD_FIT, NUT_H, align=BOT, mode=Mode.SUBTRACT)
        # 짝 나사산 — 칼라의 산을 여유 있게 키운 것을 빼낸다
        with Locations((0, 0, -THREAD_BOT)):
            add(mate, mode=Mode.SUBTRACT)
        # 손으로 돌릴 홈
        for i in range(NUT_FLUTES):
            th = 2 * math.pi * i / NUT_FLUTES
            with Locations((NUT_OD / 2 * math.cos(th), NUT_OD / 2 * math.sin(th), 0)):
                Cylinder(NUT_FLUTE_R, NUT_H, align=BOT, mode=Mode.SUBTRACT)
    return part.part


def build_deck_mock():
    """조립 확인용 상판 조각 (출력물 아님)."""
    with BuildPart() as part:
        Cylinder(45.0, DECK_T, align=TOP)
        Cylinder(HOLE_D / 2, DECK_T, align=TOP, mode=Mode.SUBTRACT)
    return part.part


def build_assembly(with_deck=True):
    cover = build_cover()
    cover.label = "cover"
    nut = build_nut().moved(Location((0, 0, -DECK_T - NUT_H - 0.5)))
    nut.label = "nut"
    parts = [cover, nut]
    if with_deck:
        deck = build_deck_mock()
        deck.label = "deck_mock"
        parts.append(deck)
    return Compound(children=parts)


if __name__ == "__main__":
    finalize_iteration(build_assembly())

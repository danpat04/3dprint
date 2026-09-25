"""dyson_dryer_hanger — 상부장 밑판에 거는 다이슨 Supersonic Travel 걸이.

리브 2장이 밑판 앞 가장자리를 물고, 그 사이 간격(41)으로 핸들(Ø38)이 아래로 빠지며
헤드(Ø71)가 두 리브에 걸린다. 헤드는 간격에 6.5mm 박혀 좌우로 자기정렬된다.

문 제약: 상부장 문이 밑판 앞면 2mm 앞에서 아래로 길게 뻗는다. 따라서 걸이는
y = -WEB_T 보다 앞으로 못 나가고, 문 하단을 지난 헤드 받이 높이에서만 앞으로 나간다.

앞판(웹)은 리브 두께 그대로 6mm 다. 선반이 아래팔 뒤끝을 눌러주는 반력까지 세면
앞판 모멘트는 −7 N·mm 로 거의 상쇄되어 1.4 MPa 밖에 안 걸린다. 넓힐 이유가 없다.

헤드는 **90° 돌려** 축이 좌우로 가게 건다. 크래들은 원호로 깎을 것 없이
**평평한 바닥 + 앞 60° 경사 립 + 뒤 수직벽(스파인)** 이면 충분하다.

**커넥터는 둘 다 뒤쪽**에 둔다. 앞에 두면 손잡이를 위에서 떨어뜨려 꽂아야 해서
불편하다. 앞을 비워두면 드라이어를 앞에서 밀어 넣어 손잡이가 리브 사이로 들어간다.

연결은 **십자 맞춤**이다 — 도브테일도 접착제도 없이, 서로 홈을 파 맞물리게 하고
중력이 맞물림을 눌러 앉히는 방향으로 배치한다.
  A : 선반 위. **리브가 위**로 가게 맞문다 — 리브가 받는 아래 방향 하중이
      맞물림을 눌러 앉힌다. 합쳤을 때 높이는 위팔 두께 그대로다.
  B : 리브 하단 뒤쪽 돌기 + 구멍 뚫린 보. **뒤에서 밀어** 끼운다.

90° 회전 덕에 헤드가 간격에 쐐기처럼 박히지 않고 바닥에 얹힌다 → 리브를 바깥으로
미는 힘이 사라져 커넥터는 정렬 유지 역할만 한다.

리브는 프로파일을 베드에 눕혀 출력. 힘이 전부 면 안쪽 방향이라 압출선이 그대로 받는다.
"""

from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Compound,
    Cylinder,
    Locations,
    Mode,
    Plane,
    Polygon,
    Rectangle,
    add,
    extrude,
    mirror,
)

from models._lib.iter import finalize_iteration
from models.bathroom.dyson_dryer_hanger.params import *  # noqa: F403


def _box(x0, x1, y0, y1, z0, z1, mode=Mode.ADD):
    """전역 좌표 (x0..x1, y0..y1, z0..z1) 로 박스."""
    with Locations((x0, y0, z0)):
        Box(x1 - x0, y1 - y0, z1 - z0,
            align=(Align.MIN, Align.MIN, Align.MIN), mode=mode)


def _rect(y0, y1, z0, z1):
    """YZ 평면 스케치용 — 전역 (y,z) 범위로 사각형."""
    with Locations(((y0 + y1) / 2, (z0 + z1) / 2)):
        Rectangle(y1 - y0, z1 - z0)


def _rib_profile():
    """리브 프로파일 (YZ). 앞판은 별도 — 여기는 두께 RIB_T 로 압출되는 부분만."""
    _rect(0.0, SLOT_D, -ARM_T, 0.0)                        # 아래팔
    _rect(0.0, SLOT_D, SLOT_H, SLOT_H + ARM_T)             # 위팔
    # 스파인 — 문 뒤로만 두꺼워진다. 다만 **슬롯 높이까지 올라오면 밑판이 안 들어간다**.
    # 아래팔 밑(z=-ARM_T)에서 끊고, 그 위는 1.6mm 앞판만 남긴다.
    _rect(FRONT_Y, FRONT_Y + SPINE_T, RIB_BOT_Z, -ARM_T)
    # 하단 뒤쪽 돌기 — 보의 구멍이 여기에 뒤에서 끼워진다
    _rect(FRONT_Y + SPINE_T, FRONT_Y + SPINE_T + TAB_L,
          TAB_Z0, TAB_Z0 + TAB_H)

    # 크래들 — 바닥(평평) + 앞 경사 립 + 뒤 수직벽. 립 위로 앞은 열려 있다
    Polygon((RIB_FRONT_Y, RIB_BOT_Z), (FRONT_Y, RIB_BOT_Z),
            (FRONT_Y, CRADLE_BOT_Z), (LIP_BASE_Y, CRADLE_BOT_Z),
            (LIP_TOP_Y, CRADLE_BOT_Z + LIP_H), (RIB_FRONT_Y, CRADLE_BOT_Z + LIP_H),
            align=None)
    # 스트럿 — 꼭짓점을 띠 둘레 순서로. 대각선 두 점을 연속으로 두면 자기교차한다.
    Polygon((FRONT_Y + SPINE_T, STRUT_Z), (STRUT_Y, -ARM_T),
            (STRUT_Y - STRUT_W, -ARM_T),
            (FRONT_Y + SPINE_T, STRUT_Z + STRUT_W), align=None)


def _dovetail(y_c, half_root, half_tip, x0, x1):
    """XY 평면 도브테일 사다리꼴. x0 = 리브 안쪽 면(뿌리), x1 = 리브 속(끝)."""
    return Polygon((x0, y_c - half_root), (x1, y_c - half_tip),
                   (x1, y_c + half_tip), (x0, y_c + half_root), align=None)


def build_rib_right():
    """오른쪽 리브 — x = GAP/2 ~ GAP/2+RIB_T."""
    with BuildPart() as part:
        with BuildSketch(Plane.YZ.offset(GAP / 2)):
            _rib_profile()
        extrude(amount=RIB_T)

        # 앞판(웹) — 문 틈을 지나는 1.6mm. 슬롯 위아래 팔을 잇는다
        with BuildSketch(Plane.YZ.offset(GAP / 2)):
            _rect(FRONT_Y, 0.0, -ARM_T, RIB_TOP_Z)
        extrude(amount=RIB_T)

        # A 십자 맞춤 홈 — 위팔 **밑면**에서 절반 깊이만 판다 (아래로 열림).
        # 리브가 커넥터 위에 올라앉아 하중이 맞물림을 눌러준다.
        _box(GAP / 2 - 1, GAP / 2 + RIB_T + 1,
             A_Y[0] - LAP_FIT, A_Y[1] + LAP_FIT,
             SLOT_H - 1, SLOT_H + LAP_D, mode=Mode.SUBTRACT)
    return part.part


def build_rib_left():
    """왼쪽 리브 — 오른쪽을 중앙(x=0)에서 미러."""
    return mirror(build_rib_right(), about=Plane.YZ)


def _rib_x(sgn):
    """리브 한 장의 x 범위."""
    a, b = sgn * (GAP / 2), sgn * (GAP / 2 + RIB_T)
    return min(a, b), max(a, b)


def build_connector_a():
    """A — 선반 위 십자 맞춤. 리브가 이 위에 올라앉는다 (윗면을 절반 판다)."""
    x_out = GAP / 2 + RIB_T + A_OVER
    with BuildPart() as part:
        _box(-x_out, x_out, A_Y[0], A_Y[1], SLOT_H, SLOT_H + A_H)
        for sgn in (-1, 1):
            x0, x1 = _rib_x(sgn)
            _box(x0 - LAP_FIT, x1 + LAP_FIT, A_Y[0] - 1, A_Y[1] + 1,
                 SLOT_H + LAP_D, SLOT_H + A_H + 1, mode=Mode.SUBTRACT)
    return part.part


def build_beam():
    """B — 하단 보. 구멍을 리브 뒤쪽 돌기에 **뒤에서 밀어** 끼운다."""
    x_out = GAP / 2 + RIB_T + BEAM_OVER
    y0 = FRONT_Y + SPINE_T
    z0 = TAB_Z0 - (BEAM_H - TAB_H) / 2
    with BuildPart() as part:
        _box(-x_out, x_out, y0, y0 + BEAM_T, z0, z0 + BEAM_H)
        for sgn in (-1, 1):
            x0, x1 = _rib_x(sgn)
            _box(x0 - HOLE_FIT, x1 + HOLE_FIT, y0 - 1, y0 + BEAM_T + 1,
                 TAB_Z0 - HOLE_FIT, TAB_Z0 + TAB_H + HOLE_FIT, mode=Mode.SUBTRACT)
    return part.part


def build_dryer_mock():
    """Supersonic Travel 목업 — 배치를 눈으로 보기 위한 것. 출력물 아님."""
    with BuildPart() as part:
        with Locations((0, HEAD_CY, HEAD_CZ)):
            Cylinder(HEAD_R, HEAD_L, rotation=(0, 90, 0))            # 헤드 (축 = 좌우)
        with Locations((0, HEAD_CY, HEAD_CZ - HEAD_R - HANDLE_L / 2)):
            Cylinder(HANDLE_D / 2, HANDLE_L)                         # 핸들
    return part.part


def build_assembly(with_dryer=True):
    parts = [build_rib_left(), build_rib_right(),
             build_connector_a(), build_beam()]
    for p, n in zip(parts, ["rib_left", "rib_right", "conn_a", "beam"]):
        p.label = n
    if with_dryer:
        m = build_dryer_mock()
        m.label = "dryer_mock"
        parts.append(m)
    return Compound(children=parts)


if __name__ == "__main__":
    finalize_iteration(build_assembly())

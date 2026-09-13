"""name_tag — 양각 글자 네임택 (글자만 다른 색으로 출력 가능).

얇은 판 + 한쪽 끝 고리 구멍 + 윗면 양각 글자.
**판과 글자를 별도 솔리드로 분리**해 STEP 에 두 바디로 담는다.
슬라이서에서 파트별로 필라멘트를 지정하면 글자만 다른 색으로 뽑힌다.

판 크기는 글자에 맞춰 자동 계산된다 (TEXT 만 바꾸면 판이 따라 커진다).
고정 크기로 쓰고 싶으면 build_tag(plate_w=..., plate_h=...) 로 덮어쓴다.

폰트: Pretendard Black — 획이 굵어 양각이 가장 잘 살아난다 (FONTS 표 참고).
      굵기는 font_style 이 아니라 **패밀리 이름으로 고른다**.

      원본 폰트 파일은 models/_assets/fonts/ 에 있고, 쓰려면 fontconfig 에 등록해야 한다:
        cp models/_assets/fonts/Pretendard*.otf models/_assets/fonts/Nanum*.ttf \
           ~/.local/share/fonts/
        fc-cache -f ~/.local/share/fonts

색 분리 방법 (권장): 판 윗면이 z=PLATE_T 의 완전한 평면이고 그 위는 전부 글자다.
  슬라이서에서 **z=2.4mm 에 색 변경(필라멘트 교체)을 한 번 넣으면** 글자만 다른 색이
  된다. 단일 노즐 프린터에서도 M600 일시정지로 가능.
  PLATE_T / EMBOSS_H 를 바꿀 땐 둘 다 레이어 높이의 정수배로 유지할 것.

  AMS/다중재료로 파트별 지정을 하고 싶으면 export.py 가 뽑는 plate/text STEP 을
  따로 불러 쓴다. 다만 한글은 자모가 떨어져 있어 글자가 여러 솔리드로 쪼개지므로
  (예: '홍길동' → 8개) 파트 지정이 번거롭다. 색 변경 쪽이 훨씬 간단하다.

출력: 판을 bed 에 글자가 위로 — 서포트리스.
"""

from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Compound,
    Cylinder,
    FontStyle,
    GeomType,
    Locations,
    Mode,
    Plane,
    Rectangle,
    Text,
    chamfer,
    extrude,
    fillet,
)

from models._lib.iter import finalize_iteration

# ---- 글자 ----
TEXT = "앞 - 오른쪽"

# 양각은 획이 굵을수록 잘 나온다. 아래는 '홍길동' size 12 기준 획 면적(mm²).
#
#   ※ Pretendard Variable 은 쓰지 말 것 — OCC 가 가변 축을 못 읽어 FontStyle.BOLD 를
#     줘도 REGULAR 와 결과가 동일(99.7)하고, 후보 중 가장 얇다. 정적 웨이트를 쓴다.
FONTS = {
    "pretendard-black":     "Pretendard Black",       # 186.4 — 기본, 가장 굵음
    "pretendard-extrabold": "Pretendard ExtraBold",   # 169.7
    "nanumsquare-eb":       "NanumSquareOTFEB00",     # 163.3
    "pretendard-bold":      "Pretendard",             # 152.7
    "nanumsquare-b":        "NanumSquareOTFB00",
    "nanumgothic":          "NanumGothic",            # 긴 문장에 무난
}
FONT = FONTS["pretendard-black"]
FONT_STYLE = FontStyle.REGULAR   # 굵기는 FONT 패밀리로 고른다 (style 로 고르지 않음)
FONT_SIZE = 12.0
EMBOSS_H = 0.6         # 양각 높이 — 0.2 레이어 3층 (사용자 확정)

# ---- 판 ----
# PLATE_T 는 레이어 높이의 정수배여야 색 경계가 층 중간에 걸리지 않는다.
#   2.4 → 0.2 레이어 12층 / 0.15 레이어 16층 (둘 다 딱 떨어짐)
#   2.5 는 0.2 에서 12.5층이라 경계가 어긋난다
PLATE_T = 2.4          # 판 두께
PAD_X = 6.0            # 글자 좌우 여백
PAD_Y = 5.0            # 글자 상하 여백
CORNER_R = 3.0         # 모서리 라운드

# ---- 고리 구멍 ----
HOLE_D = 5.0           # 구멍 지름 (사용자 확정 — 두꺼운 고리/카라비너)
HOLE_MARGIN = 4.0      # 구멍 가장자리 ↔ 판 끝 살 두께

# ---- 챔퍼 (판 상하 양쪽. 글자에는 넣지 않는다) ----
# 판 두께 2.4 에서 0.5 × 2 = 1.0 을 쓰고 수직 벽 1.4 가 남는다.
OUTER_CH = 0.5         # 외곽선 — 손맛 + 아래쪽은 코끼리발 방지
HOLE_CH = 0.5          # 고리 구멍 안쪽 — 고리 진입 유도 + 버 제거

_CTR_MIN = (Align.CENTER, Align.CENTER, Align.MIN)


def _text_sketch(text: str):
    """글자 스케치 (원점 근처). 크기 계산과 실제 배치에 모두 쓴다."""
    with BuildSketch() as sk:
        Text(text, font_size=FONT_SIZE, font=FONT, font_style=FONT_STYLE)
    return sk.sketch


def tag_size(text: str = TEXT) -> tuple[float, float]:
    """글자에서 자동 계산한 판 크기 (가로, 세로)."""
    bb = _text_sketch(text).bounding_box()
    hole_zone = HOLE_D + 2 * HOLE_MARGIN           # 구멍부가 차지하는 폭
    w = hole_zone + bb.size.X + 2 * PAD_X
    h = max(bb.size.Y + 2 * PAD_Y, hole_zone)      # 구멍이 들어갈 세로는 확보
    return w, h


def build_plate(text: str = TEXT, plate_w: float | None = None,
                plate_h: float | None = None):
    """판 — 라운드 사각형 + 고리 구멍."""
    w, h = tag_size(text)
    w, h = plate_w or w, plate_h or h

    with BuildPart() as part:
        with BuildSketch() as sk:
            with Locations((w / 2, h / 2)):
                Rectangle(w, h)
            fillet(sk.vertices(), CORNER_R)
        extrude(amount=PLATE_T)

        # 고리 구멍 — 왼쪽 끝, 세로 중앙
        hx, hy = HOLE_MARGIN + HOLE_D / 2, h / 2
        with Locations((hx, hy, 0)):
            Cylinder(HOLE_D / 2, PLATE_T, align=_CTR_MIN, mode=Mode.SUBTRACT)

        # 챔퍼 — 판의 위/아래 면 둘 다. 구멍 원과 외곽선을 나눠서 건다.
        # 주의: Edge.center() 는 원의 중심이 아니라 호 위의 점을 준다. 위치로는
        # 구멍을 못 가르므로 **반지름**으로 구분한다 (구멍 R2.5 vs 코너 라운드 R3).
        def _flat_edges():
            faces = part.faces().filter_by(Plane.XY)
            return list(faces.sort_by(Axis.Z)[-1].edges()) + \
                   list(faces.sort_by(Axis.Z)[0].edges())

        def _is_hole(e):
            return (e.geom_type == GeomType.CIRCLE
                    and abs(e.radius - HOLE_D / 2) < 1e-6)

        chamfer([e for e in _flat_edges() if not _is_hole(e)], OUTER_CH)
        chamfer([e for e in _flat_edges() if _is_hole(e)], HOLE_CH)

    return part.part


def build_text(text: str = TEXT, plate_w: float | None = None,
               plate_h: float | None = None):
    """양각 글자 — 판 윗면(z=PLATE_T)에서 EMBOSS_H 만큼 솟는 별도 솔리드."""
    w, h = tag_size(text)
    w, h = plate_w or w, plate_h or h

    hole_zone = HOLE_D + 2 * HOLE_MARGIN
    cx = hole_zone + (w - hole_zone) / 2           # 구멍부를 뺀 나머지의 중앙
    cy = h / 2

    # Text 는 원점 기준으로 나오므로, bbox 중심을 목표 위치로 옮긴다
    bb = _text_sketch(text).bounding_box()
    dx, dy = cx - bb.center().X, cy - bb.center().Y

    with BuildPart() as part:
        with BuildSketch(Plane.XY.offset(PLATE_T)):
            with Locations((dx, dy)):
                Text(text, font_size=FONT_SIZE, font=FONT, font_style=FONT_STYLE)
        extrude(amount=EMBOSS_H)

    return part.part


def build_tag(text: str = TEXT, plate_w: float | None = None,
              plate_h: float | None = None):
    """판 + 글자를 2-바디 컴파운드로. 슬라이서에서 파트별 필라멘트 지정용."""
    plate = build_plate(text, plate_w, plate_h)
    letters = build_text(text, plate_w, plate_h)
    plate.label, letters.label = "plate", "text"
    return Compound(children=[plate, letters])


if __name__ == "__main__":
    finalize_iteration(build_tag())

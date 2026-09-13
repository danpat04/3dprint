# fonts

`models/name_tag` 등에서 쓰는 폰트 원본. `model.py` 의 `FONTS` 딕셔너리가 참조하는
것만 보관한다.

| 파일 | fontconfig 패밀리 | 출처 / 라이선스 |
|---|---|---|
| `Pretendard-Black.otf` | `Pretendard Black` | [orioncactus/pretendard](https://github.com/orioncactus/pretendard) · OFL 1.1 |
| `Pretendard-ExtraBold.otf` | `Pretendard ExtraBold` | 〃 |
| `Pretendard-Bold.otf` | `Pretendard` (style=Bold) | 〃 |
| `NanumSquareEB.ttf` | `NanumSquareOTFEB00` | [moonspam/NanumSquare](https://github.com/moonspam/NanumSquare) · Naver |
| `NanumSquareB.ttf` | `NanumSquareOTFB00` | 〃 |
| `NanumGothic-Bold.ttf` | `NanumGothic` (style=Bold) | [google/fonts](https://github.com/google/fonts/tree/main/ofl/nanumgothic) · OFL 1.1 |
| `NanumGothic-Regular.ttf` | `NanumGothic` | 〃 |

## 설치

build123d(OCC)는 `Text(font_path=...)` 로 파일을 직접 지정해도 못 찾는다
(한글 fallback 실패). **fontconfig 에 등록해야** 한다:

```bash
cp models/_assets/fonts/*.otf models/_assets/fonts/*.ttf ~/.local/share/fonts/
fc-cache -f ~/.local/share/fonts
```

등록 확인:

```bash
fc-list : family | tr ',' '\n' | grep -iE 'pretendard|nanum' | sort -u
```

## 보관하지 않는 것

**Pretendard Variable** — OCC 가 가변 축을 읽지 못해 `FontStyle.BOLD` 를 줘도
Regular 와 결과가 동일하다. 후보 중 획이 가장 얇아 양각에 최악이라 제외했다.
정적 웨이트(.otf)를 쓸 것. 자세한 비교는 `models/name_tag/README.md` 참고.

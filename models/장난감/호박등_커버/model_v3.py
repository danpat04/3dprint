"""호박등 커버 v3: 원본 비율 유지(균일 확대) — v1 대비 1.11배 (외경 ~78mm, 높이 +5mm).
아래 개구부 49mm / 위 구멍 18mm 는 그대로 (아래는 안쪽 칼라가 더 넓어진다)."""
from models.장난감.호박등_커버.model import build

SCALE_V3 = 0.555   # v1 0.5 대비 1.11배 (균일)

if __name__ == "__main__":
    build("v3", SCALE_V3, out_d=SCALE_V3 * 140.0)

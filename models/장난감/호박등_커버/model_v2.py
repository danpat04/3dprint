"""호박등 커버 v2: v1(model.py) 에서 세로만 약 11% 늘려 높이 +5mm (램프가 아래로 덜 나오게).
v1 은 그대로 두고 `exports/<폴더명>_v2.*` 로 따로 내보낸다."""
from models.장난감.호박등_커버.model import build

SZ_V2 = 0.555   # v1 0.5 -> 높이 45.5mm -> 약 50.5mm

if __name__ == "__main__":
    build("v2", SZ_V2)

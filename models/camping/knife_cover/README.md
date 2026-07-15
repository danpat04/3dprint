# knife_cover

식칼 보호용 U 채널 시스(sheath). 칼날쪽 바닥 + 양옆 + 칼끝 닫음, 손잡이쪽 + 칼등쪽 open.
양 벽이 cantilever 처럼 휘면서 칼을 press-fit 으로 잡음.

![iso](images/iter_003_iso.png)

## 칼 스펙 (기준)

| 항목 | 값 |
|---|---|
| 칼날 길이 | 137mm |
| 칼날 최대 두께 (heel) | 2.0mm |
| 칼날 높이 (heel) | 34mm |
| 형태 | 전형적 식칼 (tip 으로 갈수록 thin) |

## 구조

```
front (handle 쪽 open 면):

      ↑ spine open (위로 트임)
   ┌    ┐
   │    │  ← 양 벽 (X 면, 두께 1.5mm) — cantilever flex
   │  | │  ← slot 1mm (칼 두께 2mm 보다 1mm 좁음)
   │    │
   └────┘  ← edge 벽 (Z 바닥, 두께 2mm) — hinge base
```

칼은 손잡이쪽 open 면(Y=0) 으로 밀어 넣거나 spine open 으로 떨궈 넣음. 들어가는 동안 양 벽이 각 0.5mm 휘면서 grip.

## 치수

| 항목 | 값 | 비고 |
|---|---|---|
| Slot X (relaxed) | 1.0mm | 칼 2mm - 1mm interference (벽 flex 로 grip) |
| Slot Y | 138mm | 칼 길이 + 1mm 끝쪽 여유 |
| Slot Z | 35mm | 칼 높이 + 1mm 위쪽 여유 |
| 벽 두께 (X 양면) | 1.5mm | cantilever |
| 벽 두께 (Y 끝, tip) | 2.0mm | 칼끝 막음 |
| 벽 두께 (Z 바닥, edge) | 2.0mm | hinge base |
| 챔퍼 | 0.3mm | 모든 모서리 (손맛 + slot lead-in) |
| 외부 X | 4.0mm | |
| 외부 Y | 140mm | |
| 외부 Z | 37mm | (spine 위 wall 없음) |

## acceptance criteria

- 칼이 손잡이쪽에서 밀려 들어감 (또는 spine open 으로 떨궈 넣음)
- heel 이 입구에 도달했을 때 가장 강한 grip
- 가방에서 흔들어도 칼이 빠지지 않음 (예상 retention ~165g)
- 손으로 당기면 부드럽게 빠짐
- 칼날/칼끝 외부 노출 X

## 출력 (Bambu P2S)

### 방향: 수직 (Y 축 수직, 140mm 가 print Z)

```
print bed → ▬▬▬▬▬▬▬▬▬  (tip 끝이 바닥, 148mm² 접지)
               ║
               ║   ← cover 가 수직으로 서 있음 (140mm 높이)
               ║
              ☐    ← handle open 이 위
```

벽 flex stress 가 layer 평면 방향 (Z 방향, 인장이 layer 내부) 에 들어와서 interlayer 강도와 무관 — 가장 안전한 방향.

### 슬라이서 설정

| 항목 | 값 |
|---|---|
| Layer height | 0.2mm |
| Wall loops | 4 |
| Infill | 25% gyroid |
| **Brim** | **10mm** (148mm² 접지 + 140mm 높이, 안정 필수) |
| Support | 불필요 (모든 hole 이 수직 또는 spine open) |
| Speed | 50% (첫 30 layers) — 베이스 안정 |

### 재료

- **PETG-HF** 권장 — flex elastic, crack 저항. 반복 끼움 견딤
- PLA 가능하지만 stress 누적 시 creep 위험

## 재료 + 자재

| 항목 | 수량 |
|---|---|
| PETG-HF filament | ~15g |
| (자석/나사 불필요 — single piece) | |

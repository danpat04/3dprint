# web v2 — build123d + f3d + FastAPI 통합 이미지
#
# 기존 viewer/feedback 컨테이너는 어느 쪽도 혼자서 "빌드 → 렌더 → 표시" 를 못 한다
# (f3d 는 둘 다 없음). 여기서 전부 한다.
FROM python:3.11-slim

WORKDIR /app

# OCP(OpenCascade) + f3d 소프트웨어 렌더링에 필요한 시스템 라이브러리.
# mesa 계열이 없으면 f3d 가 엔진 생성 단계에서 **세그폴트**로 죽는다 (검증 완료).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libxrender1 libxmu6 libxi6 \
    libegl1 libgles2 libgl1-mesa-dri libglx-mesa0 libosmesa6 \
    libxext6 libx11-6 libxcursor1 libxrandr2 libxinerama1 libxfixes3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN uv pip install --system --no-cache \
    build123d "f3d>=3.5.0" \
    "fastapi>=0.110" "uvicorn[standard]>=0.29" \
    "authlib>=1.3" "httpx>=0.27" "itsdangerous>=2.1"

# 소프트웨어 렌더링 강제 (GPU 없는 컨테이너)
ENV LIBGL_ALWAYS_SOFTWARE=1

COPY app/ app/

EXPOSE 3941

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3941"]

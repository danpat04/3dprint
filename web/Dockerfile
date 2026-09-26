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

# ocp-vscode 는 뷰어용이 아니라 **models/_lib/iter.py 가 import** 하기 때문에 필요하다.
# 없으면 모델 모듈을 실행할 수 없다 (show() 자체는 실패해도 무방하게 처리돼 있다).
# 인증은 Caddy forward_auth 가 대행하므로 OAuth 라이브러리는 필요 없다.
RUN uv pip install --system --no-cache \
    build123d "f3d>=3.5.0" ocp-vscode \
    "fastapi>=0.110" "uvicorn[standard]>=0.29" \
    "httpx>=0.27"

# 소프트웨어 렌더링 강제 (GPU 없는 컨테이너)
ENV LIBGL_ALWAYS_SOFTWARE=1

# 캐시 디렉토리를 이미지에 미리 만들어 소유권을 준다.
# 빈 명명 볼륨은 마운트 지점의 내용과 **소유권까지** 이미지에서 물려받는다.
# 이게 없으면 볼륨이 root 소유로 생기고, uid 1000 으로 도는 컨테이너가 못 쓴다.
RUN mkdir -p /app/cache && chown 1000:1000 /app/cache

# uid 1000 으로 돌 때 홈이 없으면 HOME 이 / 로 잡혀 f3d 가 /.cache 를 만들려다
# 권한 오류로 죽는다. 쓸 수 있는 홈을 준다.
RUN mkdir -p /home/app && chown 1000:1000 /home/app
ENV HOME=/home/app XDG_CACHE_HOME=/home/app/.cache

COPY app/ app/

EXPOSE 3941

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3941"]

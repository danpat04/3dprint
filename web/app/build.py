"""빌드 잡 큐.

웹에서 "이 파트 다시 만들어줘" 를 받아 모델 모듈을 실행한다.

**직렬로 하나씩 돌린다.** OCC 는 스레드 안전하지 않고 빌드는 CPU 를 오래 쓴다.
동시에 돌려서 얻을 게 없다.

**실행할 명령은 서버가 정한다.** 클라이언트가 보낸 문자열을 모듈 경로로 쓰면
임의 코드 실행이 된다. 탐색된 파트 목록에 있는 것만 실행한다.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

WORKDIR = os.environ.get("BUILD_WORKDIR", "/app")
MAX_LOG = 400            # 잡당 보관할 로그 줄 수
KEEP_JOBS = 50


@dataclass
class Job:
    id: str
    slug: str
    part: str
    cmd: list[str]
    status: str = "queued"        # queued | running | done | failed
    log: list[str] = field(default_factory=list)
    returncode: int | None = None
    queued_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: str | None = None
    finished_at: str | None = None

    def as_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if k != "cmd"}


_jobs: dict[str, Job] = {}
_order: list[str] = []
_queue: asyncio.Queue[str] | None = None


def submit(slug: str, part: str, cmd: list[str]) -> Job:
    job = Job(id=uuid.uuid4().hex[:12], slug=slug, part=part, cmd=cmd)
    _jobs[job.id] = job
    _order.append(job.id)
    while len(_order) > KEEP_JOBS:
        _jobs.pop(_order.pop(0), None)
    assert _queue is not None, "worker not started"
    _queue.put_nowait(job.id)
    return job


def get(job_id: str) -> Job | None:
    return _jobs.get(job_id)


def recent(slug: str | None = None, limit: int = 20) -> list[dict]:
    jobs = (_jobs[i] for i in reversed(_order) if i in _jobs)
    out = [j.as_dict() for j in jobs if slug is None or j.slug == slug]
    return out[:limit]


def active_for(slug: str) -> dict | None:
    """해당 프로젝트에서 아직 끝나지 않은 잡."""
    for i in reversed(_order):
        j = _jobs.get(i)
        if j and j.slug == slug and j.status in ("queued", "running"):
            return j.as_dict()
    return None


async def _run(job: Job) -> None:
    job.status = "running"
    job.started_at = datetime.now(timezone.utc).isoformat()
    try:
        proc = await asyncio.create_subprocess_exec(
            *job.cmd, cwd=WORKDIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        assert proc.stdout is not None
        async for raw in proc.stdout:
            line = raw.decode("utf-8", "replace").rstrip()
            job.log.append(line)
            if len(job.log) > MAX_LOG:
                del job.log[0]
        job.returncode = await proc.wait()
        job.status = "done" if job.returncode == 0 else "failed"
    except Exception as exc:                       # 실패를 삼키지 않는다
        job.log.append(f"[build] {type(exc).__name__}: {exc}")
        job.status = "failed"
    finally:
        job.finished_at = datetime.now(timezone.utc).isoformat()


async def _worker() -> None:
    assert _queue is not None
    while True:
        job_id = await _queue.get()
        job = _jobs.get(job_id)
        if job is not None:
            await _run(job)
        _queue.task_done()


def start() -> None:
    """앱 기동 시 호출. 워커 하나만 띄운다."""
    global _queue
    _queue = asyncio.Queue()
    asyncio.get_running_loop().create_task(_worker())

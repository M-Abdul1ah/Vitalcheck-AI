"""
Workflow trace: a small record of what every agent did for one message.
The app builds one trace per message; the Workflow tab replays it as an animation.
"""
import secrets
import time


def ms_since(t0: float) -> int:
    """Milliseconds since t0 (from time.perf_counter()), at least 1."""
    return max(1, round((time.perf_counter() - t0) * 1000))


def step(agent: str, status: str, ms: int = 0, inn: str = "", out: str = "", log: str = "",
         sub: str | None = None, matches=None, stream: str | None = None) -> dict:
    """One agent step. status: done, warn, alert or skip."""
    d = {"id": agent, "st": status, "ms": ms, "inn": inn, "out": out, "log": log}
    if sub:
        d["sub"] = sub
    if matches is not None:
        d["matches"] = matches
    if stream is not None:
        d["stream"] = stream
    return d


def skipped(agents: list, log: str) -> dict:
    """Several agents that were not needed (used when the safety gate stops the pipeline)."""
    return {"skip": agents, "log": log}


def make_trace(prompt: str, steps: list, tone: str, end: str, kb_chunks: int = 0) -> dict:
    """tone: success, warning or danger (colors the resolution banner)."""
    return {
        "id": "vc-" + secrets.token_hex(3),
        "query": prompt[:80],
        "steps": steps,
        "tone": tone,
        "end": end,
        "kb": kb_chunks,
    }

"""Render disjoint native Blender frame ranges from an already built .blend."""

import argparse, os, subprocess, math
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from execution_policy import production_only, enable_cli_production

from common import read, digest, write


@production_only
def render(project, workers=1, threads=4, start=1, end=None):
    p = Path(project).resolve()
    b = p.parent
    c = read(p)
    tl = read(b / c["timeline"])
    last = end or round(tl["duration"] * c["video"]["fps"])
    scene = b / "build/GeoMotionThai.blend"
    if not scene.exists():
        raise ValueError("Build Blender scene first")
    workers = max(1, min(workers, 8, last - start + 1))
    count = last - start + 1
    chunk = math.ceil(count / workers)
    jobs = [
        (i, a, min(last, a + chunk - 1))
        for i, a in enumerate(range(start, last + 1, chunk))
    ]
    env = dict(os.environ)
    env["LP_NUM_THREADS"] = str(threads)

    def job(item):
        i, a, z = item
        log = b / f"build/render_worker_{i}.log"
        cmd = [
            "blender",
            "-b",
            str(scene),
            "-t",
            str(threads),
            "-o",
            str(b / "build/frames/frame_"),
            "-s",
            str(a),
            "-e",
            str(z),
            "-a",
        ]
        with log.open("w") as f:
            r = subprocess.run(cmd, env=env, stdout=f, stderr=f)
        if r.returncode:
            raise RuntimeError(f"Blender range {a}:{z} failed, see {log.name}")
        return {"start": a, "end": z, "log": log.name}

    with ThreadPoolExecutor(workers) as pool:
        results = list(pool.map(job, jobs))
    write(
        b / "build/frame_render.json",
        {
            "scene_sha256": digest(scene),
            "project_sha256": digest(p),
            "timeline_sha256": digest(b / c["timeline"]),
            "workers": workers,
            "threads_per_worker": threads,
            "native_resolution": [c["video"]["width"], c["video"]["height"]],
            "ranges": results,
        },
    )
    print(f"Rendered frames {start}–{last} from native 3D scene, {workers} worker(s).")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int)
    ap.add_argument(
        "--produce-media",
        action="store_true",
        help="Only after an explicit user clip request",
    )
    a = ap.parse_args()
    enable_cli_production(a.produce_media)
    render(a.project, a.workers, a.threads, a.start, a.end)

# -*- coding: utf-8 -*-
"""Minimal client for the Pippit Seedance pool (OpenAI-style video API).

    BASE=http://127.0.0.1:8788 KEY=sk-wz-... python openai_client.py "prompt" [seconds]

Flow: POST /v1/videos -> poll GET /v1/videos/{id} -> GET .../content
"""
import os, sys, time, json, requests

BASE = os.environ.get("BASE", "http://127.0.0.1:8788").rstrip("/")
KEY = os.environ.get("KEY", "")
MODEL = os.environ.get("MODEL", "seedance-2.5-720p-natural")
PROMPT = sys.argv[1] if len(sys.argv) > 1 else "a rainy neon street at midnight, slow dolly, cinematic"
SECONDS = int(sys.argv[2]) if len(sys.argv) > 2 else 15
RATIO = os.environ.get("RATIO", "9:16")
OUT = os.environ.get("OUT", "out.mp4")
TIMEOUT = int(os.environ.get("TIMEOUT", "2700"))
H = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}


def create():
    body = {"model": MODEL, "prompt": PROMPT, "seconds": SECONDS, "ratio": RATIO}
    r = requests.post(BASE + "/v1/videos", headers=H, json=body, timeout=60)
    r.raise_for_status()
    return r.json()


def wait(job_id):
    t0 = time.time()
    while time.time() - t0 < TIMEOUT:
        g = requests.get(BASE + "/v1/videos/" + job_id, headers=H, timeout=60).json()
        print("  %5.0fs %-11s %3s%%" % (time.time() - t0, g["status"], g.get("progress", 0)), flush=True)
        if g["status"] == "completed":
            return g
        if g["status"] in ("failed", "canceled"):
            raise SystemExit("job %s: %s" % (g["status"], json.dumps(g.get("error"), ensure_ascii=False)))
        time.sleep(10)
    raise SystemExit("timeout waiting for %s" % job_id)


if __name__ == "__main__":
    job = create()
    print("created", job["id"], job["status"])
    done = wait(job["id"])
    url = done.get("output_url") or (BASE + "/v1/videos/%s/content" % job["id"])
    data = requests.get(url, headers={"Authorization": "Bearer " + KEY}, timeout=900).content
    open(OUT, "wb").write(data)
    print("saved", OUT, len(data), "bytes", done.get("duration"), "s", done.get("width"), "x", done.get("height"))

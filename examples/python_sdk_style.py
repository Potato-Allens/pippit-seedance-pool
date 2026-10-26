# -*- coding: utf-8 -*-
"""SDK-style wrapper, so existing `openai`-shaped code reads naturally."""

import os, time, requests


class SeedancePool:
    def __init__(self, base_url=None, api_key=None):
        self.base = (base_url or os.environ["BASE"]).rstrip("/")
        self.key = api_key or os.environ["KEY"]
        self.h = {"Authorization": "Bearer " + self.key, "Content-Type": "application/json"}

    def models(self):
        return requests.get(self.base + "/v1/models", headers=self.h, timeout=30).json()["data"]

    def videos_create(self, prompt, model="seedance-2.5-720p-natural", seconds=15, ratio="9:16", **kw):
        body = dict(model=model, prompt=prompt, seconds=seconds, ratio=ratio, **kw)
        r = requests.post(self.base + "/v1/videos", headers=self.h, json=body, timeout=60)
        r.raise_for_status()
        return r.json()

    def videos_retrieve(self, video_id):
        return requests.get(self.base + "/v1/videos/" + video_id, headers=self.h, timeout=60).json()

    def videos_content(self, video_id, path="out.mp4"):
        url = self.base + "/v1/videos/%s/content" % video_id
        data = requests.get(url, headers={"Authorization": "Bearer " + self.key}, timeout=900).content
        open(path, "wb").write(data)
        return path

    def wait(self, video_id, interval=10, timeout=2700):
        t0 = time.time()
        while time.time() - t0 < timeout:
            job = self.videos_retrieve(video_id)
            if job["status"] in ("completed", "failed", "canceled"):
                return job
            time.sleep(interval)
        raise TimeoutError(video_id)


if __name__ == "__main__":
    api = SeedancePool()
    print([m["id"] for m in api.models()][:6])
    job = api.videos_create("a lone astronaut walks across a red desert at dusk, slow tracking shot")
    print(job["id"], job["status"])
    done = api.wait(job["id"])
    print(done["status"], done.get("duration"), done.get("bytes"))
    if done["status"] == "completed":
        print(api.videos_content(job["id"]))

# Pippit Pool API ? ?? + OpenAI ??????

? Pippit?Dreamina Seedance????????????? API Key?
?????? Cookie???????????????? HTTP?

- ? HTTP?submit_run -> get_thread -> PippitAssetID -> ??? URL -> ??
- ?????Smart/Auto 1080p / 30.000s / 1080x1920 / 30fps / ???
- ?????120 ??4 ?/??720p ? 1080p ???
- ???SQLite ???????????????????? line_locks ??
- Key????????????????????

## ??

    cd C:\Users\Administrator\Documents\Codex\2026-10-15\sd2-5-30-tg-x-sd2-3\pool_api
    python app.py

??????????? run.bat??????????????
???? 0.0.0.0:8788?

?????

| ?? | ?? | ?? |
|---|---|---|
| WZ_PORT | 8788 | ?? |
| WZ_HOST | 0.0.0.0 | ??????????? 127.0.0.1 |
| WZ_MAX_WORKERS | 2 | ?????????? 5-6 ?? |
| WZ_PER_KEY_CONCURRENCY | 2 | ?? Key ???? |
| WZ_MAX_SECONDS | 30 | ???? |
| WZ_AUTO_CLAIM | 0 | ? 1 ?????????? |
| WZ_ADMIN_TOKEN | ???? | ?? Token????? data/admin_token.txt |

?????

- pool_api/data/pool.db
- pool_api/data/admin_token.txt
- pool_api/data/videos/{video_id}.mp4

## ? Key

???????X-Admin-Token: <data/admin_token.txt ??>

    POST /admin/keys
    {"name":"grandpa","quota":0,"expires_in_days":null}

???? key?sk-wz-...???????

## ????

    POST /admin/accounts/import
    {"paths":["...\\work\\funded_serial_1792298189.json"],"bootstrap":true,"min_credit":0}

??????? dict??? dict ?????????????????funded_*.json??

bootstrap=true ?? workspace_id/space_id ?????

## ????

?????

    GET /v1/models

?? 30s 1080p ???

    POST /v1/videos
    Authorization: Bearer sk-wz-...
    Content-Type: application/json

    {
      "model": "pippit-smart-1080p-30s",
      "prompt": "Vertical 9:16 30-second coffee commercial, six 5-second shots, no text, no logos.",
      "seconds": 30,
      "size": "1080x1920"
    }

???

    {"id":"video_...","object":"video","status":"queued","progress":0,
     "model":"pippit-smart-1080p-30s","seconds":30,"size":"1080x1920"}

???

    GET /v1/videos/{id}
    Authorization: Bearer sk-wz-...

???queued -> in_progress -> completed / failed

??????

    {"width":1080,"height":1920,"duration":30.0,"bytes":45155222,
     "asset_id":"...","output_url":"http://host/v1/videos/{id}/content"}

???

    GET /v1/videos/{id}/content
    Authorization: Bearer sk-wz-...

???

    GET /v1/videos?limit=50

???? queued??

    POST /v1/videos/{id}/cancel

## Python ??

```python
import requests, time
B = "http://127.0.0.1:8788"
H = {"Authorization": "Bearer sk-wz-..."}

j = requests.post(B + "/v1/videos", headers=H, json={
    "model": "pippit-smart-1080p-30s",
    "prompt": "Vertical 9:16 30-second nature film, six 5-second shots, no text, no logos.",
    "seconds": 30, "size": "1080x1920",
}).json()

while True:
    s = requests.get(B + "/v1/videos/" + j["id"], headers=H).json()
    print(s["status"], s["progress"])
    if s["status"] in ("completed", "failed"):
        break
    time.sleep(15)

if s["status"] == "completed":
    r = requests.get(B + "/v1/videos/" + j["id"] + "/content", headers=H)
    open("out.mp4", "wb").write(r.content)
```

## ????

| ?? | ?? | ?? |
|---|---|---|
| POST | /admin/keys | ? Key |
| GET | /admin/keys | ? Key |
| DELETE | /admin/keys/{id} | ?? |
| POST | /admin/accounts/import | ???? |
| GET | /admin/accounts | ??????? |
| POST | /admin/accounts/refresh | ?????{"claim":true} ???? |
| GET | /admin/jobs | ???? |
| GET | /healthz | ???? |

## ?????

- 30s 1080p = 120 ?
- 340 ??? = 2 ? + 100 ??
- 220 ? = 1 ? + 100 ??
- 100 ? = ?? 30s???????????

??? 5-6 ???WZ_MAX_WORKERS=2 ?? 5-6 ??? 2 ??

## ?????

??? _r329_line_multi.py ?? work\line_locks\{uid}.lock?????????????

## ??

- ??????? WZ_HOST=127.0.0.1???????? TLS
- ?? Token ?????
- ??????? Key?? quota ? expires_in_days
- pool.db ??? Cookie???????

## ??

    pool_api/
      app.py            FastAPI ?? + ?? + ???
      db.py             SQLite
      worker.py         ?? / ?? / ?? / ?? / ??
      pippit.py         Pippit ? HTTP ???
      run.bat           ????
      import_accounts.py ????
      PROTOCOL.md       ??????
      data/             pool.db / admin_token.txt / videos/

## 补货

新号注册仍用现有串行脚本（US 出口、22030-22032 轮换）：

    python work\_r643_serial_reg.py 20 SG GkDU4hVnfRjT R65xSG 45

跑完会生成 work\funded_serial_<ts>.json，然后：

    python pool_api\import_accounts.py --glob "work\funded_serial_*.json"

号池会自动按余额选号；0 分号不会接 30s 任务。

## OpenAPI

FastAPI 自带：

- http://127.0.0.1:8788/docs
- http://127.0.0.1:8788/openapi.json
- 本目录 openapi.json 是导出快照

## Reference material (image / video / audio)

POST /v1/videos accepts optional reference inputs (local path or http(s) URL):

    {
      "model": "pippit-smart-1080p-30s",
      "prompt": "Use the reference image style, 30s vertical film.",
      "seconds": 30, "size": "1080x1920",
      "reference_image_url": "C:\\path\\ref.png",
      "reference_video_url": "https://example.com/ref.mp4",
      "reference_audio_url": "C:\\path\\ref.mp3"
    }

Aliases: 
eference_image / 
eference_video / 
eference_audio.

Each reference is uploaded per job (prepare_upload_cloud -> ApplyUploadInner ->
upload/v1 -> CommitUploadInner -> create_cloud_asset -> asset/create_v2) and
submitted as a part with the captured live shape:

- image: iz/x_data_upload_image, {"image":{name,url,metadata{md5,name,width,height,size},asset_id}}
- video: iz/x_data_upload_video, {"video":{name,url,metadata{md5,name,width,height,duration_ms},asset_id}}
- audio: iz/x_data_upload_audio, {"audio":{name,url,metadata{md5,format,duration,size},asset_id,security_check_scene:[]}}

sset_id is the EntryID returned by create_cloud_asset (data.cloud_asset.asset_id),
NOT the PippitAssetID. The final job JSON includes 
eferences when any were used.

## 部署（生产服务器）

    服务器: 127.0.0.1
    目录:   /opt/pippit-pool
    服务:   systemd `pippit-pool`（enabled，Restart=always）
    端口:   8788（WZ_MAX_WORKERS=2 / WZ_PER_KEY_CONCURRENCY=2）
    日志:   /var/log/pippit-pool.log
    健康:   curl http://127.0.0.1:8788/healthz
    后台:   http://127.0.0.1:8000/master（TOTP 六位码登录，管理号池）
    Key:    data/srv_main_key.json（首次用 /admin/keys 生成后保存）

常用命令：

    systemctl status pippit-pool
    systemctl restart pippit-pool
    tail -f /var/log/pippit-pool.log

## 时长与参考素材的实测边界（重要）

| 场景 | 实际输出 |
|---|---|
| 纯文本 + video_resolution=720p（代码默认） | **1080x1920 / 30.000s / 900 帧** |
| 纯文本 + video_resolution=1080p | 1080x1920，但被压到 ~19s |
| 带 reference_image / reference_video | 平台注入 "imitated video must be 10-20 sec"，输出 15~19s |
| 带 reference_audio（必须配图/视频） | 同上，10~20s |

结论：**30s 量产只走纯文本通道**；参考素材接口用于 ≤20s 的图生视频 / 视频参考 / 音频参考任务。
`worker.py` 会在 prompt 未写明时长时自动补 "30-second video, 6 shots of 5 seconds each."，
需要覆盖 wire 分辨率时可用环境变量 `PP_WIRE_RES=1080p`。

## 总台面板（/master）

    地址: http://127.0.0.1:8788/master

- 首次打开：显示二维码 → 用 Google Authenticator / 1Password / Authy 扫码 → 输入 6 位数字完成绑定并登录
- 之后每次：直接输入 6 位验证码登录（与豆包总台同一套体验）
- 会话：HMAC 签名 HttpOnly Cookie，7 天有效；连续输错 12 次锁定 5 分钟
- 页面功能：总览 KPI、任务列表（进度条 / 弹窗播放 / 事件日志）、Key 创建与撤销、号池账号、清理策略
- 忘记验证器：在服务器执行
  `sqlite3 /opt/pippit-pool/data/pool.db "update settings set v='' where k in ('master_totp_active','master_totp_secret')"`
  后刷新页面重新扫码

## 自动清理（media sweep）

默认策略（可在面板「清理」页修改）：

| 设置 | 默认 | 说明 |
|---|---|---|
| 保留天数 | 7 天 | 超过天数的成片删除本地 mp4，任务记录保留 |
| 视频总量上限 | 20 GB | 超过则从最旧的开始删 |
| 低磁盘保护 | 剩余 < 5 GB | 自动删到 > 8 GB |
| 执行频率 | 每 30 分钟 | `WZ_SWEEP_INTERVAL` 可调；`WZ_MEDIA_SWEEP=0` 关闭 |

手动：`POST /master/api/sweep?dry_run=true`（预览）或 `?dry_run=false`（执行），需面板登录或 `X-Admin-Token`。
被清理的任务 `/v1/videos/{id}/content` 返回 410，元数据仍在。

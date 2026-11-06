"""pigmalion 댓글 자동 응답: 키워드 댓글 → 대댓글 + 비공개 답장 DM 1개(자료실 링크).
GitHub Actions에서 몇 분마다 실행. 로컬: IG_TOKEN, IG_USER_ID 환경변수 넣고 python bot/responder.py
상태 파일 없음: 우리 계정이 이미 대댓글을 단 댓글은 건너뛴다.
ponytail: Standard Access라 댓글당 DM 1개·글자만. 버튼→팔로우 확인→여러 DM은 앱 심사 뒤에.
"""
import json, os, urllib.parse, urllib.request
from pathlib import Path

T, IG = os.environ["IG_TOKEN"], os.environ["IG_USER_ID"]
ME = "pigmalion.kr"
G = "https://graph.facebook.com/v23.0"
SITE = "https://kimisbrother92.github.io/pigmalion-ig-media/"
POSTS = json.loads((Path(__file__).resolve().parent.parent / "posts.json").read_text(encoding="utf-8"))

def call(method, path, body=None, **q):
    q["access_token"] = T
    req = urllib.request.Request(G + path + "?" + urllib.parse.urlencode(q),
                                 data=json.dumps(body).encode() if body is not None else None,
                                 method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return json.load(e)

handled = 0
for p in POSTS:
    res = call("GET", f"/{p['media_id']}/comments", fields="id,text,username,replies{username}", limit=100)
    if "error" in res:
        raise SystemExit(f"comments error {p['nn']}: {res['error'].get('message')}")
    for c in res.get("data", []):
        if p["keyword"] not in c.get("text", "") or c.get("username") == ME:
            continue
        if any(r.get("username") == ME for r in c.get("replies", {}).get("data", [])):
            continue
        rep = call("POST", f"/{c['id']}/replies", message="DM 보내드렸어요 🐷")
        dm = call("POST", f"/{IG}/messages", {"recipient": {"comment_id": c["id"]}, "message": {"text":
            f"{p['dm']}\n\n{p['dm_line']} 👇\n{SITE}{p['nn']}/\n\n다음 자료도 받아보시려면 팔로우 해두세요 🙌"}})
        print(p["nn"], c.get("username"), "reply:", "ok" if "id" in rep else rep, "| dm:", "ok" if "message_id" in dm else dm)
        handled += 1
print("handled", handled)

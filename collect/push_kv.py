#!/usr/bin/env python3
# push_kv.py
# sector_latest.json + market_indicators.json 을 하나로 합쳐 Cloudflare KV("latest")에 업로드.
# 브라우저가 /api/data 로 이 값을 받아 트리맵·티커를 다시 그린다.
#
# 비밀값은 공개 레포에 절대 넣지 않는다. 홈 폴더의 파일에서 읽는다:
#   C:\Users\namdh\.ollashu_kv.json
#   { "account_id": "...", "namespace_id": "...", "api_token": "..." }
#
# 표준 라이브러리만 사용(requests 불필요).

import os
import sys
import json
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTOR = os.path.join(ROOT, "data", "sector_latest.json")
MARKET = os.path.join(ROOT, "data", "market_indicators.json")
SECRET = os.path.join(os.path.expanduser("~"), ".ollashu_kv.json")
KEY = "latest"


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    if not os.path.exists(SECRET):
        print(f"[push_kv] 비밀 파일 없음: {SECRET}", file=sys.stderr)
        sys.exit(1)
    cfg = load_json(SECRET)
    try:
        acct = cfg["account_id"]
        ns = cfg["namespace_id"]
        tok = cfg["api_token"]
    except KeyError as e:
        print(f"[push_kv] 비밀 파일에 키 누락: {e}", file=sys.stderr)
        sys.exit(1)

    d = load_json(SECTOR)
    try:
        ind = load_json(MARKET)
    except Exception:
        ind = {}

    payload = {
        "date": d.get("date", ""),
        "generated_at": d.get("generated_at", ""),
        "market": d.get("market", {}),
        "sectors": d.get("sectors", []),
        "indicators": ind,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    url = (f"https://api.cloudflare.com/client/v4/accounts/{acct}"
           f"/storage/kv/namespaces/{ns}/values/{KEY}")
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("Authorization", f"Bearer {tok}")
    req.add_header("Content-Type", "text/plain; charset=utf-8")

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status = r.status
    except Exception as e:
        print(f"[push_kv] KV 업로드 실패: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[push_kv] KV 업로드 OK ({len(body)} bytes, http {status})")


if __name__ == "__main__":
    main()

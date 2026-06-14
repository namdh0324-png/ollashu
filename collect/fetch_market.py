#!/usr/bin/env python3
# collect/fetch_market.py
# Yahoo Finance 차트 API로 글로벌 시장 지표(선물/유가/환율/금리/코인 등) 시세 수집.
# 출력: data/market_indicators.json  (값 + 등락률 = 사실 시세만. 해석/추천 없음)
#
#   python collect\fetch_market.py
#
# 지표 추가/삭제는 아래 SYMBOLS 리스트만 손보면 됨.
import os
import json
import time
from datetime import datetime

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "market_indicators.json")

# (표시이름, 야후심볼, 소수자리, 단위)  — 단위 "$"는 앞에, 나머지는 뒤에 붙음
SYMBOLS = [
    ("나스닥 선물", "NQ=F", 2, ""),
    ("S&P 선물", "ES=F", 2, ""),
    ("환율(USD)", "KRW=X", 1, "원"),
    ("WTI 유가", "CL=F", 2, "$"),
    ("美 10년물", "^TNX", 2, "%"),
    ("비트코인", "BTC-USD", 0, "$"),
]

URL = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
}


def fetch_one(sym):
    r = requests.get(URL.format(sym=sym), headers=HEADERS, timeout=10)
    r.raise_for_status()
    res = r.json()["chart"]["result"][0]
    meta = res["meta"]
    price = meta.get("regularMarketPrice")
    prev = meta.get("chartPreviousClose")
    if prev is None:
        prev = meta.get("previousClose")
    if price is None:
        raise ValueError("가격 없음")
    chg = round((price - prev) / prev * 100, 2) if prev else None
    return float(price), chg


def main():
    inds = []
    for label, sym, digits, unit in SYMBOLS:
        try:
            value, chg = fetch_one(sym)
            inds.append({"label": label, "value": value, "change_pct": chg,
                         "digits": digits, "unit": unit})
            print(f"  {label}: {value} ({chg}%)")
        except Exception as e:
            print(f"  ! {label}({sym}) 실패: {e}")
        time.sleep(0.2)

    out = {"updated": datetime.now().isoformat(timespec="seconds"), "indicators": inds}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=0)
    print(f"market_indicators.json 저장: {len(inds)}개")


if __name__ == "__main__":
    main()

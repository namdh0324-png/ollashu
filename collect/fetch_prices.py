#!/usr/bin/env python3
# fetch_prices.py  (v1 — 네이버 우회)
# 코스피+코스닥 전 종목의 "이름 + 등락률"만 빠르게 수집 → data/all_stocks.json
#
# KRX 직접 접속(pykrx / fdr StockListing)은 차단·불안정하므로 사용하지 않는다.
# stock_agent가 쓰는 것과 동일한 네이버 시세 우회로 전 종목을 긁는다.
#   https://finance.naver.com/sise/sise_market_sum.naver?sosok=0&page=N   (0=코스피 1=코스닥)
#
#   python fetch_prices.py [--date YYYY-MM-DD]
#
# 의존: requests, beautifulsoup4  (+ 지수 등락은 FinanceDataReader, 실패해도 진행)
# 출력: data/all_stocks.json
#   { collected_at, date, source,
#     market:{kospi_change, kosdaq_change, advance_pct_kospi, advance_pct_kosdaq},
#     stocks:{ "005930": {"name":"삼성전자","return_1d":1.23}, ... } }
#
# 네이버 시세는 장중 실시간 반영 → 추후 30분 갱신/NXT 단계에도 그대로 사용.

import os
import re
import sys
import json
import time
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DATA = os.path.join(PROJ, "data")
OUT = os.path.join(DATA, "all_stocks.json")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
MARKET_SUM = "https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page={page}"
MARKET_SUM_NXT = "https://finance.naver.com/sise/nxt_sise_market_sum.naver?sosok={sosok}&page={page}"
MAX_PAGES = 100
SLEEP = 0.3

# ETF/ETN/리츠/우선주 제외 — collect_macro.py EXCLUDE 와 동일 취지(이름 패턴).
EXCLUDE = re.compile(
    r'(ETN|ETF|레버리지|인버스|선물|'
    r'^KODEX|^TIGER|^KBSTAR|^HANARO|^KOSEF|^ARIRANG|^SOL\b|^PLUS\b|'
    r'^ACE\b|^RISE\b|^WOORI|^KIWOOM|^1Q\b|^TIME\b|^WON\b|^MIDAS|'
    r'^VITA\b|^UNICORN|^KoAct|^BNK\b|^TIMEFOLIO|^IBK\b|^HK\b|'
    r'^파워\b|^FOCUS|^마이티|^에셋플러스|^마이다스|^N2\b|^INVENI\b|'
    r'^TREX\b|^TRUSTON|^KCGI|^DAISHIN|^아이엠에셋|^더제이\b|^대신 |'
    r'\b200\b|200TR|200레버리지|코스피200|코스닥150|KRX300|코스피100|'
    r'KTOP30|MSCI|TR ETN|TR\b|'
    r'2X|3X|TOP[0-9]|'
    r'리츠$|리츠[0-9]|'
    r'우$|우[BC]$|[0-9]우[BC]?$|\(전환\)$)'
)

RE_CODE = re.compile(r'code=(\d{6})')


def _pct_from_row(tr):
    """행에서 등락률(부호 포함 float) 추출.
    등락률은 행에서 첫 번째 '%' 스팬(외국인비율 % 보다 앞 컬럼). 색 클래스+텍스트 부호 병행."""
    for sp in tr.find_all("span"):
        txt = sp.get_text(strip=True)
        if not txt.endswith("%"):
            continue
        mag_s = txt.replace("%", "").replace(",", "").replace("+", "").replace("-", "").strip()
        try:
            mag = float(mag_s)
        except ValueError:
            return None
        cls = " ".join(sp.get("class", []))
        if txt.startswith("-") or "nv" in cls or "down" in cls or "blue" in cls:
            return round(-mag, 2)
        if txt.startswith("+") or "red" in cls or "up" in cls:
            return round(mag, 2)
        return round(mag, 2)
    return None


def _parse_page(html):
    """(code, name, change) 리스트. 종목 행 = code= 링크(a.tltle) 보유 행."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    seen_in_page = set()
    for a in soup.find_all("a", href=True):
        m = RE_CODE.search(a["href"])
        if not m:
            continue
        cls = " ".join(a.get("class", []))
        if "tltle" not in cls and "/item/main" not in a["href"]:
            continue
        code = m.group(1)
        name = a.get_text(strip=True)
        if not name or code in seen_in_page:
            continue
        tr = a.find_parent("tr")
        if tr is None:
            continue
        chg = _pct_from_row(tr)
        if chg is None:
            continue
        seen_in_page.add(code)
        rows.append((code, name, chg))
    return rows


def _scrape_market(sosok, url_tmpl=MARKET_SUM):
    session = requests.Session()
    collected = {}
    for page in range(1, MAX_PAGES + 1):
        url = url_tmpl.format(sosok=sosok, page=page)
        try:
            r = session.get(url, headers=HEADERS, timeout=10)
            r.encoding = "euc-kr"
        except Exception as e:
            print(f"    page {page} 요청 실패: {e}", file=sys.stderr)
            break
        rows = _parse_page(r.text)
        new = 0
        for code, name, chg in rows:
            if code not in collected:
                collected[code] = (name, chg)
                new += 1
        if new == 0:        # 새 종목 없음 = 마지막 페이지 지남
            break
        time.sleep(SLEEP)
    return collected


def _index_change(date_str):
    """KOSPI/KOSDAQ 등락률 — 네이버 실시간 지수 폴링 API. 실패 시 None."""
    res = {}
    for key, code in [("kospi", "KOSPI"), ("kosdaq", "KOSDAQ")]:
        try:
            url = "https://polling.finance.naver.com/api/realtime/domestic/index/" + code
            r = requests.get(url, headers={**HEADERS, "Referer": "https://finance.naver.com/"}, timeout=10)
            d = r.json()["datas"][0]
            ratio = abs(float(str(d.get("fluctuationsRatio", "0")).replace(",", "")))
            if (d.get("compareToPreviousPrice") or {}).get("name", "") == "FALLING":
                ratio = -ratio
            res[key] = round(ratio, 2)
        except Exception:
            res[key] = None
    return res


def collect(date_str):
    stocks = {}
    breadth = {}
    for label, sosok in [("KOSPI", 0), ("KOSDAQ", 1)]:
        raw = _scrape_market(sosok)
        adv = tot = 0
        for code, (name, chg) in raw.items():
            if EXCLUDE.search(name):
                continue
            stocks[code] = {"name": name, "return_1d": chg}
            tot += 1
            if chg > 0:
                adv += 1
        breadth[label] = round(adv / tot * 100, 1) if tot else None
        print(f"  {label}: {tot}종목 (상승비율 {breadth[label]}%)")

    nxt_matched = 0
    for sosok in (0, 1):
        raw_nxt = _scrape_market(sosok, MARKET_SUM_NXT)
        for code, (name, chg) in raw_nxt.items():
            if code in stocks:
                stocks[code]["return_1d_nxt"] = chg
                nxt_matched += 1
    print(f"  NXT: {nxt_matched}종목 매칭")

    idx = _index_change(date_str)
    payload = {
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": date_str,
        "source": "naver sise_market_sum (+nxt)",
        "market": {
            "kospi_change": idx.get("kospi"),
            "kosdaq_change": idx.get("kosdaq"),
            "advance_pct_kospi": breadth.get("KOSPI"),
            "advance_pct_kosdaq": breadth.get("KOSDAQ"),
        },
        "stocks": stocks,
    }
    os.makedirs(DATA, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"[OK] {OUT}  ·  전 종목 {len(stocks)}개  ·  {date_str}")
    return payload


def main():
    date_str = None
    if "--date" in sys.argv:
        date_str = sys.argv[sys.argv.index("--date") + 1]
    date_str = date_str or datetime.today().strftime("%Y-%m-%d")
    collect(date_str)


if __name__ == "__main__":
    main()

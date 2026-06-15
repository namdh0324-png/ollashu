#!/usr/bin/env python3
# fetch_theme_news.py  (v2 — 노이즈 필터 강화)
# sector_latest.json의 강한 테마(tier>=1)별로 "촉매성" 뉴스 헤드라인+원문링크를 모은다.
# AI 합성 없음 — 실제 헤드라인만.
#   필터: ① 규제경고/칼럼 하드 차단  ② 원인 키워드 가점/증상 감점
#         ③ 관련성 게이트(제목에 테마 키워드 or 검색 종목명 필수)
#         ④ 여러 테마에 도배되는 헤드라인은 일반뉴스로 전역 제거
#
#   python fetch_theme_news.py
#
# 환경변수: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
# 입력:  data/sector_latest.json     출력: data/theme_news.json

import os
import re
import sys
import json
import html
import time
import urllib.parse
import urllib.request
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DATA = os.path.join(PROJ, "data")
SECTOR = os.path.join(DATA, "sector_latest.json")
OUT = os.path.join(DATA, "theme_news.json")

NEWS_PER_THEME = 3
RECENCY_DAYS = 2
STRONG_MIN = 5.0
TOP_STOCKS = 2
SLEEP = 0.15
GENERIC_THEME_LIMIT = 3      # 이보다 많은 테마에 등장하는 헤드라인 = 일반뉴스(전역 제거)

# 하드 차단 — 규제경고/관리/칼럼/날씨/행사 등. 매치되면 무조건 버림.
BLOCK = ["투자경고", "투자주의", "투자위험", "투자주의종목", "변동성 확대", "변동성확대",
         "관리종목", "거래정지", "단기과열", "불성실공시", "상장폐지", "공매도",
         "주린이", "투자노트", "투자법", "필승", "멘토", "거품론", "재테크",
         "날씨", "기온", "나들이", "미세먼지 농도", "거리응원", "국가대표", "응원",
         "창업경진대회", "인수위", "민선", "지사", "시장직", "[샷!]", "[패트롤]",
         "[기고]", "[CEO&뉴스]", "오늘의 운세", "칼럼", "공모전", "[업앤다운]",
         "특가", "ETF 수익률", "수익률 톱", "수익률 상위",
         "부고", "모친상", "별세", "빈소",
         "e스포츠", "이스포츠", "MSI", "LCK",
         "힐링", "브랜드 필름", "방문 교체", "가족 초청", "WRC", "[포토]",
         "반입 제한", "반입 금지", "휴대 금지"]

# 자동 주가 리캡 봇 패턴(증상만) — 정규식 차단.
BLOCK_RE = [
    re.compile(r"최근\s*\d+\s*거래일"),
    re.compile(r"\d\s*주차.*주가"),
    re.compile(r"주가[,\s].*(횡보|돌파|오름세|내림세|급등세|강세 마감)"),
    re.compile(r"\d+\.?\d*\s*%\s*(상승|하락|오름|내림)\s*마감"),
    re.compile(r"주가[,\s].*\d+월\s*\d+일"),
]

# 비경제·비뉴스 도메인 차단(게임/e스포츠/교민지/홍보성 소형매체).
# netloc에 아래 문자열이 들어가면 후보에서 제외. 새 노이즈 도메인 발견 시 추가.
BLOCK_DOMAIN = [
    "game.", "dailyesports", "esports", "gamechosun", "thisisgame",
    "inven.co.kr", "ruliweb", "gameple",
    "worldkorean", "dongponews", "koreadaily",
    "paxetv", "lawissue", "seoultimes.news",
    "seouleconews", "cnbizm", "onews.tv",
]

# 원인(촉매) — 가점. 헐거운 단어(투자/확대/진출/선정 등)는 제외해 노이즈 차단.
CAUSE = ["수주", "계약", "공급", "납품", "실적", "흑자", "어닝", "출시", "신제품",
         "정책", "예산", "승인", "허가", "인증", "특허", "증설", "합병", "인수",
         "협약", "파트너", "수출", "임상", "수요", "체결", "양산", "국산화",
         "공동개발", "착공", "준공", "낙찰", "공시 호재"]

# 증상(결과 묘사) — 감점.
SYMPTOM = ["급등", "급락", "신고가", "신저가", "상한가", "하한가", "순매수", "순매도",
           "폭등", "폭락", "52주", "시간외", "들썩", "강세", "약세", "껑충", "치솟",
           "급반등", "오름세", "내림세", "관심주", "테마주", "변동성", "수급"]

THEME_STOP = {"등", "주요", "종목", "관련", "발행", "개선", "활용", "저장", "및", "외",
              "산업용", "수도권", "양적", "질적", "해체"}

SOURCE_MAP = {
    'mk.co.kr': '매일경제', 'hankyung.com': '한국경제', 'sedaily.com': '서울경제',
    'fnnews.com': '파이낸셜뉴스', 'edaily.co.kr': '이데일리', 'mt.co.kr': '머니투데이',
    'news.naver.com': '네이버', 'n.news.naver.com': '네이버', 'biz.chosun.com': '조선비즈',
    'newspim.com': '뉴스핌', 'businesspost.co.kr': '비즈니스포스트', 'ajunews.com': '아주경제',
    'newsis.com': '뉴시스', 'yna.co.kr': '연합뉴스', 'inews24.com': '아이뉴스24',
    'etnews.com': '전자신문', 'thelec.kr': '디일렉', 'ddaily.co.kr': '디지털데일리',
}


def _creds():
    cid = os.environ.get("NAVER_CLIENT_ID")
    sec = os.environ.get("NAVER_CLIENT_SECRET")
    if not cid or not sec:
        print("[ERROR] NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수 없음.", file=sys.stderr)
        sys.exit(2)
    return cid, sec


def _clean(t):
    if not t:
        return ""
    t = re.sub(r'<[^>]+>', '', t)
    return html.unescape(t).strip()


def _source(url):
    try:
        from urllib.parse import urlparse
        dom = urlparse(url).netloc.replace('www.', '')
        for k, v in SOURCE_MAP.items():
            if k in dom:
                return v
        return dom
    except Exception:
        return ""


def _pub(s):
    try:
        return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d %H:%M")
    except Exception:
        return s


def naver_search(query, cid, sec, display=12):
    url = ("https://openapi.naver.com/v1/search/news.json?query="
           + urllib.parse.quote(query) + f"&display={display}&sort=date")
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", cid)
    req.add_header("X-Naver-Client-Secret", sec)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"    검색 실패 [{query}]: {e}", file=sys.stderr)
        return []
    out = []
    for it in data.get("items", []):
        link = it.get("originallink") or it.get("link") or ""
        out.append({
            "title": _clean(it.get("title", "")),
            "url": link,
            "source": _source(link),
            "date": _pub(it.get("pubDate", "")),
        })
    return out


def _recent(item, today):
    ds = (item.get("date") or "").split()[0]
    if not ds:
        return True
    try:
        nd = datetime.strptime(ds, "%Y-%m-%d").date()
    except Exception:
        return True
    return 0 <= (today - nd).days <= RECENCY_DAYS


def _theme_keywords(theme):
    base = re.sub(r'\(.*?\)', '', theme)
    toks = re.split(r'[\s/·,]+', base)
    return [t for t in toks if len(t) >= 2 and t not in THEME_STOP]


def _blocked(title):
    if any(b in title for b in BLOCK):
        return True
    return any(rx.search(title) for rx in BLOCK_RE)


def _domain_blocked(url):
    try:
        dom = urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return False
    return any(b in dom for b in BLOCK_DOMAIN)


_DUP_STOP = {"규모", "사업", "발표", "기업", "대표", "관련", "위해", "통해", "예정", "전망", "분기"}


def _dup(title, picked_titles):
    """이미 뽑힌 제목과 토큰 50% 이상 겹치면 근사 중복(같은 기사 다른 매체)."""
    def toks(t):
        t = re.sub(r'[\[\]()·,…"\'%↑↓\-]', ' ', t)
        t = re.sub(r'\d+\S*', ' ', t)   # 숫자 포함 토큰(601억 등) 제거
        return {w for w in re.split(r'\s+', t) if len(w) >= 2 and w not in _DUP_STOP}
    a = toks(title)
    if not a:
        return False
    for p in picked_titles:
        b = toks(p)
        if b and len(a & b) / min(len(a), len(b)) >= 0.5:
            return True
    return False


def _stock_of(title, stocks):
    for s in stocks:
        if s and s in title:
            return s
    return None


def _relevant(title, kws, stocks):
    if any(k in title for k in kws):
        return True
    if any(s and s in title for s in stocks):
        return True
    return False


def _score(title):
    c = sum(1 for w in CAUSE if w in title)
    s = sum(1 for w in SYMPTOM if w in title)
    return c * 2 - s


def _candidates(items, today, kws, stocks):
    """블록+최신+관련성 통과한 후보(중복 제거, 점수 부여)."""
    seen = set()
    out = []
    for it in items:
        t = it["title"]
        key = re.sub(r'\s+', '', t)
        if not t or key in seen:
            continue
        if (_domain_blocked(it.get("url", "")) or _blocked(t)
                or not _recent(it, today) or not _relevant(t, kws, stocks)):
            continue
        seen.add(key)
        it = dict(it)
        it["_score"] = _score(t)
        it["_key"] = key
        out.append(it)
    return out


def main():
    cid, sec = _creds()
    if not os.path.exists(SECTOR):
        print(f"[ERROR] sector_latest.json 없음: {SECTOR}", file=sys.stderr)
        sys.exit(1)
    with open(SECTOR, encoding="utf-8") as f:
        snap = json.load(f)

    today = datetime.today().date()
    targets = [s for s in snap.get("sectors", []) if s.get("tier", 0) >= 1]
    print(f"대상 테마(tier>=1): {len(targets)}개")

    # 1차: 테마별 후보 수집
    cand = {}
    stock_map = {}
    for i, s in enumerate(targets, 1):
        theme = s["theme"]
        kws = _theme_keywords(theme)
        stocks = [m["name"] for m in s.get("stocks", []) if m.get("change", 0) >= STRONG_MIN][:TOP_STOCKS]
        stock_map[theme] = stocks
        pool = []
        for q in [re.sub(r'\(.*?\)', '', theme).strip()] + stocks:
            pool += naver_search(q, cid, sec)
            time.sleep(SLEEP)
        cand[theme] = _candidates(pool, today, kws, stocks)
        if i % 10 == 0 or i == len(targets):
            print(f"  수집 {i}/{len(targets)}")

    # 2차: 여러 테마에 도배되는 헤드라인 = 일반뉴스 → 전역 제거
    freq = {}
    for items in cand.values():
        for it in items:
            freq[it["_key"]] = freq.get(it["_key"], 0) + 1
    generic = {k for k, n in freq.items() if n > GENERIC_THEME_LIMIT}
    if generic:
        print(f"  일반뉴스 전역 제거: {len(generic)}건")

    # 3차: 테마별 최종 — 일반뉴스 제외, 촉매(>=1) 우선 + 중립(0) 보충, 증상(<0) 제외, 근사중복 제거
    themes_news = {}
    for theme, items in cand.items():
        items = [it for it in items if it["_key"] not in generic]
        cause = sorted([x for x in items if x["_score"] >= 1], key=lambda x: x["_score"], reverse=True)
        neutral = [x for x in items if x["_score"] == 0]
        picked = []
        used_stocks = set()
        for x in cause + neutral:
            if len(picked) >= NEWS_PER_THEME:
                break
            st = _stock_of(x["title"], stock_map.get(theme, []))
            if st and st in used_stocks:       # 같은 종목 기사 1개만
                continue
            if _dup(x["title"], [p["title"] for p in picked]):
                continue
            picked.append(x)
            if st:
                used_stocks.add(st)
        clean = [{"title": x["title"], "url": x["url"], "source": x["source"], "date": x["date"]}
                 for x in picked]
        if clean:
            themes_news[theme] = clean

    result = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": snap.get("date", ""),
        "themes": themes_news,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    total = sum(len(v) for v in themes_news.values())
    print(f"[OK] {OUT}  ·  뉴스 있는 테마 {len(themes_news)}개 · 헤드라인 총 {total}개")


if __name__ == "__main__":
    main()

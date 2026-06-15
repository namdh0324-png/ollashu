#!/usr/bin/env python3
# build_sectors.py
# all_stocks.json(전 종목 등락률) + theme_map.json(테마 매핑) → sector_latest.json
#
# run_scanner.py의 테마 집계 로직을 그대로 이식한다(로직 동일, 출력 동일 구조).
#   - 강세 기준: return_1d >= 5.0%
#   - weighted_strong: 강세 멤버의 Σ(1/소속테마수)  (전용주↑ 제너럴리스트↓)
#   - tier: 평균≥6% & W≥2.0 → 2 / 평균≥4% & W≥1.0 → 1 / else 0
#   - 출력: strong_count≥1 테마만, W 내림차순
# 추가: 각 테마의 구성 종목(이름+등락률)도 stocks[]로 — 점수/등급/추천 일절 없음(법적 안전).
#
#   python build_sectors.py
#
# 입력:  data/all_stocks.json , data/meta/theme_map.json , data/meta/theme_blocklist.json
# 출력:  data/sector_latest.json

import os
import sys
import json
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)                       # krx_heatmap/
DATA = os.path.join(PROJ, "data")
META = os.path.join(DATA, "meta")
ALL_STOCKS = os.path.join(DATA, "all_stocks.json")
THEME_MAP = os.path.join(META, "theme_map.json")
THEME_BLOCKLIST = os.path.join(META, "theme_blocklist.json")
OUT = os.path.join(DATA, "sector_latest.json")

# ── run_scanner.py 상수 (동일값) ─────────────────────────────
THEME_STRONG_THRESHOLD = 5.0   # +5% 이상이면 "강한 강세"
THEME_TIER1_AVG = 4.0
THEME_TIER2_AVG = 6.0
THEME_W_TIER1 = 1.0            # 가중강세합 ≥1.0 AND 평균 ≥4% → Tier1
THEME_W_TIER2 = 2.0            # 가중강세합 ≥2.0 AND 평균 ≥6% → Tier2

STOCKS_PER_THEME = 20          # 구성 종목 표시 상한(등락률 상위) — 페이로드 절약


def load_theme_map():
    """theme_map.json + theme_blocklist.json 로드.
    반환: (themes{name:{tickers}}, ticker_themes{code:[names]}, blocklist:set)"""
    if not os.path.exists(THEME_MAP):
        print(f"[ERROR] theme_map.json 없음: {THEME_MAP}", file=sys.stderr)
        print("        stock_agent의 data/meta/theme_map.json 을 여기로 복사하세요.", file=sys.stderr)
        sys.exit(2)
    with open(THEME_MAP, encoding="utf-8") as f:
        data = json.load(f)
    themes = data.get("themes", {})
    ticker_themes = data.get("ticker_themes", {})
    blocklist = set()
    if os.path.exists(THEME_BLOCKLIST):
        with open(THEME_BLOCKLIST, encoding="utf-8") as f:
            blocklist = set(json.load(f).get("blocklist", []))
    return themes, ticker_themes, blocklist


def build_spec_weight(ticker_themes, blocklist):
    """전문성 가중치 = 1/소속테마수(블록 제외). run_scanner와 동일."""
    spec = {}
    for code, names in ticker_themes.items():
        n = sum(1 for nm in names if nm not in blocklist)
        spec[code] = 1.0 / n if n > 0 else 0.0
    return spec


def theme_tier(avg_return, weighted_strong):
    """run_scanner calculate_theme_map_bonus 의 tier 부분(동일)."""
    if avg_return >= THEME_TIER2_AVG and weighted_strong >= THEME_W_TIER2:
        return 2
    if avg_return >= THEME_TIER1_AVG and weighted_strong >= THEME_W_TIER1:
        return 1
    return 0


def compute_theme_momentum(all_stocks, themes, blocklist, spec_weight, field="return_1d", skip_missing=False):
    """run_scanner compute_theme_map_momentum 이식(로직 동일) + 구성 종목 부가.
    반환: {name: {avg_return, strong_count, weighted_strong, data_count, total_count, members[]}}
    members[] = [{name, change}] (등락률 내림차순) — 사실 정보만."""
    stats = {}
    for name, info in themes.items():
        if name in blocklist:
            continue
        tickers = info.get("tickers", [])
        returns = []
        strong = 0
        up = 0
        wstrong = 0.0
        members = []
        for t in tickers:
            s = all_stocks.get(t)
            if not s:
                continue
            ret = s.get(field)
            if ret is None:
                if skip_missing:
                    continue
                ret = 0
            returns.append(ret)
            members.append({"name": s.get("name", t), "change": round(float(ret), 2)})
            if ret > 0:
                up += 1
            if ret >= THEME_STRONG_THRESHOLD:
                strong += 1
                wstrong += spec_weight.get(t, 0.0)
        if not returns:
            continue
        members.sort(key=lambda m: m["change"], reverse=True)
        stats[name] = {
            "avg_return": round(sum(returns) / len(returns), 2),
            "strong_count": strong,
            "weighted_strong": round(wstrong, 2),
            "up_pct": round(up / len(returns) * 100),
            "data_count": len(returns),
            "total_count": len(tickers),
            "members": members[:STOCKS_PER_THEME],
        }
    return stats


def market_label(kospi_change, advance_pct):
    """간이 시장 라벨 — 핸드오버 임계값 기준. (스캐너 label_market과 추후 정렬 가능)"""
    if advance_pct is not None:
        if advance_pct <= 15:
            return "NARROW_EXTREME"
        if advance_pct <= 25:
            return "NARROW"
    c = kospi_change if kospi_change is not None else 0
    if c >= 2.0:
        return "BULL"
    if c >= 0.7:
        return "STRONG"
    if c >= -0.7:
        return "NORMAL"
    if c >= -2.0:
        return "WEAK"
    return "EXTREME"


def _sectors_from_stats(stats):
    sectors = []
    for name, info in stats.items():
        if info["strong_count"] < 1:
            continue
        tier = theme_tier(info["avg_return"], info["weighted_strong"])
        sectors.append({
            "theme": name,
            "avg_return": info["avg_return"],
            "strong_count": info["strong_count"],
            "weighted_strong": info["weighted_strong"],
            "up_pct": info["up_pct"],
            "data_count": info["data_count"],
            "total_count": info["total_count"],
            "tier": tier,
            "stocks": info["members"],   # 구성 종목(이름+등락률) — 펼침 패널용
        })
    sectors.sort(key=lambda x: x["weighted_strong"], reverse=True)
    return sectors


def build_snapshot(payload, themes, ticker_themes, blocklist):
    all_stocks = payload.get("stocks", {})
    market = payload.get("market", {})
    date_str = payload.get("date") or datetime.today().strftime("%Y-%m-%d")

    spec = build_spec_weight(ticker_themes, blocklist)
    stats = compute_theme_momentum(all_stocks, themes, blocklist, spec)
    sectors = _sectors_from_stats(stats)
    stats_nxt = compute_theme_momentum(all_stocks, themes, blocklist, spec,
                                       field="return_1d_nxt", skip_missing=True)
    sectors_nxt = _sectors_from_stats(stats_nxt)

    label = market_label(market.get("kospi_change"), market.get("advance_pct_kospi"))
    return {
        "date": date_str,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market": {
            "kospi_change": market.get("kospi_change"),
            "kosdaq_change": market.get("kosdaq_change"),
            "label": label,
        },
        "sector_count": len(sectors),
        "sectors": sectors,
        "sector_count_nxt": len(sectors_nxt),
        "sectors_nxt": sectors_nxt,
        "disclaimer": "본 데이터는 공개 시세 정보 기반 시장 현황 요약이며 투자 권유가 아닙니다.",
    }


def main():
    if not os.path.exists(ALL_STOCKS):
        print(f"[ERROR] all_stocks.json 없음: {ALL_STOCKS}", file=sys.stderr)
        print("        먼저 fetch_prices.py 를 실행해 전 종목 등락률을 수집하세요.", file=sys.stderr)
        sys.exit(1)
    with open(ALL_STOCKS, encoding="utf-8") as f:
        payload = json.load(f)

    themes, ticker_themes, blocklist = load_theme_map()
    snap = build_snapshot(payload, themes, ticker_themes, blocklist)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(snap, f, ensure_ascii=False, indent=2)

    print(f"[OK] {OUT}")
    print(f"     날짜 {snap['date']} · 라벨 {snap['market']['label']} · 섹터 {snap['sector_count']}개 · NXT섹터 {snap['sector_count_nxt']}개")
    t2 = sum(1 for s in snap["sectors"] if s["tier"] == 2)
    t1 = sum(1 for s in snap["sectors"] if s["tier"] == 1)
    print(f"     Tier2 {t2}개 · Tier1 {t1}개")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# update.py
# 한 번의 갱신 사이클: 전종목 수집 → 섹터 집계 → 사이트 빌드.
# Task Scheduler가 장중 30분마다 이 파일을 venv 파이썬으로 직접 실행한다(bat 불필요).
#
#   python update.py
#
# 각 단계 결과를 update.log 에 타임스탬프로 박제(블랙박스). 한 단계라도 실패하면
# 그 사이클은 중단(다음 30분 트리거가 재시도). 배포 단계가 되면 마지막에 git push 한 줄 추가.

import os
import sys
import subprocess
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
COLLECT = os.path.join(ROOT, "collect")
LOG = os.path.join(ROOT, "update.log")
THEME_NEWS = os.path.join(ROOT, "data", "theme_news.json")
PY = sys.executable   # 이 스크립트를 실행한 바로 그 파이썬(venv) 사용

NEWS_MAX_AGE_SEC = 2 * 3600   # 뉴스는 2시간에 한 번만 갱신(가격은 매번)

# 가격→집계는 매번, 뉴스는 throttle, 빌드는 매번
ALWAYS_PRE = [
    ("fetch_prices.py", COLLECT),
    ("build_sectors.py", COLLECT),
]
ALWAYS_POST = [
    ("build_site.py", ROOT),
]


def _news_stale():
    if not os.path.exists(THEME_NEWS):
        return True
    try:
        import time
        return (time.time() - os.path.getmtime(THEME_NEWS)) > NEWS_MAX_AGE_SEC
    except Exception:
        return True


def log(msg):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def run_step(script, cwd):
    try:
        r = subprocess.run([PY, script], cwd=cwd, capture_output=True, text=True, timeout=600)
    except Exception as e:
        log(f"  ! {script} 실행 예외: {e}")
        return False
    tail = (r.stdout or "").strip().splitlines()
    if tail:
        log(f"  {script}: {tail[-1]}")
    if r.returncode != 0:
        err = (r.stderr or "").strip().splitlines()
        log(f"  ! {script} 실패(rc={r.returncode}): {err[-1] if err else ''}")
        return False
    return True


def main():
    log("=== update 시작 ===")
    for script, cwd in ALWAYS_PRE:          # 가격·집계: 실패 시 중단
        if not run_step(script, cwd):
            log("=== 중단(단계 실패) ===")
            sys.exit(1)
    if _news_stale():                       # 뉴스: best-effort (실패해도 진행)
        if not run_step("fetch_theme_news.py", COLLECT):
            log("  (뉴스 수집 실패 — 기존 뉴스로 진행)")
    else:
        log("  뉴스 최신(2h 이내) — 수집 생략")
    run_step("fetch_market.py", COLLECT)    # 글로벌 지표: best-effort (실패해도 진행)
    for script, cwd in ALWAYS_POST:         # 빌드: 실패 시 중단
        if not run_step(script, cwd):
            log("=== 중단(단계 실패) ===")
            sys.exit(1)
    log("=== update 완료 ===")


if __name__ == "__main__":
    main()

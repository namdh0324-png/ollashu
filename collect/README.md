# collect/ — 웹용 경량 데이터 파이프라인

stock_agent의 무거운 수집(종목당 펀더멘털·수급·일봉)을 쓰지 않고,
**"이름 + 등락률"만** 빠르게 모아 섹터 집계 JSON을 만든다.

## 데이터 흐름

```
fetch_prices.py   전 종목 등락률 수집(pykrx EOD, 한 방)   →  data/all_stocks.json
      │
build_sectors.py  테마 집계(run_scanner 로직 이식)        →  data/sector_latest.json
      │           (data/meta/theme_map.json 필요)
      │
build_site.py     히트맵 HTML 생성                         →  site/
```

## 먼저 준비할 것 (stock_agent에서 복사)

집계는 테마 매핑이 있어야 한다. 아래 두 파일을 stock_agent에서 이 프로젝트로 복사:

```
stock_agent\data\meta\theme_map.json        →  krx_heatmap\data\meta\theme_map.json
stock_agent\data\meta\theme_blocklist.json  →  krx_heatmap\data\meta\theme_blocklist.json
```

(theme_blocklist.json은 없으면 생략 가능 — 블록 0개로 동작.)

## 실행 (전체 체인)

stock_agent venv 파이썬으로 실행 (pykrx·FinanceDataReader·pandas 필요):

```
cd /d C:\Users\namdh\OneDrive\Desktop\krx_heatmap\collect
python fetch_prices.py
python build_sectors.py
cd /d C:\Users\namdh\OneDrive\Desktop\krx_heatmap
python build_site.py
```

특정 날짜로 받으려면: `python fetch_prices.py --date 2026-06-12`

## 집계 로직 (run_scanner와 동일)

- 강세 = 등락률 ≥ 5.0%
- weighted_strong = 강세 멤버의 Σ(1/소속테마수)  (전용주↑ 제너럴리스트↓)
- tier = 평균≥6% & W≥2.0 → 2 / 평균≥4% & W≥1.0 → 1 / else 0
- 출력 = strong_count≥1 테마만, W 내림차순
- 각 테마 구성 종목(이름+등락률, 등락률순 상위 20)도 포함 → 펼침 패널에 표시

## 법적 안전

stocks[]에는 **이름 + 등락률만** 들어간다. 점수·등급·AI판정·추천·목표가는
파이프라인 어디에도 없다. news는 다음 단계에서 헤드라인+링크만 추가.

## 다음 단계

- **장중 30분 갱신 / NXT:** fetch_prices에 네이버 실시간 소스 모드 추가(EOD→실시간).
- **뉴스:** collect_news 재활용해 테마별 헤드라인+링크를 sector_latest.json에 부착.

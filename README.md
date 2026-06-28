# 올랐슈 (krx_heatmap) — 원리와 시스템

> 한국 증시 **테마(섹터) 히트맵** 사이트. "오늘 장에서 뭐가 올랐나"를 공개 시세로
> 한눈에 보여준다. **종목 추천 없이 시장 현황만** 정보로 제공한다.
>
> - 서비스: <https://ollashu.com>
> - 호스팅: Cloudflare (Worker + 정적 assets + KV)
> - 운영 방식: 현재는 **비영리 정보 제공** 형태로 운영 (수집 방식 관련 사유는 아래 [데이터 출처와 법적 이슈](#5-데이터-출처와-법적-이슈) 참고)

이 문서는 이 사이트가 **어떤 원리로 데이터를 모으고, 어떻게 가공해서, 어떻게 화면에
띄우는지** 전체 시스템을 설명한다. (블로그/기록용으로 정리한 문서)

---

## 1. 한 줄 요약

> 코스피·코스닥 **전 종목의 등락률**을 모아 → **테마별로 묶어 평균/강세도를 계산** →
> 강한 테마를 **히트맵(트리맵)** 으로 그려 보여준다. 추천·점수·등급은 일절 없고,
> "사실(이름 + 등락률)"만 보여준다.

---

## 2. 설계 제1원칙 — 법적 안전선

이 사이트는 **유사투자자문·저작권 리스크 회피**를 최우선으로 설계했다.
모든 기능은 아래 규칙을 넘지 않는 선에서만 만들어진다.

1. **종목 추천·매수신호·목표가·점수·등급·AI 판정 일절 금지.**
   어떤 페이지·데이터·문구에도 넣지 않는다.
2. 종목 데이터(`stocks[]`)에 담기는 필드는 **`name`(종목명), `change`(등락률) 둘뿐.**
   "이 종목이 몇 % 올랐다"는 사실만 있고, "사라/좋다/유망" 같은 판단은 없다.
3. 뉴스는 **헤드라인 + 원문 링크 + 매체명만.** 기사 본문은 복제하지 않는다.
4. 모든 페이지 하단에 **고지문(DISCLAIMER)** 이 들어간다.
   ("공개 시세를 가공한 시장 현황 요약이며, 매매를 권유하지 않습니다.")

> 코드 곳곳에 "법적 안전" 주석이 달려 있는 이유가 이것이다. 기능을 추가할 때
> **사실 정보를 넘어 '해석/판단'으로 가는 순간 선을 넘는다**고 보면 된다.

---

## 3. 시스템 전체 흐름

데이터는 **수집 → 집계 → 가공/배포**의 3단계를 거친다.

```
[수집]  collect/fetch_prices.py    전 종목 등락률(네이버 시세)   → data/all_stocks.json
        collect/fetch_market.py    글로벌 지표(야후 차트 API)    → data/market_indicators.json
        collect/fetch_theme_news.py 테마 뉴스(네이버 검색 API)   → data/theme_news.json
            ▲ 뉴스는 집계 결과(강한 테마)를 입력으로 받으므로 build_sectors 뒤에 실행

[집계]  collect/build_sectors.py   테마별 평균·강세도 계산       → data/sector_latest.json
            (data/meta/theme_map.json 매핑 필요)

[가공]  build_site.py (←content.py) 위 데이터로 정적 사이트 생성  → site/ (HTML·CSS·robots·sitemap)
        collect/push_kv.py         라이브 데이터 업로드          → Cloudflare KV "latest"

[묶음]  update.py                  위 전체를 한 사이클로 실행
            (가격·빌드 실패 시 중단 / 뉴스·지표·KV는 실패해도 진행 = best-effort)

[서빙]  worker/index.js            /api/data → KV "latest"
                                   그 외 경로 → site/ 정적 파일
```

핵심은 **두 가지 경로로 같은 데이터를 내보낸다**는 점이다.

- **정적 경로**: 빌드 시점의 데이터가 박힌 HTML(`site/`). 검색엔진·첫 화면용.
- **라이브 경로**: 최신 데이터를 KV에 올려두고, 브라우저가 `/api/data`로 받아 화면을
  다시 그림(트리맵·티커). 장중 갱신이 새 배포 없이 반영됨.

---

## 4. 단계별 원리 상세

### 4-1. 전 종목 등락률 수집 — `collect/fetch_prices.py`

- 코스피(`sosok=0`)·코스닥(`sosok=1`) **시가총액 페이지를 1페이지씩 순회**하며
  종목코드·종목명·등락률을 긁는다. 새 종목이 안 나오는 페이지가 나오면 끝으로 보고 멈춘다.
- ETF/ETN/리버리지·인버스/리츠/우선주 등은 **이름 패턴(`EXCLUDE` 정규식)으로 제외** —
  테마 히트맵에 노이즈가 되는 상품성 종목을 걸러낸다.
- 코스피/코스닥 **지수 등락률**은 네이버 실시간 지수 폴링 API에서 따로 받는다.
- NXT(대체거래소) 시세도 같은 방식으로 추가로 긁어 `return_1d_nxt`로 병합한다.
- 산출물 `data/all_stocks.json`:
  ```json
  {
    "collected_at": "...", "date": "YYYY-MM-DD",
    "market": { "kospi_change": ..., "kosdaq_change": ...,
                "advance_pct_kospi": ..., "advance_pct_kosdaq": ... },
    "stocks": { "005930": { "name": "삼성전자", "return_1d": 1.23 }, ... }
  }
  ```
  → 종목당 **이름과 등락률만** 저장(법적 안전선과 일치).

### 4-2. 테마 집계 — `collect/build_sectors.py`

전 종목 등락률을 **테마 매핑(`data/meta/theme_map.json`)** 으로 묶어 테마별 지표를 만든다.

- **강세 기준**: 종목 등락률 `≥ 5%` 이면 "강한 강세"로 카운트.
- **`weighted_strong`(가중 강세합)**: 강세 종목의 `1/(소속 테마 수)`를 더한 값.
  → 한 종목이 여러 테마에 걸쳐 있으면 가중치가 낮아져, **그 테마 전용 종목이 오를 때**
  점수가 더 크게 잡힌다. (제너럴리스트 종목이 테마를 부풀리는 걸 억제)
- **`tier`(테마 강도 구분, 추천 아님)**:
  - 평균 `≥6%` 그리고 가중강세합 `≥2.0` → `2`
  - 평균 `≥4%` 그리고 가중강세합 `≥1.0` → `1`
  - 그 외 → `0`
- 강세 종목이 1개 이상인 테마만 남기고, 가중강세합 내림차순으로 정렬한다.
- 각 테마에 **구성 종목 목록(`stocks[]` = 이름 + 등락률, 등락률 상위 20개)** 을 붙인다.
- 일반장(`sectors`)과 NXT장(`sectors_nxt`)을 둘 다 계산한다.
- 산출물 `data/sector_latest.json`: 위 모든 테마 지표 + 시장 라벨 + 고지문.

> `tier`는 "이 테마에 강세 종목이 얼마나 몰렸나"라는 **사실의 강도 표시**이지,
> 매수 등급이 아니다. 화면에서도 색/굵기 정도로만 쓴다.

### 4-3. 테마 뉴스 — `collect/fetch_theme_news.py`

강한 테마(`tier ≥ 1`)에 대해 **"왜 올랐나"의 단서가 될 헤드라인만** 모은다.

- 네이버 검색 API로 테마명·대표 종목명을 검색.
- **노이즈를 강하게 거른다**:
  - 규제경고/관리종목/칼럼/날씨/부고/e스포츠 등 **하드 차단 키워드·도메인**
  - "최근 N거래일", "N% 상승 마감" 같은 **자동 주가 리캡 봇 패턴** 정규식 차단
  - **원인(촉매) 키워드**(수주/계약/실적/승인/특허…)는 가점,
    **증상 키워드**(급등/신고가/상한가…)는 감점
  - 제목에 테마 키워드나 종목명이 없으면 탈락(관련성 게이트)
  - 여러 테마에 도배되는 헤드라인은 일반뉴스로 보고 전역 제거
- **AI 합성 없음.** 실제 헤드라인·원문 링크·매체명만 저장한다(저작권 안전선).
- 환경변수 `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` 필요.

### 4-4. 글로벌 지표 — `collect/fetch_market.py`

- 야후 파이낸스 차트 API로 나스닥/S&P 선물·환율·유가·미 10년물·비트코인 등의
  **값과 등락률**만 받는다. 해석·전망 없음.
- 지표 추가/삭제는 파일 안 `SYMBOLS` 리스트만 손보면 된다.

### 4-5. 사이트 빌드 — `build_site.py` (← `content.py`)

- 위 JSON들을 읽어 **정적 HTML 6쪽 이상 + CSS + robots + sitemap**을 `site/`에 만든다.
- 브랜드/공통 헤더·푸터·고지·정적 페이지 카피는 전부 **`content.py` 상단**에 모여 있다
  (`SITE_NAME`, `BASE_URL`, `CONTACT_EMAIL`, `DISCLAIMER_SHORT` 등).
- 카피를 고친 뒤에는 **반드시 `python build_site.py`를 다시 실행**해야 반영된다.
- ⚠️ `site/` 안의 파일을 손으로 고치지 말 것 — 빌드가 매번 통째로 덮어쓴다.
  고치려면 `content.py` / `build_site.py`를 고친다.

### 4-6. 라이브 데이터 업로드 — `collect/push_kv.py`

- `sector_latest.json` + `market_indicators.json` + `theme_news.json`을 하나로 합쳐
  Cloudflare KV의 `"latest"` 키에 올린다.
- 화면에 실제로 쓰이는 상위 테마만 `stocks`/`news`를 남기고 나머지는 떼어내 **페이로드를
  경량화**한다(무손실).
- KV 시크릿(계정/토큰)은 레포에 넣지 않고 홈 폴더의 `~/.ollashu_kv.json`에서 읽는다.

### 4-7. 서빙 — `worker/index.js`

- `/api/data` 요청 → KV `"latest"` 값을 그대로 반환(`no-store`, 최신 데이터).
- 그 외 경로 → `site/`의 정적 파일을 서빙.
- 브라우저는 첫 화면을 정적 HTML로 받고, 그 뒤 `/api/data`로 최신값을 받아
  트리맵·티커를 다시 그린다 → **재배포 없이 장중 갱신이 반영**된다.

---

## 5. 데이터 출처와 법적 이슈

> 이 절이 이 문서를 따로 남기는 핵심 이유다.

**현재 시세 데이터는 네이버 금융(시가총액 페이지 스크래핑 + 실시간 지수 폴링 API)에서
가져온다.** 빠르고 전 종목을 한 번에 받을 수 있어 채택했지만,

- 네이버 금융의 **HTML 페이지를 스크래핑**하는 방식은 해당 서비스의 이용약관/robots
  관점에서 **떳떳한 방식이 아니다.** (공식 허가된 데이터 공급 경로가 아님)
- 그래서 현재는 **비영리 정보 제공** 형태로만 운영하고 있다.

**향후 전환 방향(예정):**

- 합법적·안정적인 데이터 출처로 교체해야 한다. 후보:
  - **KRX 공식 데이터** (정보데이터시스템/오픈API 등 정식 경로)
  - **유료/공식 시세 벤더 API**
  - 라이선스가 명확한 데이터 제공처
- 다행히 **수집 계층이 분리되어 있어 교체 비용이 작다.** 출력 스키마
  (`data/all_stocks.json`의 `stocks.{code} = {name, return_1d}` 형태)만 동일하게
  맞춰 주면, 그 뒤 단계(집계·빌드·배포)는 **그대로 재사용**할 수 있다.
  → 실질적으로 `collect/fetch_prices.py` 한 파일(필요 시 뉴스/지표 수집기)만
  새 출처에 맞게 다시 쓰면 된다.

> 즉 "힘들게 만들어 둔" 집계·히트맵·사이트·배포 파이프라인은 손대지 않고,
> **데이터 입력구만 합법 경로로 갈아끼우는** 것이 전환 계획이다.

---

## 6. 빌드 / 배포 / 운영

- **사이트만 다시 빌드**: `python build_site.py` (산출물 = `site/`)
- **전체 갱신 1회**: `python update.py` (수집 → 집계 → 빌드 → KV)
- 실행에는 `pykrx`/`FinanceDataReader`/`pandas` 등이 깔린 venv가 필요.
  (수집기 자체는 `requests`/`beautifulsoup4` 중심)
- **배포 = git push.** `site/`까지 포함해 레포를 push하면 Cloudflare가
  `wrangler.jsonc` 기준(name `ollashu` · assets `./site` · KV binding `DATA`)으로
  **자동 재배포**한다. 별도 CI 없음.
- **정기 갱신**은 오라클 클라우드 서버의 cron이 `update.py`를 장중 주기적으로 실행한다.
  (cron/서버 설정은 오라클 쪽에 있고 이 레포엔 없다. 로컬 PC의 Task Scheduler는
  더 이상 주 운영 경로가 아니며, `update.log`는 옛 로컬 실행 기록이다.)

---

## 7. 디렉터리 구조

```
krx_heatmap/
├─ collect/                  데이터 수집·집계·업로드 스크립트
│  ├─ fetch_prices.py        전 종목 등락률 (네이버 시세)        ← 향후 교체 대상
│  ├─ build_sectors.py       테마 집계 (평균/강세도/tier)
│  ├─ fetch_theme_news.py    테마 뉴스 (네이버 검색 API)
│  ├─ fetch_market.py        글로벌 지표 (야후 차트 API)
│  └─ push_kv.py             라이브 데이터 → Cloudflare KV
├─ data/                     수집·집계 산출물(JSON)
│  ├─ all_stocks.json        전 종목 등락률
│  ├─ sector_latest.json     테마별 집계 결과
│  ├─ theme_news.json        테마 뉴스
│  ├─ market_indicators.json 글로벌 지표
│  └─ meta/                  테마 매핑(theme_map.json 등) — 직접 편집 금지
├─ content.py                브랜드·공통 레이아웃·정적 페이지 카피
├─ build_site.py             정적 사이트 생성기 (→ site/)
├─ site/                     빌드 결과물(정적 사이트) — 손으로 고치지 말 것
├─ worker/index.js           Cloudflare Worker (/api/data + 정적 서빙)
├─ wrangler.jsonc            Cloudflare 배포 설정
└─ update.py                 전체 갱신 한 사이클
```

---

## 8. 건드리지 말 것

- `data/meta/theme_map.json` · `theme_blocklist.json` — 외부(stock_agent)에서 복사해
  오는 매핑. 여기서 직접 편집 금지.
- `~/.ollashu_kv.json` — Cloudflare KV 시크릿(계정/토큰). 코드·커밋에 노출 금지.
- `site/` 안 파일 — `build_site.py`가 매번 덮어쓴다. 고치려면 `content.py` /
  `build_site.py`를 고친다.

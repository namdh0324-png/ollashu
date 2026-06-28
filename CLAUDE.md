# 올랐슈 (krx_heatmap)

한국 증시 **테마(섹터) 히트맵** 사이트. "오늘 장에서 뭐가 올랐나"를 공개 시세로
한눈에 보여준다. 종목 추천 없이 **시장 현황만** 정보로 제공한다.
(브랜드 톤: 충청도 사투리 "~유/~슈" — 카피 작성 시 유지)

- 도메인: https://ollashu.com
- 저장소: github.com/namdh0324-png/ollashu (프로젝트 전체 + 빌드 결과물 `site/` 까지 커밋)
- 호스팅: Cloudflare (Worker + 정적 assets + KV)

## 작업 규칙
- 모든 답변·커밋 메시지는 한국어로.
- 지시하지 않은 수정은 하지 않는다. 범위 밖이 보이면 고치지 말고 보고만 한다.
- 진단·보고는 솔직하게. 안 되면 안 됐다고 그대로 말한다.
- 기존 파일 상단의 **한글 주석 블록 스타일을 유지**한다 (이 프로젝트는 주석으로
  의도를 남기는 컨벤션이다 — 주석을 지우지 말 것).

## ⚠️ 절대 규칙 — 법적 안전선 (최우선)
유사투자자문·저작권 리스크 회피가 이 사이트의 제1원칙이다.
- **종목 추천·매수신호·목표가·점수·등급·AI판정 일절 금지.**
  어떤 페이지·데이터·문구에도 넣지 않는다.
- `sector_*.json`의 `stocks[]` 필드는 **`name`, `change`(등락률) 둘뿐.**
- 뉴스는 **헤드라인 + 원문링크 + 매체명만.** 본문 복제 금지.
- 모든 페이지 하단에 **고지문(DISCLAIMER)** 이 들어가야 한다.

## 아키텍처 (데이터 흐름)
```
collect/fetch_prices.py     전 종목 등락률(pykrx EOD)  → data/all_stocks.json
collect/build_sectors.py    테마 집계                  → data/sector_latest.json
                            (data/meta/theme_map.json 필요)
collect/fetch_theme_news.py 테마 뉴스(헤드라인+링크)   → data/theme_news.json
collect/fetch_market.py     글로벌 지표                → data/market_indicators.json
build_site.py (←content.py) 위 데이터로 사이트 생성    → site/ (HTML 6+페이지·css·robots·sitemap)
collect/push_kv.py          라이브 데이터 업로드       → Cloudflare KV "latest"
update.py                   위 전체를 한 사이클로 묶음 (가격·빌드 실패 시 중단,
                            뉴스·지표·KV는 best-effort)
worker/index.js             /api/data → KV "latest", 그 외 → site/ 정적 서빙
```

## 빌드 / 배포 / 운영
- 사이트만 다시 빌드: `python build_site.py` (산출물 = `site/`)
- 전체 갱신 1회: `python update.py` (수집→집계→빌드→KV)
- 실행에 stock_agent venv 필요 (pykrx·FinanceDataReader·pandas).
- **배포 = git push.** 저장소(`site/` 포함)를 push하면 Cloudflare가 wrangler.jsonc
  기준(name "ollashu" · assets `./site` · KV binding DATA)으로 자동 재배포한다. 별도 CI 없음.
- **정기 갱신은 오라클 클라우드 서버의 cron**이 `update.py`를 장중 주기적으로 실행한다.
  (그 cron/서버 설정은 오라클 쪽에 있고 이 저장소엔 없다. 로컬 PC의 Task Scheduler는
  더 이상 주 운영 경로가 아니다 — `update.log`는 옛 로컬 실행 기록.)

## 핵심 설정 — `content.py` 상단
`SITE_NAME` / `BASE_URL` / `CONTACT_EMAIL` + 공통 헤더·푸터·고지·정적페이지 카피가
전부 여기 있다. 카피 수정 후엔 반드시 `python build_site.py` 재실행.

## 건드리지 말 것
- `data/meta/theme_map.json`·`theme_blocklist.json` — stock_agent에서 복사해 오는
  매핑. 여기서 직접 편집 금지.
- `~/.ollashu_kv.json` — Cloudflare KV 시크릿(계정/토큰). 코드·커밋에 노출 금지.
- `site/` 안 파일을 손으로 고치지 말 것 — build_site.py가 매번 덮어쓴다.
  고치려면 content.py / build_site.py 를 고친다.

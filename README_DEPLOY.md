# 섹터레이더 배포 가이드

`build_site.py` 가 `data/sector_latest.json` 을 읽어 `site/` 폴더 전체를 생성한다.
**배포 대상은 `site/` 폴더 하나뿐.** 나머지(build_site.py, content.py, data/)는 빌드 재료라 올릴 필요 없다.

---

## 0. 로컬 미리보기 (지금 바로)

`site/index.html` 더블클릭 → 브라우저에서 바로 열린다.
데이터를 HTML 안에 박아넣어서 서버 없이도(file://) 그대로 보인다.

다시 빌드할 때:
```
cd 프로젝트폴더
python build_site.py
```

---

## 1. 배포 전 교체할 값 (content.py 상단)

| 변수 | 현재 | 바꿀 것 |
|---|---|---|
| `SITE_NAME` | 섹터레이더 | 최종 사이트명 (도메인과 맞추면 좋음) |
| `BASE_URL` | https://sectorradar.pages.dev | 실제 배포 도메인 |
| `CONTACT_EMAIL` | contact@example.com | 실제 문의 메일 (애드센스 필수) |

바꾼 뒤 `python build_site.py` 다시 돌리면 전 페이지에 반영된다.

---

## 2. Cloudflare Pages 배포 (추천 · 무료)

가장 쉬운 길은 GitHub 저장소 연결이다.

1. GitHub에 새 저장소 생성 → `site/` 폴더 안의 파일들을 저장소 **루트**에 올린다.
   (즉 `index.html` 이 저장소 최상단에 오게. site 폴더째로 올리면 경로가 `/site/index.html`이 되니 주의.)
2. Cloudflare 대시보드 → Workers & Pages → Create → Pages → Connect to Git → 저장소 선택.
3. 빌드 설정: **Framework preset = None**, Build command 비움, Output directory = `/` (루트).
4. Deploy. `이름.pages.dev` 주소가 나온다. 이게 `BASE_URL`.

> 대안: 빌드 없이 `site/` 폴더를 Cloudflare Pages "Direct Upload"로 드래그해도 된다. 더 단순하지만 매번 수동.

### GitHub Pages 대안
저장소 Settings → Pages → Source = main 브랜치 루트. `username.github.io/저장소명` 으로 뜬다.

---

## 3. 매일 자동 갱신 (menu[2] 연동)

평일 저녁 menu[2] 루틴이 새 `sector_YYYY-MM-DD.json` 을 만든 직후, 아래 흐름을 한 번 돌리면 사이트가 자동 갱신된다.

```
copy /Y "stock_agent의_최신_sector_json_경로" "프로젝트폴더\data\sector_latest.json"
cd /d 프로젝트폴더
python build_site.py
xcopy /Y /E site\* 깃저장소폴더\
cd /d 깃저장소폴더
git add -A
git commit -m "update %date%"
git push
```

Cloudflare Pages는 push 감지하면 자동 재배포한다. (수동 운영이면 push 두 줄 빼고, 가끔 Direct Upload만 해도 됨.)

> menu.bat에 이 흐름을 [5] 항목으로 붙이는 건 다음 작업으로 같이 하면 된다. (지금 menu.bat은 안 건드림.)

---

## 4. 애드센스 통과 체크리스트

이 사이트는 통과의 핵심 요소를 이미 갖췄다:

- [x] 실질 기능 (매일 갱신되는 인터랙티브 히트맵 + 정렬 가능한 표)
- [x] 충분한 정보 페이지 (소개 / 보는 법 / FAQ)
- [x] 정책 페이지 (개인정보처리방침 / 이용약관 / 투자정보 고지)
- [x] 전 페이지 공통 헤더·푸터·고지문
- [x] 모바일 대응 + sitemap.xml + robots.txt
- [ ] **실제 도메인 + 실제 연락처 메일** (위 1번)
- [ ] 며칠치 갱신 이력 (심사 전 평일 데이터 며칠 쌓기 권장)
- [ ] Google Search Console 등록 + sitemap 제출
- [ ] AdSense 신청 후 발급되는 `ads.txt` 를 site 루트에 추가

신청 순서: 도메인 확정 → 며칠 운영 → Search Console 등록 → AdSense 신청.

---

## 5. 다음 단계 — 펼침 패널 데이터 채우기

타일 클릭 시 펼쳐지는 패널의 **구성 종목 / 관련 뉴스** 칸은 UI가 이미 완성돼 있다.
`sector_*.json` 의 각 테마에 아래 두 필드를 추가하면 자동으로 채워진다(없으면 "준비 중" 표시).

```
{
  "theme": "로봇",
  "avg_return": 6.7,
  "strong_count": 13,
  "weighted_strong": 5.28,
  "data_count": 30,
  "total_count": 70,
  "tier": 2,
  "stocks": [
    {"name": "종목명", "change": 12.3}
  ],
  "news": [
    {"title": "헤드라인", "url": "원문링크", "source": "매체"}
  ]
}
```

### ⚠️ export 안전 규칙 (반드시)
`stocks` 에 넣어도 되는 필드는 **`name`, `change`(등락률) 뿐**이다.
점수·등급·AI판정·추천여부·목표가·매수신호는 **절대 넣지 말 것** (유사투자자문 리스크).
export 스크립트에서 화이트리스트 방식으로 두 필드만 뽑아 내보내는 것을 권장한다.
`news` 는 **헤드라인 + 원문링크 + 매체명만** (본문 복제 금지, 저작권).

> 이 필드들은 stock_agent의 sector export 스크립트를 고쳐야 생긴다.
> 그 스크립트를 다음 단계에서 안전 필터까지 함께 패치하면 된다.

## 6. 그 밖의 후보
- **날짜 아카이브:** 지난 날짜 히트맵을 `/archive/2026-06-13.html` 로 남겨 재방문·SEO 강화.
- **이름/도메인 확정** 후 브랜드 톤 1차 점검.

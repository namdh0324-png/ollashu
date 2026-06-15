# content.py
# 사이트 브랜드/공통 레이아웃/정적 페이지 카피. build_site.py가 import.
# 모든 페이지는 여기서 헤더/푸터/메타를 공유한다. 카피만 고치면 전 페이지 반영.

SITE_NAME = "올랐슈"
SITE_TAGLINE = "오늘 장에서 뭐가 올랐나, 급할 거 없이 보고 가유"
SITE_DESC = "공개 시세로 오늘 어떤 테마가 셌는지 한눈에 보여주는 사이트유. 종목 추천 없이 시장 현황만 정보로 알려드려유."
BASE_URL = "https://ollashu.com"  # 배포된 실제 도메인
CONTACT_EMAIL = "namdh0324@gmail.com"        # 애드센스/문의용 메일로 교체

NAV = [
    ("index.html", "오늘장"),
    ("guide.html", "보는 법"),
    ("about.html", "인사"),
    ("faq.html", "궁금한 거"),
    ("disclaimer.html", "투자 고지"),
]

# 모든 페이지 하단 고정 고지(법적 안전선). 절대 투자권유 문구 금지.
DISCLAIMER_SHORT = ("본 사이트는 공개 시세 정보를 가공한 <b>시장 현황 요약</b>이며, "
                    "특정 종목의 매매를 권유하지 않습니다. 투자 판단과 책임은 이용자 본인에게 있습니다.")


def css() -> str:
    return r"""
:root{
  --bg:#0d1014; --surface:#161b22; --surface2:#1c2430; --line:#222b36;
  --text-hi:#e8edf2; --text-mid:#aab6c4; --text-lo:#7c8896;
  --up:#ff5257; --up-soft:#3a1c1f; --down:#3b82f6; --down-soft:#16233c;
  --gold:#e0b341; --gold-soft:#2c2410;
  --tile-text:#ffffff; --tile-shadow:0 1px 3px rgba(0,0,0,.55);
  --badge1-bg:rgba(255,255,255,.16); --badge1-fg:#ffffff;
  --head-bg:rgba(13,16,20,.82);
  --mono:"Pretendard Variable",Pretendard,-apple-system,"Apple SD Gothic Neo",sans-serif;
  --display:"Jua","Pretendard Variable",sans-serif;
  --sans:"Pretendard Variable",Pretendard,-apple-system,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;
  --maxw:1120px;
}
:root[data-theme="light"]{
  --bg:#f5f7fa; --surface:#ffffff; --surface2:#eef1f6; --line:#dfe4ec;
  --text-hi:#1a2129; --text-mid:#465162; --text-lo:#606b7a;
  --up:#e5484d; --up-soft:#fbe3e4; --down:#2563eb; --down-soft:#e2eafc;
  --gold:#e8ab1e; --gold-soft:#f9e7b4;
  --tile-text:#ffffff; --tile-shadow:0 1px 3px rgba(0,0,0,.55);
  --badge1-bg:rgba(0,0,0,.10); --badge1-fg:#1a2129;
  --head-bg:rgba(255,255,255,.85);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--bg); color:var(--text-hi);
  font-family:var(--sans); line-height:1.6; letter-spacing:-.01em;
  font-feature-settings:"tnum" 1; word-break:keep-all;
}
a{color:inherit; text-decoration:none}
.wrap{max-width:var(--maxw); margin:0 auto; padding:0 20px}

/* header */
.site-head{position:sticky; top:0; z-index:20; background:var(--head-bg);
  backdrop-filter:blur(10px); border-bottom:1px solid var(--line)}
.site-head .wrap{display:flex; align-items:center; gap:18px; height:60px}
.brand{display:flex; align-items:baseline; gap:9px; font-weight:400; font-size:20px; font-family:var(--display); letter-spacing:0}
.brand .dot{width:9px; height:9px; border-radius:50%;
  background:radial-gradient(circle at 30% 30%,#ff7a7d,var(--up)); box-shadow:0 0 12px #ff525799}
.brand small{font-weight:500; color:var(--text-lo); font-size:12px; letter-spacing:.04em; font-family:var(--sans)}
.nav{margin-left:auto; display:flex; gap:4px; flex-wrap:wrap}
.nav a{padding:7px 11px; border-radius:8px; font-size:14px; color:var(--text-mid)}
.nav a:hover{background:var(--surface); color:var(--text-hi)}
.nav a.active{color:var(--text-hi); background:var(--surface2)}
.theme-toggle{margin-left:6px; width:34px; height:34px; border-radius:9px; cursor:pointer;
  border:1px solid var(--line); background:var(--surface); color:var(--text-mid);
  font-size:15px; line-height:1; display:inline-flex; align-items:center; justify-content:center}
.theme-toggle:hover{color:var(--text-hi); border-color:var(--gold)}

/* hero */
.hero{padding:34px 0 18px}
.hero .date{font-family:var(--mono); font-size:14px; color:var(--text-lo); letter-spacing:.02em}
.hero h1{margin:6px 0 14px; font-size:clamp(28px,4.8vw,44px); line-height:1.15; font-weight:400; font-family:var(--display); letter-spacing:0; color:var(--text-hi)}
.market-row{display:flex; align-items:center; gap:10px; flex-wrap:wrap}
.chip{display:inline-flex; align-items:center; gap:7px; padding:6px 12px; border-radius:999px;
  font-size:13px; font-weight:700; border:1px solid var(--line); background:var(--surface)}
.chip .k{color:var(--text-lo); font-weight:600}
.chip .v{font-family:var(--mono)}
.chip.mood{font-weight:700}
.chip.mood-bull{color:#e5484d; border-color:#e5484d; background:rgba(229,72,77,.14)}
.chip.mood-strong{color:#ef7a6f; border-color:#ef7a6f; background:rgba(239,122,111,.14)}
.chip.mood-normal{color:var(--text-mid); border-color:var(--line); background:var(--surface2)}
.chip.mood-weak{color:#2f6fe0; border-color:#2f6fe0; background:rgba(47,111,224,.14)}
.chip.mood-extreme{color:#d39a12; border-color:#d39a12; background:rgba(211,154,18,.14)}
.chip.mood-narrow{color:#9b6dd6; border-color:#9b6dd6; background:rgba(155,109,214,.14)}
.up-num{color:var(--up)} .down-num{color:var(--down)} .flat-num{color:var(--text-mid)}
.summary{margin:14px 0 0; color:var(--text-mid); font-size:15px; max-width:62ch}

/* 제목 + 시세 기준 시각(우상단 박스) */
.hero-top{display:flex; justify-content:space-between; align-items:center; gap:18px; flex-wrap:wrap; margin:4px 0 14px}
.hero-top h1{margin:0}
.hero-time{display:flex; flex-direction:column; align-items:flex-end; gap:2px; flex:0 0 auto;
  padding:9px 18px; border:1px solid var(--line); border-radius:14px; background:var(--surface2)}
.ht-k{font-size:11.5px; color:var(--text-lo); letter-spacing:.02em}
.ht-v{font-family:var(--mono); font-weight:800; font-size:clamp(34px,5.2vw,50px); color:var(--text-hi); line-height:1.02}

/* market ticker (글로벌 지표) — 지표만 폭 꽉 채우는 한 줄 바 */
.ticker{display:flex; align-items:stretch; margin:18px 0 0;
  border:1px solid var(--line); border-radius:14px; background:var(--surface); overflow:hidden}
.tk{flex:1 1 0; display:flex; flex-direction:column; justify-content:center; gap:4px;
  padding:13px 18px; min-width:0; border-left:1px solid var(--line)}
.tk:first-child{border-left:0}
.tk-k{font-size:13px; color:var(--text-lo); white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
.tk-v{font-family:var(--mono); font-size:18.5px; font-weight:700; color:var(--text-hi); white-space:nowrap}
.tk-c{font-family:var(--mono); font-size:13.5px; font-weight:600; white-space:nowrap}
@media(max-width:760px){
  .ticker{flex-wrap:wrap}
  .tk{flex:1 1 33%; border-top:1px solid var(--line)}
  .tk:nth-child(-n+3){border-top:0}
  .tk:nth-child(3n+1){border-left:0}
}

/* legend */
.legend{display:flex; gap:18px; flex-wrap:wrap; align-items:center; margin:22px 0 14px;
  padding:13px 16px; border:1px solid var(--line); border-radius:12px; background:var(--surface);
  font-size:13px; color:var(--text-mid)}
.legend .grad{height:10px; width:140px; border-radius:6px;
  background:linear-gradient(90deg,var(--surface2),var(--up))}
.legend b{color:var(--text-hi); font-weight:700}
.legend .tier-mark{width:13px; height:13px; border-radius:4px; border:2px solid var(--gold); display:inline-block; vertical-align:-2px}

/* heatmap treemap */
.grid{position:relative; width:100%; margin:0 0 8px}
.grid-hint{color:var(--text-lo); font-size:13px; margin:0 0 30px}
.tile{position:relative; border:1px solid var(--line); border-radius:13px; padding:14px 14px 12px;
  background:var(--surface2); overflow:hidden; min-height:116px; cursor:pointer;
  display:flex; flex-direction:column; justify-content:space-between;
  transition:transform .12s ease, border-color .12s ease}
.tile:hover{transform:translateY(-2px); border-color:var(--gold)}
.tile.t2{border-color:var(--gold); box-shadow:inset 0 0 0 1px var(--gold-soft)}
:root[data-theme="light"] .tile{background:#c8cfd8}
:root[data-theme="light"] .tile.t2{box-shadow:inset 0 0 0 1.5px var(--gold)}
.tile.open{outline:2px solid var(--gold); outline-offset:-1px; transform:none}
.tile .heat{position:absolute; inset:0; z-index:0}
.tile .body{position:relative; z-index:1; display:flex; flex-direction:column; height:100%}
.tile .theme{font-weight:700; font-size:15px; line-height:1.25; color:var(--tile-text); text-shadow:var(--tile-shadow)}
.tile .ret{font-family:var(--mono); font-size:24px; font-weight:700; margin:6px 0 2px;
  color:var(--tile-text); text-shadow:var(--tile-shadow); white-space:nowrap}
.tile .meta{font-size:12px; color:var(--tile-text); opacity:.82; font-family:var(--mono);
  text-shadow:var(--tile-shadow)}
.tile .badge{position:absolute; top:10px; right:10px; z-index:2; font-size:10.5px; font-weight:800;
  padding:3px 7px; border-radius:6px; letter-spacing:.03em}
.badge.b2{background:var(--gold); color:#1a1405}
.badge.b1{background:var(--badge1-bg); color:var(--badge1-fg)}

/* expand detail panel */
.detail{grid-column:1/-1; background:var(--surface); border:1px solid var(--gold);
  border-radius:13px; padding:18px 20px 20px; position:relative; animation:dopen .18s ease}
@keyframes dopen{from{opacity:0; transform:translateY(-4px)} to{opacity:1; transform:none}}
.detail .d-close{position:absolute; top:12px; right:14px; background:transparent; border:0;
  color:var(--text-lo); font-size:22px; line-height:1; cursor:pointer; padding:2px 6px}
.detail .d-close:hover{color:var(--text-hi)}
.d-head{display:flex; align-items:baseline; gap:12px; margin-bottom:14px; padding-right:30px}
.d-theme{font-size:20px; font-weight:800; color:var(--text-hi)}
.d-ret{font-family:var(--mono); font-size:20px; font-weight:700}
.d-stats{display:flex; flex-wrap:wrap; gap:10px 22px; padding:13px 16px; margin-bottom:16px;
  background:var(--surface2); border:1px solid var(--line); border-radius:10px}
.d-stats span{display:flex; flex-direction:column; gap:2px; font-family:var(--mono); font-size:15px; color:var(--text-hi)}
.d-stats i{font-style:normal; font-size:11.5px; color:var(--text-lo); font-family:var(--sans)}
.d-sec{margin-top:14px}
.d-sec h4{margin:0 0 9px; font-size:13px; color:var(--text-lo); font-weight:600; letter-spacing:.02em}
.d-stocks{display:flex; flex-wrap:wrap; gap:8px}
.d-stock{display:inline-flex; align-items:center; gap:7px; padding:6px 11px; border-radius:8px;
  background:var(--surface2); border:1px solid var(--line); font-size:14px}
.d-stock span{font-family:var(--mono); font-size:13px}
.d-newslist{display:flex; flex-direction:column; gap:8px}
.d-news{display:flex; align-items:center; gap:9px; padding:10px 13px; border-radius:9px;
  background:var(--surface2); border:1px solid var(--line); font-size:14.5px; color:var(--text-hi)}
.d-news:hover{border-color:var(--gold)}
.d-src{margin-left:auto; font-size:12px; color:var(--text-lo); white-space:nowrap}
.d-empty{color:var(--text-lo); font-size:13.5px; padding:4px 2px}

/* full table */
.table-wrap{margin:8px 0 40px; border:1px solid var(--line); border-radius:13px; overflow:hidden; background:var(--surface)}
.table-head{display:flex; align-items:center; gap:10px; padding:14px 16px; border-bottom:1px solid var(--line); flex-wrap:wrap}
.table-head h2{margin:0; font-size:16px}
.table-head .count{color:var(--text-lo); font-size:13px; font-family:var(--mono)}
.sortbtns{margin-left:auto; display:flex; gap:6px}
.sortbtns button{font-family:var(--sans); font-size:12.5px; color:var(--text-mid); cursor:pointer;
  background:var(--surface2); border:1px solid var(--line); padding:6px 11px; border-radius:8px}
.sortbtns button.on{color:#1a1405; background:var(--gold); border-color:var(--gold); font-weight:700}
.exchbar{display:flex; align-items:center; gap:8px; margin:2px 0 12px; flex-wrap:wrap}
.exchbar button{font-family:var(--sans); font-size:14.5px; font-weight:700; color:var(--text-mid); cursor:pointer; background:var(--surface2); border:1px solid var(--line); padding:8px 20px; border-radius:9px}
.exchbar button.on{color:#1a1405; background:var(--gold); border-color:var(--gold)}
.exch-note{font-size:12.5px; color:var(--text-lo); font-family:var(--sans)}
table{width:100%; border-collapse:collapse; font-size:14px}
th,td{padding:10px 16px; text-align:right; border-bottom:1px solid var(--line); white-space:nowrap}
th:first-child,td:first-child{text-align:left}
th{position:sticky; top:0; background:var(--surface); color:var(--text-lo); font-weight:600; font-size:12.5px; cursor:pointer}
tbody tr:hover{background:var(--surface2)}
td.num{font-family:var(--mono)}
.t-tier{display:inline-block; min-width:30px; text-align:center; font-size:11px; font-weight:700; padding:2px 6px; border-radius:5px}
.t-tier.x2{background:var(--gold-soft); color:var(--gold); border:1px solid var(--gold)}
.t-tier.x1{background:var(--surface2); color:var(--text-mid)}
.t-tier.x0{color:var(--text-lo)}

/* content pages */
.page{padding:36px 0 20px; max-width:760px}
.page h1{font-size:30px; margin:0 0 6px; color:var(--text-hi)}
.page .lead{color:var(--text-mid); font-size:16px; margin:0 0 26px}
.page h2{font-size:20px; margin:34px 0 10px; padding-top:6px; color:var(--text-hi)}
.page h3{font-size:16px; margin:22px 0 6px; color:var(--text-hi)}
.page p,.page li{color:var(--text-mid); font-size:15.5px}
.page b,.page strong{color:var(--text-hi)}
.page ul,.page ol{padding-left:20px}
.page li{margin:5px 0}
.page .card{border:1px solid var(--line); background:var(--surface); border-radius:12px; padding:18px 20px; margin:16px 0}
.page .warn{border-color:var(--gold); background:var(--gold-soft)}
.page table{margin:14px 0; font-size:14.5px}
.page th,.page td{text-align:left}
.updated{font-family:var(--mono); font-size:12.5px; color:var(--text-lo)}

/* footer */
.site-foot{border-top:1px solid var(--line); margin-top:20px; padding:26px 0 50px; color:var(--text-lo); font-size:13px}
.site-foot .disc{background:var(--surface); border:1px solid var(--line); border-radius:11px; padding:14px 16px; margin-bottom:18px; color:var(--text-mid); line-height:1.55}
.site-foot .disc b{color:var(--text-hi)}
.site-foot .flinks{display:flex; gap:16px; flex-wrap:wrap; margin-bottom:10px}
.site-foot .flinks a:hover{color:var(--text-hi)}
.site-foot .copy{color:var(--text-lo)}

@media(max-width:880px){ .grid{grid-template-columns:repeat(3,1fr)} }
@media(max-width:560px){
  .site-head .wrap{height:60px; flex-wrap:nowrap; gap:10px}
  .brand{flex:0 0 auto}
  .brand small{display:none}
  .nav{flex-wrap:nowrap; overflow-x:auto; gap:4px}
  .nav::-webkit-scrollbar{display:none}
  .nav a{padding:6px 9px; font-size:13px; flex:0 0 auto}
  .theme-toggle{flex:0 0 auto; width:30px; height:30px}
  .hero{padding:22px 0 14px}
  .hero-time{align-items:flex-start; padding:9px 14px}
  .grid{grid-template-columns:repeat(2,1fr); gap:8px}
  .tile{min-height:104px; padding:12px; border-radius:4px} .tile .ret{font-size:21px}
  .tile .body{justify-content:center; gap:2px}
  .tile .theme{flex:0 1 auto !important}
  .d-stats{gap:8px 16px}
  .table-head .sortbtns{margin-left:0; width:100%}
  table{font-size:12.5px}
  th,td{padding:8px 9px; white-space:normal}
}
@media(prefers-reduced-motion:reduce){ .tile{transition:none} .detail{animation:none} }
"""


def head(title: str, desc: str, canonical: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{BASE_URL}/{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:locale" content="ko_KR">
<meta property="og:url" content="{BASE_URL}/{canonical}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:image" content="{BASE_URL}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{BASE_URL}/og.png">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" as="style" crossorigin
  href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jua&display=swap">
<link rel="stylesheet" href="style.css">
<script>(function(){{try{{var t=localStorage.getItem('theme');if(t==='light')document.documentElement.dataset.theme='light';}}catch(e){{}}}})();</script>
</head>
<body>
"""


def header(active: str) -> str:
    links = "".join(
        f'<a href="{href}"{" class=\"active\"" if href == active else ""}>{label}</a>'
        for href, label in NAV
    )
    return f"""<header class="site-head"><div class="wrap">
<a class="brand" href="index.html"><span class="dot"></span>{SITE_NAME}<small>오늘 뭐 올랐슈</small></a>
<nav class="nav">{links}<button class="theme-toggle" id="themeToggle" type="button" aria-label="라이트/다크 전환"></button></nav>
</div></header>
"""


def footer() -> str:
    flinks = "".join(f'<a href="{href}">{label}</a>'
                     for href, label in NAV + [("privacy.html", "개인정보처리방침"), ("terms.html", "이용약관")])
    return f"""<footer class="site-foot"><div class="wrap">
<div class="disc">{DISCLAIMER_SHORT}</div>
<div class="flinks">{flinks}</div>
<div class="copy">© 2026 {SITE_NAME}. 데이터 출처: KRX·NXT 공개 시세. 문의: {CONTACT_EMAIL}</div>
</div></footer>
<script>
(function(){{
  var btn=document.getElementById('themeToggle');
  function isLight(){{return document.documentElement.dataset.theme==='light';}}
  function icon(){{ if(btn) btn.textContent = isLight() ? '\\u263D' : '\\u2600\\uFE0E'; }}
  icon();
  if(btn) btn.addEventListener('click',function(){{
    var next = isLight() ? 'dark' : 'light';
    if(next==='light') document.documentElement.dataset.theme='light';
    else document.documentElement.removeAttribute('data-theme');
    try{{localStorage.setItem('theme',next);}}catch(e){{}}
    icon();
    if(window.repaintHeat) window.repaintHeat();
  }});
}})();
</script>
</body></html>"""


def wrap_page(title: str, desc: str, canonical: str, active: str, body_html: str) -> str:
    return head(title, desc, canonical) + header(active) + body_html + footer()


# ────────────────────────────────────────────────────────────────────
# 정적 페이지 본문 (애드센스 통과 핵심: 실질 콘텐츠 + 정책 페이지)
# ────────────────────────────────────────────────────────────────────

def page_about() -> str:
    return f"""<main class="wrap"><div class="page">
<h1>{SITE_NAME}가 뭐냐면유</h1>
<p class="lead">{SITE_TAGLINE}.</p>

<p>{SITE_NAME}는 한국거래소(KRX)에 상장된 종목들의 공개 시세를 테마·섹터 단위로
묶어서, 그날 어떤 산업 테마가 셌는지를 히트맵 한 장으로 보여드리는 정보 사이트유.
매 거래일 장 끝나고 알아서 갱신돼유.</p>

<h2>왜 만들었냐면유</h2>
<p>장 끝나면 늘 똑같은 질문이 남잖유 — "오늘은 뭐가 올랐댜?" 지수만 봐선
어떤 테마가 시장을 끌었는지 안 보이고, 개별 종목만 봐선 큰 흐름이 안 잡혀유.
그 사이의 '어떤 테마가 셌나'를 후딱 보고 싶어서 시작한 거유.</p>

<h2>딴 데랑 뭐가 다르냐면유</h2>
<div class="card">
<p><b>① 시장이 실제로 거래하는 테마 분류.</b> 단순 업종 코드가 아니라, 현재 시장에서
함께 묶여 움직이는 테마 단위(예: 로봇, HBM, 전력기기)로 집계합니다.</p>
<p><b>② 평균만이 아니라 '얼마나 같이 올랐나'까지.</b> 평균 등락률뿐 아니라 그 테마에서
+5%↑ 오른 <b>종목 수</b>랑 오른(+) 종목 <b>비율</b>을 같이 보여줘, 한두 종목이 끌어올린
건지 여럿이 같이 오른 건지 구분해유.</p>
<p><b>③ 누르면 펼쳐지는 상세.</b> 타일을 클릭하면 그 테마의 구성 종목과 '오른 이유'(관련 뉴스
헤드라인·원문 링크)까지 한 자리에서 확인할 수 있습니다.</p>
</div>

<h2>데이터는유</h2>
<p>모든 수치는 KRX·NXT 공개 시세로 계산한 <b>과거·당일 사실 데이터</b>유.
화면 위 <b>KRX·NXT 버튼</b>으로 거래소를 바꿔볼 수 있슈 — NXT(넥스트레이드)는 정규장 전후로도
거래되는 대체거래소라, 프리마켓(아침 8:00~8:50)·애프터마켓(오후 3:30~8:00)까지 봐유.
장 시작 전 아침 분위기나 장 끝난 뒤 흐름이 궁금할 때 눌러보면 돼유.
미래 예측, 목표가, 매수/매도 신호 같은 건 안 드리고, 앞으로도 안 할 거유.
{SITE_NAME}는 정보 제공 서비스이며 투자자문업·유사투자자문업에 해당하지 않습니다.
자세한 건 <a href="disclaimer.html">투자 고지</a> 보고 가유.</p>

<h2>어떻게 계산하냐면유</h2>
<p>매 거래일 장 마감 뒤, 공개 시세를 테마별로 묶어 이렇게 집계해유:</p>
<div class="card">
<p><b>평균 등락률</b> — 그 테마 종목들의 그날 등락률 평균이유. 타일 크기를 정해유.</p>
<p><b>+5%↑ 종목 수</b> — 그 테마에서 5% 넘게 오른 종목이 몇 개냐. 테마가 '얼마나 세게' 움직였나를 봐유.</p>
<p><b>오른 비율</b> — 그 테마 종목 중 오른(+) 종목이 몇 %냐. 한두 종목이 끌었나, 여럿이 같이 올랐나를 가려유.</p>
<p>이 셋을 합쳐 그날 테마 강도 순서를 매기고, <b>오른 테마 중 상위만</b> 히트맵 칸으로 보여드려유.</p>
</div>

<h2>한계도 있슈</h2>
<p>솔직히 말하면유 — 시세엔 지연이나 오류가 있을 수 있고, 테마 분류도 시장 상황에 맞춰
사람이 다듬는 부분이라 정답이 하나는 아니유. 그래서 {SITE_NAME}의 모든 수치는 <b>참고용</b>이고,
투자 판단의 근거로 삼으시면 안 돼유. 데이터 정확성은 보장하지 않아유.</p>

<h2>누가 만드냐면유</h2>
<p>한국 주식에 관심 많은 개인이 취미로 만들어 직접 운영하는 사이트유. 고칠 거나
궁금한 게 보이면 언제든 아래 메일로 연락 주셔유.</p>

<p class="updated">문의: {CONTACT_EMAIL}</p>
</div></main>
"""


def page_guide() -> str:
    return f"""<main class="wrap"><div class="page">
<h1>이거 어떻게 보냐면유</h1>
<p class="lead">색·숫자·테두리가 뭔 뜻인지, 1분이면 다 익혀유.</p>

<h2>맨 위 KRX·NXT 버튼</h2>
<p>화면 맨 위 <b>KRX</b>·<b>NXT</b> 버튼으로 어느 거래소 기준으로 볼지 골라유.
<b>KRX</b>는 한국거래소 정규장(09:00~15:30), <b>NXT</b>(넥스트레이드)는 정규장 전후로도 도는
대체거래소유 — 프리마켓(아침 8:00~8:50)·애프터마켓(오후 3:30~8:00)까지 거래돼유.
그래서 <b>장 시작 전 아침 분위기</b>나 <b>장 끝난 뒤 흐름</b>이 궁금하면 NXT를 눌러봐유.
버튼 옆에 지금 어느 시간대인지도 알려줘유.</p>

<h2>1. 색이랑 칸 크기</h2>
<p>색이 <b style="color:var(--up)">진한 빨강일수록 많이 올랐슈</b>. 1·2·3…% 정수 단위로
진하기가 달라져서 색만 봐도 대충 몇 %인지 가늠돼유. <b>칸 크기</b>는 평균 등락률이
클수록 커져유 — 큰 칸이 그날 많이 오른 테마유. 안 오른 테마는 안 나오고,
<b>오른 것 중 상위만</b> 칸으로 보여줘유.</p>

<h2>2. 큰 숫자 — 평균 등락률</h2>
<p>타일 가운데 큰 숫자는 그 테마 종목들의 <b>평균 등락률</b>이유.
"이 테마가 오늘 평균 몇 % 움직였댜"를 뜻해유.</p>

<h2>3. 5%↑ 종목이랑 오른 비율 (누르면 나와유)</h2>
<p>칸을 누르면 상세에 나오는 숫자유. <b>5%↑ N</b>은 그 테마에서 오늘 5% 넘게 오른
종목 수, <b>오른 비율</b>은 그 테마 종목 중 <b>오른(+) 종목이 몇 %</b>냐는 거유.
평균만 봐선 한두 종목이 끌어올린 건지 여럿이 같이 오른 건지 구분이 안 되거든유.</p>

<h2>예를 들면유</h2>
<div class="card">
<p>같은 평균 <b>+6%</b>라도 속은 완전 달라유:</p>
<p><b>A 테마</b> — 평균 +6%, 5%↑ <b>12개</b>, 오른 비율 <b>90%</b> → 한두 종목이 아니라
<b>테마 전체가 같이</b> 달군 거유.</p>
<p><b>B 테마</b> — 평균 +6%, 5%↑ <b>1개</b>, 오른 비율 <b>40%</b> → <b>한 종목</b>이 평균을 끌어올린 거유.</p>
<p>그래서 평균만 보지 말고 5%↑랑 오른 비율을 같이 보면, 그날 테마가 진짜 셌는지 가늠이 돼유.</p>
</div>

<h2>4. 금색 테두리 — 핵심 테마</h2>
<div class="card">
<p><span style="color:var(--gold)">금색 테두리(짱 쎄유)</span> — 오늘 제일 달군 핵심 테마유.</p>
<p>테두리 없음 — 그 외 오른 테마유.</p>
</div>

<h2>5. 누르면 더 나와유</h2>
<p>타일 누르면 그 밑에 패널이 열려유. 그 테마의 5%↑·본·전체 종목이랑 오른 비율,
그리고 <b>뭐뭐 들었는지</b>·<b>왜 올랐는지(관련 뉴스)</b>까지 보여줘유.
다시 누르거나 ×를 누르면 닫혀유.</p>

<h2>6. 싹 다 보는 표</h2>
<p>히트맵 아래 표에서 그날 집계된 테마를 전부 볼 수 있슈. 위 버튼으로
<b>비율순 · 등락순 · 5%↑순</b>으로 정렬 바꿔가며 보고 가유.</p>

<div class="card warn">
<p><b>읽을 때 한 가지.</b> 이 화면은 '오늘 뭐가 셌나'라는 지나간 사실 요약이유.
앞으로의 주가를 예측하거나 매매를 권하는 정보가 아닙니다.</p>
</div>
</div></main>
"""


def page_faq() -> str:
    return f"""<main class="wrap"><div class="page">
<h1>궁금한 거 모음</h1>
<p class="lead">{SITE_NAME} 쓰면서 많이들 묻는 거 모아놨슈.</p>

<h3>데이터는 얼마나 자주 갱신돼유?</h3>
<p>매 거래일(평일) 장 끝나고 그날 데이터로 알아서 갱신돼유. 주말·공휴일엔
직전 거래일 데이터가 그대로 남아유.</p>

<h3>여기 나온 테마 사면 돼유?</h3>
<p>아니유. {SITE_NAME}는 어떤 종목도 추천하지 않습니다. 화면의 모든 수치는 '오늘 이런
테마가 셌다'는 지나간 시장 현황 요약일 뿐이며, 매수·매도 판단의 근거로 쓰여서는 안 됩니다.</p>

<h3>'5%↑'랑 '오른 비율'이 뭐예유?</h3>
<p><b>5%↑</b>는 그 테마에서 오늘 5% 넘게 오른 종목이 몇 개냐는 거고, <b>오른 비율</b>은
그 테마 종목 중에 <b>오른(+) 종목이 몇 %</b>냐는 거유. 평균 등락률만 봐선
한두 종목이 끌어올린 테마랑 여럿이 고르게 오른 테마가 구분이 안 되거든유.
자세한 건 <a href="guide.html">보는 법</a>에 있슈.</p>

<h3>테마는 무슨 기준으로 묶어유?</h3>
<p>표준 산업 코드 말고, 지금 시장에서 같이 움직이는 테마 단위로 묶어유.
그래서 한 종목이 여러 테마에 동시에 들어갈 수도 있슈.</p>

<h3>특정 종목이 어느 테마인지 찾을 수 있슈?</h3>
<p>종목 이름으로 검색하는 기능은 아직 없슈. 다만 테마 타일을 누르면 그 테마에 <b>뭐뭐 들었는지</b>
구성 종목을 보여드려유. '이 종목이 어느 테마' 식의 역검색은 준비 중이유.</p>

<h3>KRX랑 NXT 버튼은 뭐예유?</h3>
<p>화면 위에서 거래소를 고르는 버튼이유. <b>KRX</b>는 한국거래소 정규장(09:00~15:30),
<b>NXT</b>(넥스트레이드)는 그 전후로도 거래되는 대체거래소라 프리마켓(아침 8:00~8:50)·
애프터마켓(오후 3:30~8:00)까지 봐유. 아침 장 전이나 장 끝난 뒤 분위기가 궁금하면 NXT를
눌러보면 돼유. 자세한 건 <a href="guide.html">보는 법</a>에 있슈.</p>

<h3>데이터 출처가 어디예유?</h3>
<p>전부 한국거래소(KRX)랑 넥스트레이드(NXT) 공개 시세유. 그 시세를 테마별로 묶어 평균 등락률·5%↑ 종목 수·오른
비율을 계산한 거고, 별도의 예측이나 가공된 점수는 안 써유.</p>

<h3>왜 자꾸 '~유', '~슈' 그래유?</h3>
<p>이름이 '{SITE_NAME}'잖유. 보다가 한 번 피식 웃고 가시라고 말투도 거기 맞췄슈. 다만 투자
고지·약관 같은 중요한 안내는 또박또박 진지하게 써놨으니 그건 꼭 읽고 가셔유.</p>

<h3>데이터가 틀린 거 같은데유.</h3>
<p>집계·표시 오류 보이면 <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>로
알려주셔유. 다만 시세 데이터 자체의 정확성은 보장되지 않으며 참고용입니다.</p>

<h3>폰에서도 보여유?</h3>
<p>네, 보여유. 화면 크기에 맞춰 히트맵이랑 표가 알아서 재배치돼유.</p>
</div></main>
"""


def page_disclaimer() -> str:
    return f"""<main class="wrap"><div class="page">
<h1>투자정보 고지</h1>
<p class="lead">반드시 읽어주세요. {SITE_NAME}의 성격과 한계를 명확히 합니다.</p>

<div class="card warn">
<p><b>{SITE_NAME}는 투자자문·유사투자자문 서비스가 아닙니다.</b> 본 사이트가 제공하는 모든
정보는 공개 시세 데이터를 가공한 <b>시장 현황 요약(정보 제공)</b>이며, 특정 종목·시점에 대한
매수·매도·보유 권유가 아닙니다.</p>
</div>

<h2>제공하는 것 / 제공하지 않는 것</h2>
<ul>
<li>제공: 테마·섹터 단위의 당일 평균 등락률, 5%↑ 종목 수, 오른 비율, 그날 센 정도 표시,
그리고 참고용 글로벌 지표(지수·선물·환율·유가 등) 같은 <b>지나간 사실 또는 참고 시세</b>.
모든 표시는 사실 요약일 뿐 평가·추천이 아닙니다.</li>
<li>제공하지 않음: 개별 종목 추천, 목표가, 매매 신호, 수익률 보장, 미래 가격 예측.</li>
</ul>

<h2>책임의 한계</h2>
<ul>
<li>모든 데이터는 참고용이며 정확성·완전성·적시성을 보장하지 않습니다. 수집·계산 과정에서
오류나 지연이 있을 수 있습니다.</li>
<li>본 사이트 정보를 근거로 한 어떠한 투자 판단과 그 결과에 대해서도 {SITE_NAME}는 책임지지 않습니다.
투자 결정과 책임은 전적으로 이용자 본인에게 있습니다.</li>
<li>투자는 원금 손실의 위험이 있습니다. 투자 전 충분히 검토하시고, 필요하면 자격을 갖춘
전문가와 상담하시기 바랍니다.</li>
</ul>

<h2>데이터 출처</h2>
<p>한국거래소(KRX)·넥스트레이드(NXT) 등 공개된 시세 정보를 기반으로 합니다. 원천 데이터의 권리는 각 제공처에 있습니다.</p>

<p class="updated">최종 개정: 2026-06-15</p>
</div></main>
"""


def page_privacy() -> str:
    return f"""<main class="wrap"><div class="page">
<h1>개인정보처리방침</h1>
<p class="lead">{SITE_NAME}는 이용자의 개인정보를 소중히 다룹니다.</p>

<h2>1. 수집하는 개인정보</h2>
<p>{SITE_NAME}는 회원가입·로그인 기능이 없으며, 이름·연락처 등 개인을 식별하는 정보를
직접 수집하지 않습니다. 다만 서비스 운영을 위해 아래 정보가 자동으로 처리될 수 있습니다.</p>
<ul>
<li>접속 로그, 브라우저·기기 정보, 쿠키 (방문 통계 및 광고 제공 목적)</li>
</ul>

<h2>2. 쿠키와 제3자 광고</h2>
<p>본 사이트는 Google AdSense 등 제3자 광고를 게재할 수 있습니다. 이 과정에서 Google을
포함한 제3자 공급업체는 쿠키를 사용해 이용자의 방문 기록을 바탕으로 광고를 제공할 수 있습니다.
Google의 광고 쿠키 사용에 관한 자세한 내용은
<a href="https://policies.google.com/technologies/ads" rel="noopener" target="_blank">Google 광고 기술 정책</a>에서
확인할 수 있습니다. 맞춤 광고를 해제하더라도 이용자의 과거 사이트 방문을 바탕으로 한
리마케팅 광고는 게재될 수 있습니다. 이용자는
<a href="https://www.google.com/settings/ads" rel="noopener" target="_blank">Google 광고 설정</a>에서
맞춤 광고를 해제할 수 있으며, 브라우저 설정에서 쿠키를 차단할 수 있습니다.</p>

<h2>3. 분석 도구</h2>
<p>방문 통계 분석을 위해 익명화된 접속 데이터를 처리하는 분석 도구를 사용할 수 있습니다.
이 데이터는 개인을 식별하지 않습니다.</p>

<h2>4. 개인정보의 보유 및 파기</h2>
<p>직접 수집하는 개인정보가 없으므로 별도의 보유·파기 대상이 없습니다. 자동 수집되는
로그성 정보는 관련 법령이 정한 기간에 따라 처리됩니다.</p>

<h2>5. 이용자의 권리</h2>
<p>이용자는 브라우저 쿠키 차단, 맞춤 광고 해제 등을 통해 자신의 정보 처리에 관여할 수 있습니다.</p>

<h2>6. 문의</h2>
<p>개인정보 처리에 관한 문의는 <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>로 보내주세요.</p>

<p class="updated">최종 개정: 2026-06-15</p>
</div></main>
"""


def page_terms() -> str:
    return f"""<main class="wrap"><div class="page">
<h1>이용약관</h1>
<p class="lead">{SITE_NAME} 이용에 적용되는 기본 약관입니다.</p>

<h2>제1조 (목적)</h2>
<p>본 약관은 {SITE_NAME}(이하 "사이트")가 제공하는 정보 서비스의 이용 조건과 책임 범위를 정합니다.</p>

<h2>제2조 (서비스의 성격)</h2>
<p>사이트는 공개 시세 데이터를 가공한 시장 현황 정보를 무료로 제공합니다. 사이트는 투자자문·
유사투자자문 서비스가 아니며, 제공 정보는 투자 권유가 아닙니다.</p>

<h2>제3조 (면책)</h2>
<ul>
<li>사이트는 제공 정보의 정확성·완전성·적시성을 보장하지 않습니다.</li>
<li>이용자가 사이트 정보를 이용해 내린 판단과 그 결과에 대해 사이트는 책임지지 않습니다.</li>
<li>사이트는 천재지변, 데이터 공급처의 사정, 기술적 문제 등으로 서비스가 중단·지연될 수 있으며
이에 대해 책임지지 않습니다.</li>
</ul>

<h2>제4조 (저작권)</h2>
<p>사이트가 생성한 화면·디자인·집계 결과물의 권리는 {SITE_NAME}에 있습니다. 원천 시세
데이터의 권리는 각 제공처에 귀속됩니다. 무단 복제·재배포를 금합니다.</p>

<h2>제5조 (약관의 변경)</h2>
<p>사이트는 필요 시 본 약관을 개정할 수 있으며, 변경 사항은 본 페이지에 게시합니다.</p>

<p class="updated">최종 개정: 2026-06-15</p>
</div></main>
"""

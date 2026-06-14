#!/usr/bin/env python3
# build_site.py
# data/sector_latest.json 을 읽어 site/ 폴더 전체를 생성한다.
# 매 거래일 저녁 menu[2] 루틴 끝에 이 스크립트를 호출하면 사이트가 자동 갱신된다.
#
#   python build_site.py
#
# 산출물: site/index.html (히트맵, 데이터 내장) + 정책/정보 6페이지 + style.css + robots.txt + sitemap.xml

import json
import os
import sys
from datetime import datetime

import content as C

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "sector_latest.json")
THEME_NEWS = os.path.join(HERE, "data", "theme_news.json")
MARKET_IND = os.path.join(HERE, "data", "market_indicators.json")
SITE = os.path.join(HERE, "site")

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]
LABEL_KO = {
    "BULL": "다 올랐슈", "STRONG": "쎘슈", "NORMAL": "그냥저냥유", "WEAK": "시원찮유",
    "EXTREME": "정신없었슈", "NARROW": "몇 개만 올랐슈", "NARROW_EXTREME": "진짜 몇 개만 올랐슈",
}


def market_status():
    """빌드 시각 기준 장 세션 문구. NXT(08:00~20:00)까지 반영."""
    now = datetime.now()
    if now.weekday() >= 5:            # 토/일
        return "지난 장 기준이유"
    t = now.hour * 60 + now.minute
    if t < 8 * 60:                    # ~08:00
        return "아직 장 안 열렸슈 · 어제 기준"
    if t < 8 * 60 + 50:              # 08:00~08:50 NXT 프리마켓
        return "프리마켓 도는 중이유"
    if t < 9 * 60:                    # 08:50~09:00 동시호가 휴장
        return "곧 정규장 열려유"
    if t < 15 * 60 + 30:            # 09:00~15:30 정규장(KRX)+NXT메인
        return "장 도는 중이유"
    if t < 20 * 60:                  # 15:30~20:00 NXT 애프터마켓
        return "애프터마켓 도는 중이유"
    return "장 끝나고 기준"            # 20:00~


def fmt_date(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{date_str} ({WEEKDAY_KO[d.weekday()]})"
    except Exception:
        return date_str


def signed(v, dec=2):
    return f"{'+' if v >= 0 else ''}{v:.{dec}f}"


def render_ticker():
    """data/market_indicators.json → (시각 블록 HTML, 지표 바 HTML). 없으면 ('','')."""
    try:
        with open(MARKET_IND, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return "", ""
    inds = data.get("indicators", [])
    chips = []
    for it in inds:
        v = it.get("value")
        if v is None:
            continue
        digits = int(it.get("digits", 2))
        unit = it.get("unit", "")
        try:
            num = f"{v:,.{digits}f}"
        except Exception:
            num = str(v)
        val = f"${num}" if unit == "$" else f"{num}{unit}"
        chg = it.get("change_pct")
        if chg is None:
            cstr, ccls = "–", "flat-num"
        else:
            ccls = "up-num" if chg > 0 else ("down-num" if chg < 0 else "flat-num")
            cstr = f"{'+' if chg >= 0 else ''}{chg:.2f}%"
        chips.append(
            f'<span class="tk"><span class="tk-k">{it.get("label", "")}</span>'
            f'<span class="tk-v">{val}</span>'
            f'<span class="tk-c {ccls}">{cstr}</span></span>'
        )
    if not chips:
        return "", ""
    hhmm = ""
    up = data.get("updated", "")
    if "T" in up:
        hhmm = up.split("T", 1)[1][:8]
    time_html = ('<div class="hero-time"><span class="ht-k">시세 기준 · 실시간 아니유</span>'
                 f'<span class="ht-v">{hhmm or "—"}</span></div>')
    bar_html = '\n<div class="ticker">' + "".join(chips) + '</div>'
    return time_html, bar_html


def load_indicators():
    try:
        with open(MARKET_IND, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def strip_unused_stocks(sectors, keep=50):
    # 트리맵 타일(클라이언트 TOP_N=40, avg_return>0)에서만 stocks/news가 화면에 쓰임.
    # 그 밖 섹터의 stocks/news는 표·트리맵 어디에도 안 떠서 payload에서 제거(무손실 경량화).
    # keep=50 = TOP_N 40 + 정렬 동률 여유 10. push_kv.py에도 동일 로직 유지할 것.
    pos = sorted([s for s in sectors if s.get("avg_return", 0) > 0],
                 key=lambda s: s.get("avg_return", 0), reverse=True)
    keep_ids = {id(s) for s in pos[:keep]}
    for s in sectors:
        if id(s) not in keep_ids:
            s.pop("stocks", None)
            s.pop("news", None)
    return sectors


def build_summary(sectors, n_total):
    top = [s["theme"] for s in sorted(sectors, key=lambda s: s.get("avg_return", 0), reverse=True)[:3]]
    if not top:
        return "오늘은 집계된 테마가 없슈."
    names = ", ".join(top)
    return (f"오늘 제일 센 테마는 {names} 쪽이었슈.<br>"
            f"전체 {n_total}개, 급할 거 없으니께 아래에서 천천히 보고 가유.")


def render_index(d):
    sectors = sorted(d.get("sectors", []), key=lambda s: s.get("weighted_strong", 0), reverse=True)
    market = d.get("market", {})
    n_total = len(sectors)
    date_disp = fmt_date(d.get("date", ""))
    gen_at = d.get("generated_at", "")
    label = market.get("label", "")
    label_ko = LABEL_KO.get(label, label)
    MOOD_CLS = {"BULL": "mood-bull", "STRONG": "mood-strong", "NORMAL": "mood-normal",
                "WEAK": "mood-weak", "EXTREME": "mood-extreme",
                "NARROW": "mood-narrow", "NARROW_EXTREME": "mood-narrow"}
    mood_cls = MOOD_CLS.get(label, "mood-normal")

    kospi = market.get("kospi_change", 0.0)
    kosdaq = market.get("kosdaq_change", 0.0)

    def numcls(v):
        return "up-num" if v > 0 else ("down-num" if v < 0 else "flat-num")

    hero = """<section class="hero">
<div class="date" id="heroDate"></div>
<div class="hero-top">
  <h1>오늘 뭐 올랐슈~?</h1>
  <div class="hero-time" id="heroTime" style="display:none"></div>
</div>
<div class="market-row" id="marketRow"></div>
<p class="summary" id="heroSummary"></p>
<div id="tickerHost"></div>
</section>
"""

    legend = """<section class="legend">
<span><b>색</b> 진할수록 많이 올랐슈</span>
<span class="grad"></span>
<span style="color:var(--text-lo)">쪼끔</span><span style="color:var(--up)">많이</span>
<span style="margin-left:auto; color:var(--text-lo)">눌러보면 더 나와유</span>
</section>
"""

    grid_table = """<div class="grid" id="grid"></div>
<div class="grid-hint" id="ghint">칸 크기 = 평균 상승률, 색 진할수록 많이 올랐슈. 눌러보면 뭐뭐 들었는지·왜 올랐는지 나와유.</div>
<div id="detailHost"></div>

<div class="table-wrap">
  <div class="table-head">
    <h2>싹 다 보기</h2>
    <span class="count" id="tcount"></span>
    <div class="sortbtns">
      <button data-sort="up_pct" class="on">비율순</button>
      <button data-sort="avg_return">등락순</button>
      <button data-sort="strong_count">5%↑순</button>
    </div>
  </div>
  <div style="overflow-x:auto">
  <table>
    <thead><tr>
      <th>테마</th><th>평균 등락</th><th>5%↑ 종목</th><th>오른 비율</th><th>등급</th>
    </tr></thead>
    <tbody id="tbody"></tbody>
  </table>
  </div>
</div>
"""

    indicators = load_indicators()
    strip_unused_stocks(sectors)
    payload = {
        "date": d.get("date", ""),
        "generated_at": gen_at,
        "market": market,
        "sectors": sectors,
        "indicators": indicators,
    }
    data_script = ('<script type="application/json" id="sector-data">'
                   + json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
                   + "</script>\n")

    render_js = """<script>
(function(){
  var SNAPSHOT = JSON.parse(document.getElementById('sector-data').textContent);
  var S=[], market={}, inds={}, curDate='', tiles=[], lastGen=null, curKey='up_pct';

  // 색=등락(절대 정수% 구간). 0~7%+ 8단계, 7% 이상은 제일 진함. 당일 최대값과 무관.
  function heat(r){
    var light = document.documentElement.dataset.theme==='light';
    if(r>=0){
      var lv=Math.min(Math.floor(r),7);
      var lo=0.12, hi=light?0.90:0.96;
      var a=lo + lv*(hi-lo)/7;
      return 'rgba(229,72,77,'+a.toFixed(3)+')';
    }
    var lv2=Math.min(Math.floor(Math.abs(r)),5);
    var lo2=0.12, hi2=light?0.58:0.70;
    var b=lo2 + lv2*(hi2-lo2)/5;
    return 'rgba(90,110,130,'+b.toFixed(3)+')';
  }
  function paintHeat(){
    Array.prototype.forEach.call(document.querySelectorAll('#grid .heat'),function(h){
      h.style.background = heat(parseFloat(h.getAttribute('data-ret'))||0);
    });
  }
  window.repaintHeat = paintHeat;
  function sgn(v,d){d=d||2; return (v>=0?'+':'')+Number(v).toFixed(d);}
  function chg(v){return (v>=0?'+':'')+Number(v).toFixed(2)+'%';}
  function numcls(v){return v>0?'up-num':(v<0?'down-num':'flat-num');}

  var WD=['일','월','화','수','목','금','토'];
  function fmtDate(s){
    if(!s||s.length<10) return s||'';
    var y=+s.slice(0,4), mo=+s.slice(5,7), da=+s.slice(8,10);
    if(!y||!mo||!da) return s;
    return s+' ('+WD[new Date(y,mo-1,da).getDay()]+')';
  }
  function marketStatus(){
    var now=new Date(), d=now.getDay();
    if(d===0||d===6) return '지난 장 기준이유';
    var t=now.getHours()*60+now.getMinutes();
    if(t<480) return '아직 장 안 열렸슈 · 어제 기준';
    if(t<530) return '프리마켓 도는 중이유';
    if(t<540) return '곧 정규장 열려유';
    if(t<930) return '장 도는 중이유';
    if(t<1200) return '애프터마켓 도는 중이유';
    return '장 끝나고 기준';
  }
  var LABEL_KO={BULL:'다 올랐슈',STRONG:'쎘슈',NORMAL:'그냥저냥유',WEAK:'시원찮유',EXTREME:'정신없었슈',NARROW:'몇 개만 올랐슈',NARROW_EXTREME:'진짜 몇 개만 올랐슈'};
  var MOOD_CLS={BULL:'mood-bull',STRONG:'mood-strong',NORMAL:'mood-normal',WEAK:'mood-weak',EXTREME:'mood-extreme',NARROW:'mood-narrow',NARROW_EXTREME:'mood-narrow'};
  function buildSummary(arr,n){
    var top=arr.slice().sort(function(a,b){return b.avg_return-a.avg_return;}).slice(0,3).map(function(s){return s.theme;});
    if(!top.length) return '오늘은 집계된 테마가 없슈.';
    return '오늘 제일 센 테마는 '+top.join(', ')+' 쪽이었슈.<br>전체 '+n+'개, 급할 거 없으니께 아래에서 천천히 보고 가유.';
  }
  function renderHero(){
    var label=market.label||'', labelKo=LABEL_KO[label]||label, moodCls=MOOD_CLS[label]||'mood-normal';
    var kospi=market.kospi_change||0, kosdaq=market.kosdaq_change||0;
    document.getElementById('heroDate').textContent=fmtDate(curDate)+' · '+marketStatus();
    document.getElementById('marketRow').innerHTML=
      '<span class="chip mood '+moodCls+'">오늘 장 · '+labelKo+'</span>'+
      '<span class="chip"><span class="k">코스피</span><span class="v '+numcls(kospi)+'">'+sgn(kospi)+'%</span></span>'+
      '<span class="chip"><span class="k">코스닥</span><span class="v '+numcls(kosdaq)+'">'+sgn(kosdaq)+'%</span></span>'+
      '<span class="chip"><span class="k">본 테마</span><span class="v">'+S.length+'</span></span>';
    document.getElementById('heroSummary').innerHTML=buildSummary(S,S.length);
  }
  function renderTime(){
    var up=(inds&&inds.updated)||'', el=document.getElementById('heroTime'), arr=(inds&&inds.indicators)||[];
    if(!arr.length){ el.style.display='none'; return; }
    el.style.display='';
    var hhmm='—'; if(up.indexOf('T')>=0) hhmm=up.split('T')[1].slice(0,8);
    el.innerHTML='<span class="ht-k">시세 기준 · 실시간 아니유</span><span class="ht-v">'+hhmm+'</span>';
  }
  function renderTicker(){
    var arr=(inds&&inds.indicators)||[], host=document.getElementById('tickerHost');
    if(!arr.length){ host.innerHTML=''; return; }
    var chips=arr.map(function(it){
      if(it.value==null) return '';
      var digits=(it.digits!=null)?it.digits:2, unit=it.unit||'';
      var num=Number(it.value).toLocaleString('en-US',{minimumFractionDigits:digits,maximumFractionDigits:digits});
      var val=(unit==='$')?('$'+num):(num+unit);
      var c=it.change_pct, cstr, ccls;
      if(c==null){ cstr='–'; ccls='flat-num'; }
      else{ ccls=c>0?'up-num':(c<0?'down-num':'flat-num'); cstr=(c>=0?'+':'')+Number(c).toFixed(2)+'%'; }
      return '<span class="tk"><span class="tk-k">'+it.label+'</span><span class="tk-v">'+val+'</span><span class="tk-c '+ccls+'">'+cstr+'</span></span>';
    }).join('');
    host.innerHTML='<div class="ticker">'+chips+'</div>';
  }

  // ---- 트리맵: 오른(+) 테마 중 상승률 상위 TOP_N. 위치=오른 비율 우선, 크기=평균 상승률 ----
  var TOP_N = 40;
  function recomputeTiles(){
    tiles = S.filter(function(s){return s.avg_return>0;})
             .sort(function(a,b){return b.avg_return-a.avg_return;})
             .slice(0,TOP_N)
             .sort(function(a,b){return (b.up_pct-a.up_pct) || (b.avg_return-a.avg_return);});
  }
  var grid = document.getElementById('grid');
  var detailHost = document.getElementById('detailHost');
  var detail=document.createElement('div'); detail.className='detail'; detail.style.display='none';

  function buildDetail(s){
    var tname={2:'짱 쎄유',1:'쎄유',0:'그냥'}[s.tier]||'그냥';
    var stocksHtml;
    if(s.stocks && s.stocks.length){
      stocksHtml=s.stocks.map(function(st){
        var c=st.change>0?'up-num':(st.change<0?'down-num':'flat-num');
        var c2=(st.change!=null)?'<span class="'+c+'">'+chg(st.change)+'</span>':'';
        return '<span class="d-stock">'+st.name+c2+'</span>';
      }).join('');
    } else { stocksHtml='<div class="d-empty">곧 채울게유.</div>'; }
    var newsHtml;
    if(s.news && s.news.length){
      newsHtml=s.news.map(function(n){
        var src=n.source?'<span class="d-src">'+n.source+'</span>':'';
        return '<a class="d-news" href="'+n.url+'" target="_blank" rel="noopener">'+n.title+src+'</a>';
      }).join('');
    } else { newsHtml='<div class="d-empty">뭔 일 있었는지 아직 못 찾았슈.</div>'; }
    return '<button class="d-close" aria-label="닫기">×</button>'+
      '<div class="d-head"><span class="d-theme">'+s.theme+'</span>'+
        '<span class="d-ret '+(s.avg_return>=0?'up-num':'down-num')+'">'+sgn(s.avg_return)+'%</span></div>'+
      '<div class="d-stats">'+
        '<span><i>5%↑ 종목</i>'+s.strong_count+'</span>'+
        '<span><i>본 종목</i>'+s.data_count+'</span>'+
        '<span><i>전체</i>'+s.total_count+'</span>'+
        '<span><i>오른 비율</i>'+s.up_pct+'%</span>'+
        '<span><i>등급</i>'+tname+'</span>'+
      '</div>'+
      '<div class="d-sec"><h4>뭐뭐 들었슈</h4><div class="d-stocks">'+stocksHtml+'</div></div>'+
      '<div class="d-sec"><h4>왜 올랐댜?</h4><div class="d-newslist">'+newsHtml+'</div></div>';
  }
  function clearOpen(){ Array.prototype.forEach.call(grid.querySelectorAll('.tile.open'),function(t){t.classList.remove('open');}); }
  function closeDetail(){ detail.style.display='none'; clearOpen(); }
  function openDetail(el,s){
    detail.innerHTML=buildDetail(s);
    detailHost.appendChild(detail);
    detail.style.display='block';
    clearOpen(); el.classList.add('open');
    detail.querySelector('.d-close').addEventListener('click',function(e){e.stopPropagation(); closeDetail();});
    detail.scrollIntoView({behavior:'smooth', block:'nearest'});
  }

  // squarified treemap
  function worst(row,len,scale){
    var sum=0,mx=-Infinity,mn=Infinity;
    for(var k=0;k<row.length;k++){var a=row[k]*scale; sum+=a; if(a>mx)mx=a; if(a<mn)mn=a;}
    var l2=len*len, s2=sum*sum;
    return Math.max(l2*mx/s2, s2/(l2*mn));
  }
  function layout(items,W,H){
    var total=0; for(var k=0;k<items.length;k++) total+=items[k].avg_return;
    if(total<=0) return [];
    var scale=(W*H)/total;
    var x=0,y=0,w=W,h=H,i=0,n=items.length,out=new Array(n);
    while(i<n){
      var side=Math.min(w,h);
      var row=[items[i].avg_return], idx=[i], j=i+1;
      while(j<n){
        var nrow=row.concat([items[j].avg_return]);
        if(worst(row,side,scale) >= worst(nrow,side,scale)){ row=nrow; idx.push(j); j++; }
        else break;
      }
      var rsum=0; for(var k=0;k<row.length;k++) rsum+=row[k]*scale;
      if(w>=h){
        var colW=rsum/h, yy=y;
        for(var k=0;k<row.length;k++){ var ch=(row[k]*scale)/colW; out[idx[k]]={s:items[idx[k]],x:x,y:yy,w:colW,h:ch}; yy+=ch; }
        x+=colW; w-=colW;
      } else {
        var rowH=rsum/w, xx=x;
        for(var k=0;k<row.length;k++){ var cw=(row[k]*scale)/rowH; out[idx[k]]={s:items[idx[k]],x:xx,y:y,w:cw,h:rowH}; xx+=cw; }
        y+=rowH; h-=rowH;
      }
      i=j;
    }
    return out;
  }
  function render(){
    detail.style.display='none';
    grid.innerHTML='';
    var ghint=document.getElementById('ghint');
    if(!tiles.length){
      grid.style.height='auto';
      grid.innerHTML='<div style="color:var(--text-lo);padding:30px 4px">오늘은 오른 테마가 없슈. 아래 표나 보고 가유.</div>';
      if(ghint) ghint.style.display='none';
      return;
    }
    var W=grid.clientWidth||900;
    var H = W<560 ? Math.round(W*1.5) : Math.round(Math.min(W,960));
    grid.style.height=H+'px';
    var GAP = W<560 ? 0 : 3;
    layout(tiles,W,H).forEach(function(p){
      var s=p.s, cw=Math.max(0,p.w-GAP), ch=Math.max(0,p.h-GAP);
      var el=document.createElement('div');
      el.className='tile'+(s.tier>=2?' t2':'');
      el.style.cssText='position:absolute;left:'+(p.x+GAP/2).toFixed(1)+'px;top:'+(p.y+GAP/2).toFixed(1)+'px;width:'+cw.toFixed(1)+'px;height:'+ch.toFixed(1)+'px;min-height:0;padding:'+(cw<92?'6px 8px':'12px 13px');
      var retStr=sgn(s.avg_return)+'%';
      var pad=(cw<92?14:24);
      var retFs=Math.max(11,Math.min((cw-pad)/(retStr.length*0.60), ch*0.26, 30));
      var nameLen=Math.max(s.theme.length,4);
      var padV=(cw<92?6:12);
      var retH=retFs*1.2+8;                        // % 글자높이+여백
      var availName=Math.max(ch - padV*2 - retH - 2, 12);
      var maxW=Math.max(cw - padV*2, 10);
      var capFs=Math.min(cw*0.16, 18);
      var nameFs=9;                                 // 못 찾으면 최소
      var cwf=(W<560?0.95:0.56);                     // 한글은 거의 정사각 → 모바일은 글자폭 정확히 잡아 잘림 방지
      for(var fz=capFs; fz>=9; fz-=0.5){
        var cpl=Math.max(1, Math.floor(maxW/(fz*cwf)));    // 한 줄 글자수
        var ln=Math.ceil(nameLen/cpl);                     // 필요 줄수
        if(ln*fz*1.22 <= availName){ nameFs=fz; break; }   // 다 들어가면 채택
      }
      var nameLines=Math.max(1, Math.floor(availName/(nameFs*1.22)));
      var showName=(cw>46&&ch>38), showRet=(cw>34&&ch>26);
      var nameStyle='flex:1 1 auto;min-height:0;font-size:'+nameFs.toFixed(1)+'px;line-height:1.22;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:'+nameLines+';overflow:hidden';
      var inner='<div class="heat" data-ret="'+s.avg_return+'"></div><div class="body">';
      inner += showName ? '<div class="theme" style="'+nameStyle+'">'+s.theme+'</div>' : '<div style="flex:1 1 auto"></div>';
      inner += '<div style="flex:0 0 auto">';
      if(showRet) inner += '<div class="ret" style="font-size:'+retFs.toFixed(1)+'px">'+retStr+'</div>';
      inner += '</div></div>';
      el.innerHTML=inner;
      el.title=s.theme+' '+sgn(s.avg_return)+'%';
      el.addEventListener('click',function(){ if(el.classList.contains('open')) closeDetail(); else openDetail(el,s); });
      grid.appendChild(el);
    });
    paintHeat();
  }
  var rzT, lastW=window.innerWidth;
  window.addEventListener('resize',function(){
    if(window.innerWidth===lastW) return;   // 높이만 바뀌는 모바일 주소창 스크롤은 무시 → 상세 안 닫힘
    lastW=window.innerWidth;
    clearTimeout(rzT); rzT=setTimeout(render,160);
  });

  // ---- full table with sort ----
  var tbody=document.getElementById('tbody');
  var tierTxt={2:'짱 쎄유',1:'쎄유',0:'–'};
  function rowHtml(s){
    var rc = s.avg_return>0?'up-num':(s.avg_return<0?'down-num':'flat-num');
    return '<tr>'+
      '<td>'+s.theme+'</td>'+
      '<td class="num '+rc+'">'+sgn(s.avg_return)+'%</td>'+
      '<td class="num">'+s.strong_count+'</td>'+
      '<td class="num">'+s.up_pct+'%</td>'+
      '<td><span class="t-tier x'+s.tier+'">'+(tierTxt[s.tier]||'–')+'</span></td>'+
    '</tr>';
  }
  function renderTable(key){
    var arr=S.slice().sort(function(a,b){return (b[key]-a[key]) || (b.avg_return-a.avg_return);});
    tbody.innerHTML=arr.map(rowHtml).join('');
  }
  renderTable('up_pct');
  var btns=document.querySelectorAll('.sortbtns button');
  btns.forEach(function(b){
    b.addEventListener('click',function(){
      btns.forEach(function(x){x.classList.remove('on');});
      b.classList.add('on');
      curKey=b.getAttribute('data-sort');
      renderTable(curKey);
    });
  });

  // ---- 데이터 적용 + 60초 폴링(라이브) ----
  function applyData(d, initial){
    S=(d.sectors||[]).slice(); market=d.market||{}; inds=d.indicators||{}; curDate=d.date||'';
    renderHero(); renderTime(); renderTicker();
    if(initial || d.generated_at!==lastGen){          // 데이터 실제로 바뀐 경우만 트리맵·표 재구성
      lastGen=d.generated_at;
      recomputeTiles(); render(); renderTable(curKey);
      document.getElementById('tcount').textContent='총 '+S.length+'개';
    }
  }
  function fetchData(){
    fetch('/api/data',{cache:'no-store'}).then(function(r){return r.ok?r.json():null;})
      .then(function(j){ if(j&&j.sectors&&j.sectors.length) applyData(j,false); }).catch(function(){});
  }
  applyData(SNAPSHOT, true);   // 인라인 스냅샷으로 즉시 렌더
  fetchData();                 // 곧바로 최신값으로 갱신
  setInterval(fetchData, 60000);
})();
</script>
"""

    body = ('<main class="wrap">' + hero + legend + grid_table + '</main>\n'
            + data_script + render_js)

    title = f"오늘 뭐 올랐슈 · {date_disp} | {C.SITE_NAME}"
    return C.wrap_page(title, C.SITE_DESC, "index.html", "index.html", body)


def robots_txt():
    return f"User-agent: *\nAllow: /\nSitemap: {C.BASE_URL}/sitemap.xml\n"


def sitemap_xml():
    pages = ["index.html", "guide.html", "about.html", "faq.html",
             "disclaimer.html", "privacy.html", "terms.html"]
    today = datetime.today().strftime("%Y-%m-%d")
    items = "".join(
        f"  <url><loc>{C.BASE_URL}/{p}</loc><lastmod>{today}</lastmod></url>\n"
        for p in pages
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + items + "</urlset>\n")


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    if not os.path.exists(DATA):
        print(f"[ERROR] 데이터 파일 없음: {DATA}", file=sys.stderr)
        sys.exit(1)
    with open(DATA, encoding="utf-8") as f:
        d = json.load(f)

    # theme_news.json 있으면 각 섹터에 news 부착(없으면 펼침 패널은 "준비 중" 표시)
    news_map = {}
    if os.path.exists(THEME_NEWS):
        try:
            with open(THEME_NEWS, encoding="utf-8") as f:
                news_map = json.load(f).get("themes", {})
        except Exception:
            news_map = {}
    n_with_news = 0
    for s in d.get("sectors", []):
        nl = news_map.get(s.get("theme"))
        if nl:
            s["news"] = nl
            n_with_news += 1

    os.makedirs(SITE, exist_ok=True)

    write(os.path.join(SITE, "style.css"), C.css())
    write(os.path.join(SITE, "index.html"), render_index(d))

    static_pages = {
        "about.html":      ("소개", C.page_about),
        "guide.html":      ("히트맵 보는 법", C.page_guide),
        "faq.html":        ("자주 묻는 질문", C.page_faq),
        "disclaimer.html": ("투자정보 고지", C.page_disclaimer),
        "privacy.html":    ("개인정보처리방침", C.page_privacy),
        "terms.html":      ("이용약관", C.page_terms),
    }
    for fname, (subtitle, fn) in static_pages.items():
        title = f"{subtitle} | {C.SITE_NAME}"
        html = C.wrap_page(title, C.SITE_DESC, fname, fname, fn())
        write(os.path.join(SITE, fname), html)

    write(os.path.join(SITE, "robots.txt"), robots_txt())
    write(os.path.join(SITE, "sitemap.xml"), sitemap_xml())

    print(f"[OK] 생성 완료 → {SITE}")
    print(f"     날짜: {d.get('date')}  테마: {len(d.get('sectors', []))}개  뉴스부착: {n_with_news}개")
    print(f"     페이지: index + {len(static_pages)} + style.css + robots + sitemap")


if __name__ == "__main__":
    main()

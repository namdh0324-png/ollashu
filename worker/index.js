// worker/index.js
// /api/data 요청 → KV(DATA)의 "latest" 값을 그대로 반환(최신 섹터·지표 JSON).
// 그 외 경로 → 정적 자산(site/)으로 위임. 정적 자산은 기본적으로 Worker보다 먼저 서빙되므로
// 이 핸들러는 /api/* 와 매칭 안 되는 경로에서만 실행된다.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/data") {
      let body = "{}";
      try {
        const v = await env.DATA.get("latest");
        if (v) body = v;
      } catch (e) {}
      return new Response(body, {
        headers: {
          "content-type": "application/json; charset=utf-8",
          "cache-control": "no-store",
          "access-control-allow-origin": "*"
        }
      });
    }
    return env.ASSETS.fetch(request);
  }
};

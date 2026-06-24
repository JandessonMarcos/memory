// Memory Lab — Cloudflare Worker (static assets + lead capture)
// -----------------------------------------------------------------------------
// Workers Static Assets serves every real file (the 23 pages, /assets/*) BEFORE
// this Worker runs. So the only requests that reach fetch() are non-asset paths:
// we handle POST /api/lead (-> D1), and fall through to the assets 404 for the rest.
// Static serving is therefore unchanged; the Worker only ADDS the /api/lead route.
//
// Binding DB -> D1 "memorylab-leads".  Mirrors functions/api/lead.js (Pages),
// which www does not use (www is served by this Worker).
// -----------------------------------------------------------------------------

const CORS = {
  "Content-Type": "application/json",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: CORS });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/lead") {
      if (request.method === "OPTIONS") return new Response(null, { headers: CORS });
      if (request.method === "POST") return handleLead(request, env);
      return json({ ok: false, error: "method_not_allowed" }, 405);
    }

    // Not an API route. Hand back to the static-assets system (serves the file or its 404).
    return env.ASSETS.fetch(request);
  },
};

async function handleLead(request, env) {
  try {
    const body = await request.json().catch(() => ({}));

    if (body.website) return json({ ok: true }); // honeypot tripped: pretend success, store nothing

    const email = String(body.email || "").trim().toLowerCase();
    if (!EMAIL_RE.test(email) || email.length > 254) {
      return json({ ok: false, error: "invalid_email" }, 400);
    }
    if (!env.DB) return json({ ok: false, error: "db_unbound" }, 200);

    const now = new Date().toISOString();
    const day = now.slice(0, 10);
    const a = body.answers || {};
    const utm = body.utm || {};
    const country = request.headers.get("cf-ipcountry") || "";
    const ua = (request.headers.get("user-agent") || "").slice(0, 400);

    await env.DB.prepare(
      `INSERT INTO leads
         (lead_id,email,subid,segment,q_symptom,q_age,q_dur,q_tried,
          source_page,referrer,incoming_clickid,utm_source,utm_medium,utm_campaign,
          country,ua,status,event_day,created_at,raw)
       VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14,?15,?16,'new',?17,?18,?19)
       ON CONFLICT(email) DO UPDATE SET
         subid=excluded.subid, segment=excluded.segment,
         q_symptom=excluded.q_symptom, q_age=excluded.q_age,
         q_dur=excluded.q_dur, q_tried=excluded.q_tried,
         source_page=excluded.source_page, raw=excluded.raw`
    )
      .bind(
        String(body.lead_id || ""),
        email,
        String(body.subid || ""),
        String(body.segment || ""),
        String(a.symptom || ""),
        String(a.age || ""),
        String(a.dur || ""),
        String(a.tried || ""),
        String(body.source_page || ""),
        String(body.referrer || "").slice(0, 400),
        String(body.incoming_clickid || ""),
        String(utm.source || ""),
        String(utm.medium || ""),
        String(utm.campaign || ""),
        country,
        ua,
        day,
        now,
        JSON.stringify(body).slice(0, 4000)
      )
      .run();

    return json({ ok: true });
  } catch (e) {
    return json({ ok: false, error: "server", detail: String((e && e.message) || e) }, 500);
  }
}

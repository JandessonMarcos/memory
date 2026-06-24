/* ============================================================================
   Memory Lab — lead capture endpoint  (Cloudflare Pages Function)
   Route: POST /api/lead   (auto-mapped from functions/api/lead.js)
   ----------------------------------------------------------------------------
   Stores the "Memory Check" quiz lead in OUR own D1 (binding: DB).
   - Honeypot + email validation + upsert-by-email (no dupes).
   - Stores `subid` (quiz_<leadId>_<segment>) so a later BuyGoods sale — whose
     subid the financial panel records in `sales` — can be matched back to this
     exact lead. That join is the data-ownership payoff: capture -> $215 sale.
   - Same-origin POST, so CORS isn't required; headers added for safety/local dev.
   SETUP (one-time): see _automation/LEADS-SETUP.md  (create D1, apply schema,
   bind it as `DB` on the Pages project).
   ============================================================================ */

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

export async function onRequestOptions() {
  return new Response(null, { headers: CORS });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  try {
    const body = await request.json().catch(() => ({}));

    // honeypot: a filled "website" field = bot. Pretend success, store nothing.
    if (body.website) return json({ ok: true });

    const email = String(body.email || "").trim().toLowerCase();
    if (!EMAIL_RE.test(email) || email.length > 254) {
      return json({ ok: false, error: "invalid_email" }, 400);
    }

    if (!env.DB) {
      // Binding not configured yet. Don't 500 the visitor's funnel.
      return json({ ok: false, error: "db_unbound" }, 200);
    }

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
    return json({ ok: false, error: "server", detail: String(e && e.message || e) }, 500);
  }
}

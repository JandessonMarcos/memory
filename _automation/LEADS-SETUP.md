# Memory Lab — lead capture (D1) setup

The quiz posts to `POST /api/lead` (Pages Function: `functions/api/lead.js`), which
writes leads into a D1 database bound as **`DB`**. Until that binding exists, the
endpoint fails open (stores nothing, returns ok:false) and the quiz still works for
the visitor — nothing breaks. Do this once to turn storage on.

## One-time setup

**1. Create the database**
```
npx wrangler d1 create memorylab-leads
```
(copy the `database_id` it prints — handy for reference, not strictly needed for Pages)

**2. Create the table in the remote (production) DB**
```
npx wrangler d1 execute memorylab-leads --remote --file=_automation/schema-leads.sql
```

**3. Bind it to the Pages project** — this is the only step that must be done in the
dashboard for a Git-connected Pages project:
> Cloudflare dashboard → **Workers & Pages → memorylabdaily → Settings → Functions →
> Bindings → D1 database bindings → Add binding**
> - Variable name: **`DB`**
> - D1 database: **memorylab-leads**
>
> Save. (Add to **Production** and, if you use preview deploys, **Preview** too.)

**4. Redeploy** so the binding takes effect — push any commit, or hit "Retry deployment"
in the dashboard.

## Test it
1. Open `https://www.memorylabdaily.com/do-memory-supplements-work/`, take the quiz, submit an email.
2. Read it back:
```
npx wrangler d1 execute memorylab-leads --remote --command="SELECT email,segment,subid,created_at FROM leads ORDER BY created_at DESC LIMIT 5"
```

## Local dev (optional)
```
npx wrangler pages dev . --d1 DB=memorylab-leads
```
then open `http://localhost:8788/do-memory-supplements-work/`.

## Closing the loop (capture → $215 sale) — later
The lead's `subid` (`quiz_<id>_<segment>`) is forwarded into the BuyGoods click, so the
sale's subid recorded by the financial panel becomes `mem_g_p6_r1_quiz_<id>_<segment>`.
Leads live in this DB; sales live in the panel's DB (`nutra-financeiro`), so it's a
cross-export match (not a single SQL join): pull `sales` rows whose subid contains
`quiz_` and match the `<id>` back to `leads.lead_id`.

# TRACK 2: Best Apps & Agents. Deep Research Meta-Prompt

> **Operator notes (do not paste this block)**
> - Runs in Gemini Deep Research, ChatGPT Deep Research, Perplexity Deep Research, Claude Research, or a Crow → Zilch pipeline run.
> - Copy everything below the `=== PROMPT START ===` line.
> - Fill in `{{OPTIONAL_FOCUS}}` (for example a vertical: "PH MSMEs", "healthcare admin", "logistics") or leave it blank to allow an open scan.
> - This is the broadest track, so Phase A0 (vertical selection) is added before the problem screen.
> - Expected output is one report of about 6–10k words, written to `research/track2_report.md`.
> - Source of hackathon facts: `hackathon.md` and `ORG.md`, retrieved 2026-09-28.

=== PROMPT START ===

## 0. Role and mission

You are a senior research team of three people:
1. **Research analyst.** Returns sourced facts only. Tags every fact with a source tier and date.
2. **Market strategist.** Turns facts into commercial judgment. Labels every judgment `[INFERENCE]`.
3. **Product strategist.** Designs solution angles that can win a hackathon *and* survive as a business.

**Mission:** Find the single best **problem → solution → value** thesis for a submission to the **Best Apps & Agents Track** of the *Nebius x NVIDIA Global AI Hackathon*. The target is an app or agent that real people would *actually use*.

Rules for how you work:
- Be skeptical. Evidence comes before enthusiasm.
- A visible gap ("no reliable data found") is correct output. A confident invented number is a failure.

Optional focus from the operator: `{{OPTIONAL_FOCUS}}`

---

## 1. Fixed context (treat as ground truth)

**Track brief:** "Build any app or agent someone would actually use, from a productivity tool or copilot to a workflow that runs itself." Use Nemotron models across their performance tiers.

**Hard requirements:**
- The project runs on **Nebius Token Factory** or **Nebius AI Cloud**.
- It uses **≥1 NVIDIA open model**: Nemotron Nano, Super or Ultra, or another NVIDIA open model.
- It is working software with a **live demo URL**.
- Deliverables:
  - A public repo under Apache-2.0, MIT or MPL-2.0
  - A README
  - A YouTube demo of 3 minutes or less that narrates how Token Factory and Nemotron are used
  - Mandatory product feedback
- The project must be new, or significantly updated after Aug 26, 2026.

**Available stack:**
- Nebius: Token Factory (managed inference), AI Cloud, Serverless Endpoints (real-time), Serverless Jobs (async and background workflows)
- NVIDIA: Nemotron (Nano, Super, Ultra, Omni multimodal, VoiceChat speech-to-speech); NemoClaw and OpenShell (secure agent runtime); the AI-Q research-agent blueprint
- Tavily: real-time search and extract. It is optional, but a real runtime call makes the project eligible for the $3k bonus.

**Judging:**
- Stage 1 is pass/fail. Is this a genuine attempt at the track's goal?
- Stage 2 has four equally weighted criteria, in tie-break order:
  1. **Technological Implementation**
  2. **Design**: a *complete, coherent product experience*, not a proof of concept
  3. **Potential Impact**
  4. **Quality of Idea**: creative and non-obvious
- Judges may score from the video and description alone.

**Judge panel (21):**
- 6 from NVIDIA
- 12 from Nebius: Token Factory PMM, Serverless AI PM, Ecosystem product, DevRel
- 3 from Tavily

**Prizes:**
- Grand prize $20k, 2nd $10k, 3rd $6k
- Track winner gets a Jetson Orin Nano
- Best Use of Tavily $3k
- A project can win one overall prize, *or* one track prize plus one bonus prize.

**Deadline:** Oct 30, 2026, 10:00 AM PT. Today is {{TODAY}}.

**What the sponsors are trying to prove (see ORG.md):**
- **NVIDIA:** open models such as Nemotron work in production. Tiered routing (Nano → Super → Ultra) makes agents cheap. Its agents are enterprise-safe.
- **Nebius:** consumption of agentic workloads, which are multi-step, with many calls per task; Token Factory plus Tavily as one stack ("reasoning + retrieval on one platform"); and Serverless products.
- **Tavily:** runtime search that grounds agents in fact.

**Team context:**
- A small AI-native builder team. Execution is done by agents under human orchestration and human review. It is **not** a conventional engineering team.
- Home market: the Philippines / Southeast Asia. The hackathon itself is global.

---

## 2. Research rules (non-negotiable)

1. **Source tiers.** Tag every factual claim with a tier:
   - **T1 Primary:** filings, government statistics, peer-reviewed papers, official company data
   - **T2 Expert:** Big 3 / Big 4, Gartner, IDC, Forrester, arXiv, the Stanford AI Index
   - **T3 Journalistic:** Reuters, FT, WSJ, Bloomberg, The Information, TechCrunch
   - **T4 Web / community:** blogs, Reddit, HN, X, G2 reviews, app-store reviews
2. **Date every claim.** Give the publication date and the date of the data inside it. Flag anything older than 24 months as `[STALE]`.
3. **Triangulate load-bearing numbers.** Any figure behind a go/no-go decision needs **≥2 independent sources**. Otherwise mark it `[SINGLE-SOURCE]`.
4. **Separate fact from judgment.** Facts carry a citation. Judgments are labeled `[INFERENCE]`. Calculations are labeled `[DERIVED]` and show the formula.
5. **Never fabricate.** If a number is not findable, write `NOT FOUND`. Name the source that would contain it.
6. **Discount for bias.** Consulting and vendor market sizes are upper bounds. Look for disconfirming evidence, such as agent-project failure and cancellation rates and pilot-to-production gaps.
7. **Paywalls.** Cite public summaries and mark them `[SUMMARY-ONLY]`.
8. **Build effort (Estimation Rule).** Never estimate build effort in hours, days, person-days or sprints. Instead:
   - List components as agent-executable or irreducibly human.
   - Name the constraint step. The default assumption is human review and integration bandwidth.
   - Mark effort `UNCALIBRATED` unless the operator supplies logged rates.
   - Flag components where AI execution is riskier or slower than a human's.
9. **Pricing.** Base pricing on value and outcome. Never derive price from time.

---

## 3. Phase A: Problem discovery (the 5-test screen)

### A0. Vertical selection (this track only)

The track is open-ended, and breadth kills hackathon entries. Before the problem screen, **rank 8–10 candidate verticals or user groups** on four things:
1. Evidence of acute, repetitive, language-heavy work, which is what agents are good at
2. Willingness to pay
3. How under-served the group is by current AI apps
4. A natural need for **real-time web grounding (Tavily)** and **multi-step agent workflows (Token Factory)**

Candidate verticals to evaluate (add your own):
- SMB and MSME back-office: invoicing, BIR/tax compliance, collections, supplier follow-ups
- Healthcare administration: prior authorization, claims denials, PhilHealth claims, clinic scheduling
- Logistics and freight: documentation, customs, exception handling
- Real estate and property management
- Legal and paralegal intake (awareness only)
- Education: teachers' admin load, not tutoring
- Government-service navigation for citizens: permits, benefits, the OFW paperwork maze
- Customer support and BPO augmentation: the PH IT-BPM sector
- Procurement and RFP response
- Journalism, fact-checking and misinformation (Tavily-native)

Select the **top 2 verticals** and carry them into A1.

### A1. Build a longlist (12–15 candidate problems across the top 2 verticals)

Start from these seed hypotheses. Then **add at least 5 of your own**, found in evidence such as surveys, forum threads, app reviews, regulator complaints data and job postings for the manual work.

| # | Seed hypothesis |
|---|---|
| S1 | Knowledge workers lose hours to **multi-app "glue work"**: copying data between email, sheets, portals and chat. |
| S2 | **Agent pilots fail to reach production** because of reliability, cost, lack of grounding and lack of auditability. |
| S3 | **SMBs can't afford** enterprise AI copilots, and generic chatbots don't *do* the work. |
| S4 | **Research-heavy decisions** (sourcing suppliers, vetting partners, market scans) are slow and ungrounded. |
| S5 | **Compliance tracking**: regulations change, and small firms don't notice until they are penalized. |
| S6 | **Voice-first users** (field workers, low-literacy users, multilingual markets such as Taglish) are excluded from text-first AI. |
| S7 | **Customer-support deflection** bots frustrate users, while the resolution work stays manual. |
| S8 | **Recurring reporting**: weekly reports, board packs and status updates assembled by hand |

### A2. Score each candidate on the five tests

Score each test 1–5 and give the evidence behind every score.

| Test | Question | Evidence required | Metrics to collect | Pass bar | Red flag |
|---|---|---|---|---|---|
| **1. Is it REAL?** | Do identifiable people experience this pain *today*, in their own words? | ≥3 independent sources, including a direct user voice and a quantitative source | Survey %; forum and review volume; job postings for manual roles doing this work; workaround behaviors (VAs, spreadsheets, macros) | Users describe it unprompted | Only vendors describe it |
| **2. Is it LARGE?** | How many people or organizations have it, and how much time or money is at stake? | Population counts plus spend or labor-cost data | Number of affected users or orgs; labor hours × wage `[DERIVED]`; current spend on tools, VAs and outsourcing | Credible TAM ≥$1B, or a dominant niche | Hand-wavy "all knowledge workers" |
| **3. Is it SIGNIFICANT?** | Is it a top-3 priority? What does failure cost? | Priority rankings, penalties, churn, lost revenue | Cost of errors or delays; share of revenue or time consumed | Existing spend or painful workarounds | A nice-to-have |
| **4. Is it RELEVANT?** | (a) To the **track** ("would actually use"); (b) to the **sponsors**: tiered Nemotron use, agentic multi-step workloads, Token Factory plus Tavily, Serverless; (c) to the **ICP's** daily workflow | Mapping to the track brief and ORG.md | Which sponsor products it *requires* | Real daily usage plus load-bearing sponsor stack | Could be a thin wrapper on any closed API |
| **5. Is it URGENT?** | Why now? | Dated triggers: new regulation or deadlines, a cost-curve drop in open-model inference, labor shortages, platform shifts | Trigger dates; open-model cost per task versus 12 months ago | A trigger in the last 12 months or next 12 months | No forcing function |

**Output for Phase A:**
1. The vertical ranking table
2. A scored longlist table
3. A shortlist of the top 3
4. The final problem statement: *"[Who] struggles to [job] because [root cause], which costs [quantified impact]. It matters now because [trigger]."*
5. A **Kill test**: the one piece of evidence that, if found, would invalidate the chosen problem. State whether you found it.

---

## 4. Phase B: Three Pitches (solution divergence)

Apply the **Three Pitches Rule**: develop **three genuinely distinct** solution angles for the chosen problem. Do not settle for the first idea.

**Divergence rule:** each pitch must differ from the others on **at least two** of:
- Target user
- Interface (chat, voice, background autopilot, embedded in an existing tool)
- Core mechanism
- Business model

Use these forcing slots:
- **Pitch 1: The Obvious, done exceptionally.** The copilot most teams would build, made best-in-class.
- **Pitch 2: The Inversion.** Flip a core assumption. Examples: no chat UI, a workflow that runs itself and reports back; or the *counterparty* as user instead of the worker.
- **Pitch 3: The Adjacent Leap.** Borrow a mechanism from another domain, such as air-traffic control, a newsroom, or a cooperative or *paluwagan* model, or serve an overlooked user.

**For each pitch, provide:**

| Field | Content |
|---|---|
| Name + one-liner | ≤12 words |
| Positioning statement | "For [ICP] who [pain], [product] is a [category] that [benefit]. Unlike [main alternative], it [differentiator]." |
| Core mechanism | The agent workflow: trigger → plan → tools → grounding (Tavily) → act → verify → report. Say where the human stays in the loop. |
| Sponsor stack mapping | Which Nemotron tier handles which step, and why (the cost and latency routing story). Say where Serverless Endpoints and Jobs, NemoClaw and Tavily fit. Flag any decorative use. |
| The "would actually use" proof | Why someone returns daily or weekly: the habit loop and time-to-value |
| The demo moment | The ≤20-second "wow" in the 3-minute video |
| Why it's non-obvious | Evidence that few competitors do this |
| Biggest risk | Technical, market or adoption |
| Build decomposition | Components tagged agent-executable or human-irreducible. Name the constraint. Effort stays `UNCALIBRATED`. |

---

## 5. Phase C: Market value

### C1. Ideal Customer Profile (per pitch where it differs)

| Dimension | Detail |
|---|---|
| Firmographics / demographics | Size, industry, region, tech maturity, regulatory exposure (for B2C: age, occupation, income, device) |
| Persona(s) | Economic buyer, champion and end user, with their KPIs |
| Jobs-to-be-done | Functional, emotional and social jobs |
| Pain triggers | The events that make them look for help now |
| Current alternatives | Tools, VAs or outsourcing, spreadsheets, do nothing |
| Buying process | Self-serve versus sales; who approves; typical cycle |
| Willingness to pay | Evidence from comparables and current spend on alternatives |
| Where they gather | Facebook groups, Viber communities, subreddits, associations, trade events |
| **Anti-ICP** | Who looks like a fit but isn't, and why |
| **PH / SEA lens** | MSME counts (DTI/PSA), IT-BPM workforce (IBPAP), digital-payment adoption (BSP), language needs (Filipino, Taglish, regional languages), price sensitivity; beachhead or later market |

### C2. Competitive market analysis

Cover all four layers:
1. **Direct competitors:** vertical AI apps in the chosen vertical. Find the top 5–10 by funding and traction.
2. **Horizontal agent platforms:** OpenAI (ChatGPT agent, Operator, custom GPTs), Microsoft 365 Copilot and Copilot Studio, Google Gemini for Workspace and Agentspace, Salesforce Agentforce, ServiceNow, Zapier Agents, n8n, Make, Lindy, Relevance AI, Manus, Genspark, Perplexity (Comet / Labs).
3. **Substitutes:** virtual assistants and BPO (including Philippine BPO itself), in-house staff, templates.
4. **Sponsor-adjacent:** NVIDIA AI-Q and blueprints, Nebius Echo, Tavily's customers. Is the pitch complementary to them or competing?

**For each relevant competitor, report:**
- Positioning
- ICP
- Pricing
- Funding and revenue: public figures only
- Model dependency
- Deployment
- Known weaknesses: from reviews and churn complaints

**Then produce:**
- A **feature/positioning matrix** comparing the 3 pitches against the top 8 competitors
- A **2×2 positioning map** whose axes reveal white space
- A **white-space statement**. Is it an unmet need or a graveyard? Look for dead startups in the space and why they died.
- A **"Why won't Microsoft, Google or OpenAI just add this?"** answer for each pitch

### C3. TAM / SAM / SOM

Do **both methods** and reconcile them:
- **Top-down.** Analyst sizing of AI agents, the vertical software market, or the labor pool being automated. Cite each figure and note the variance between analysts.
- **Bottom-up (mandatory for SOM).** Reachable ICP accounts or users × adoption × annual contract value or ARPU.
- **Labor-substitution view `[DERIVED]`.** Number of workers doing the task × share of time × loaded wage. This is useful for AI agents, but treat it as a ceiling, not revenue.

Show every formula and put every assumption in a table.

| Layer | Definition to use |
|---|---|
| TAM | Global annual spend on the job, whoever currently does it (software, labor, outsourcing) |
| SAM | Reachable with this form factor, language, regions and ICP |
| SOM | Realistic 3-year capture. Bottom-up only. |

Also provide:
- Low, base and high sensitivity cases, naming which assumption swings the number most
- A separate **PH/SEA beachhead SOM**
- **Why Now data:** agent adoption curves, open-model cost per task, and enterprise agent-deployment rates

---

## 6. Phase D: Business value

| Area | What to research / produce |
|---|---|
| **Quantified customer value** | Time, cost or error reduction per user, backed by evidence. Include disconfirming data on agent reliability and task-success rates. |
| **Unit economics** | Cost per completed workflow on Token Factory: fetch **current Nemotron Nano, Super and Ultra pricing** and estimate calls and tokens per workflow `[DERIVED]`. Add Tavily cost per search at current pricing and Serverless costs. Compare with a closed-API equivalent. Target gross margin. |
| **Pricing model** | Value-based: per seat, per workflow, per outcome, or tiered. Benchmark against C2. PH affordability check. |
| **Moat / defensibility** | Proprietary workflow data, integrations, vertical know-how, trust, distribution. Rate each Weak, Medium or Strong. |
| **GTM** | First 10 and 100 customers: channel, motion and wedge. Partnerships such as BPOs, associations, accounting firms and banks. |
| **Platform risk** | Horizontal platforms absorbing the feature; model-quality gaps (cite agent benchmarks such as τ-bench, GAIA and BrowseComp); API-access risk from third-party tools |
| **Regulatory / ethical** | PH Data Privacy Act (RA 10173) and NPC rules, GDPR, EU AI Act risk tiers, consumer-protection and sector rules. *Awareness only, not legal advice.* |
| **Business-model viability verdict** | `[INFERENCE]` Venture-scale, lifestyle, or feature-not-a-company |

---

## 7. Phase E: Hackathon value

Score each of the 3 pitches from 1 to 10 on each line below and justify every score.

| Criterion | Pitch 1 | Pitch 2 | Pitch 3 |
|---|---|---|---|
| Stage 1 fit ("someone would actually use") | | | |
| Technological Implementation (tiered Nemotron, Token Factory, Serverless) | | | |
| Design (complete product feel, polish visible in video) | | | |
| Potential Impact | | | |
| Quality of Idea (non-obvious) | | | |
| Tavily bonus eligibility (grounding is load-bearing) | | | |
| Demo-ability | | | |
| Differentiation from likely competing submissions `[INFERENCE]` | | | |

Also report:
- **Likely crowding:** this track will be flooded with generic chat copilots, RAG-over-docs and email agents. Show how each pitch escapes that crowd.
- **Judge-lens read:** what a Token Factory PMM, an Ecosystem product director, and a Tavily forward-deployed engineer would each reward.

---

## 8. Phase F: Decision

1. Build a **weighted decision matrix** with these weights:
   - Problem strength: 30%
   - Market value: 20%
   - Business value: 15%
   - Hackathon value: 35%

   Show the math.
2. **Recommendation** `[INFERENCE]`: one pitch, with the reason, the strongest counter-argument, and what evidence would change the call.
3. **Kill criteria**: three findings that should stop the build.
4. **Open questions**: the primary research needed, such as 5 user interviews and a script for them.
5. **Validation plan**: the cheapest demand tests, such as a landing page, a Facebook group poll, or pre-sales conversations.

---

## 9. Output format

Return a single Markdown report with these sections, in order:
1. Executive Summary (≤250 words)
2. Phase A: Vertical ranking and Problem Screen
3. Phase B: Three Pitches
4. Phase C: Market Value (ICP, Competition, TAM/SAM/SOM)
5. Phase D: Business Value
6. Phase E: Hackathon Scorecard
7. Phase F: Decision Matrix and Recommendation
8. Evidence Register: a table of `# | claim | value | source | tier | pub date | data date | confidence (H/M/L) | flags`
9. Gaps and `NOT FOUND` list
10. Full source list with URLs

Use tables wherever you are comparing things. Every number carries a citation or a `[DERIVED]` or `[ASSUMPTION]` tag.

---

## 10. Source playbook (where to find strong data)

**Big 3 strategy firms (T2; headline sizes are upper bounds)**
- **McKinsey**: *The State of AI*, MGI (the economic potential of generative AI; agentic AI and the future of work), *Technology Trends Outlook*, "Superagency in the workplace"
- **BCG**: *AI at Work*, *AI Radar*, BCG Henderson Institute, "Where's the value in AI?", agentic AI reports
- **Bain**: *Technology Report*, e-Conomy SEA (with Google and Temasek), generative-AI customer-service and SMB research

**Big 4 (T2)**
- **Deloitte**: *State of Generative AI in the Enterprise*, *Tech Trends*, agentic AI predictions (Deloitte TMT Predictions)
- **PwC**: *Global AI Jobs Barometer*, *AI Agent Survey*, CEO Survey, *Sizing the Prize*
- **EY**: *AI Pulse Survey*, *Work Reimagined*
- **KPMG**: *Trust, attitudes and use of AI* (global study with the University of Melbourne), AI Quarterly Pulse (agent adoption)
- Also Tier-2 consulting: Accenture *Technology Vision*, Capgemini Research Institute (agentic AI), IBM Institute for Business Value

**Industry analysts (T2)**
- Gartner: agentic AI predictions (including agent-project cancellation forecasts), Hype Cycle for AI
- IDC: worldwide AI spending guide, agentic AI forecasts
- Forrester: *Predictions: AI*

**Behavioral and usage data (T1/T2)**
- Similarweb and Sensor Tower / data.ai (app traffic and downloads)
- OpenRouter token-share rankings; Artificial Analysis (model and provider speed, price, quality)
- Agent benchmarks: GAIA, τ-bench, BrowseComp, WebArena, OSWorld
- Stanford HAI *AI Index*; Epoch AI
- Microsoft *Work Trend Index*; Anthropic Economic Index; OpenAI usage research; Upwork / Fiverr AI-work reports

**Company and market data (T1/T3)**
- SEC EDGAR filings (Salesforce, ServiceNow, Microsoft, Intuit, Freshworks, Zapier if disclosed)
- Crunchbase, PitchBook, CB Insights (AI agent market maps), Dealroom
- Sacra; The Information
- Menlo Ventures *State of Generative AI in the Enterprise*
- a16z enterprise and consumer AI top-100 lists
- ICONIQ *State of AI*; Retool *State of AI*

**Voice of customer (T4)**
- Reddit (r/smallbusiness, r/Entrepreneur, vertical subreddits), Facebook groups, Hacker News
- G2 and Capterra reviews of competitors; App Store and Google Play reviews; Product Hunt
- Job postings for the manual roles being automated (LinkedIn, JobStreet, OnlineJobs.ph)

**PH / SEA (T1/T2)**
- PSA and DTI (MSME statistics), DICT, IBPAP (IT-BPM size and headcount)
- BSP (digital payments), NPC (privacy), BIR (compliance calendars)
- e-Conomy SEA; ADB and World Bank; Google/Kantar SEA consumer studies

**Hackathon intelligence**
- Past Devpost AI hackathon winner galleries (crowding analysis)
- Nebius docs (Token Factory model catalog and pricing, Serverless), Nemotron model cards (Hugging Face, build.nvidia.com), Tavily docs and pricing

**Validation rule:** Pair every load-bearing claim with one consulting or analyst source (what executives say) and one behavioral or primary source (what users actually do). Report any gap between the two explicitly.

=== PROMPT END ===

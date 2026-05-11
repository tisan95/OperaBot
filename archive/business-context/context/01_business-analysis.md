# Business Analysis: OperaBot

**Operational Knowledge Assistant for Companies**

---

## 📋 Document Metadata

- **Date**: April 2026
- **Project**: OperaBot MVP
- **Scope**: Minimum Viable Product (MVP)
- **Status**: ✅ EXPLORATION → IDEATION → VALIDATION Complete | Ready for Requirements Engineer Handoff
- **BA Version**: 1.0
- **Product Owner**: Santiago Castello Golsalvez

---

## 1. Executive Summary

### 1.1 Problem Statement

Operational teams at small-to-medium enterprises (SMEs) in logistics and manufacturing struggle with **knowledge accessibility**:

- 70-80% of questions to senior experts are repeated.
- Senior experts spend 2-3 hours daily answering the same operational questions.
- Junior employees hesitate to ask repeatedly, fearing they're slowing down the expert.
- Operational knowledge is scattered across documents, outdated wikis, and most critically—**in the heads of a few people**.
- The result: **high onboarding friction, operational slowdowns, and knowledge loss** when key people leave.

### 1.2 Core Insight

**The problem is not lack of information, but lack of accessibility at the moment of action.**

Companies have documentation (procedures, manuals, protocols), but employees don't use it because:
- It's not searchable in their operational language.
- It requires leaving their workflow to navigate multiple systems.
- It's scattered and outdated.

### 1.3 Solution Idea

**OperaBot** is a **B2B SaaS operational knowledge assistant** that makes internal operational knowledge instantly accessible through:
- A **chat interface** for real-time, conversational answers to operational questions.
- A **FAQ browsable interface** for self-service knowledge without chat friction.
- An **admin panel** where operation managers can continuously improve knowledge based on what employees are actually asking.

The product is trained on **real company knowledge** (uploaded documents, admin-authored FAQs) and delivers answers with **confidence signals, sources, and escalation options**—building trust for mission-critical operational decisions.

### 1.4 Expected Impact (MVP Targets)

| Dimension | Target | Notes |
|-----------|--------|-------|
| **Adoption** | 60-70% of invited employees use in first month; 40%+ weekly active | Depth over breadth; focused on pilot companies |
| **Quality** | ≥75% of answers rated helpful; <30% escalations | Trust is the hard gate |
| **Operational** | ~50% reduction in repeated questions; 20-30% faster onboarding | Measurable in pilot companies |
| **Business Viability** | €500-750/month/company; LTV/CAC > 3 long-term | Sustainability proof, not profitability |

---

## 2. Problem Statement (Detailed)

### 2.1 Context

Many SMEs have digitized their processes and use AI, but **operational knowledge remains fragmented and human-dependent**.

- **High coss of expert time**: Senior staff act as "living databases," spending 30-50% of their day answering repetitive questions.
- **Slow onboarding**: New employees take weeks to reach basic autonomy because they must rely on informal knowledge transfer.
- **Operational risk**: When key people leave, their knowledge leaves with them, causing process disruptions and delays.
- **Inconsistent answers**: Different people answer the same question differently, creating confusion and rework.

### 2.2 Research Foundation (Master's Project)

This problem was validated through 15+ interviews with operations teams across logistics and manufacturing companies:

**Key Findings**:

| Finding | Evidence |
|---------|----------|
| Question repetition | 70-80% of questions to experts are identical or very similar |
| Expert saturation | Responsible people spend 2-3 hours/day on repetitive Q&A |
| Knowledge scattering | Docs exist but are outdated, scattered across tools, or only in people's minds |
| Accessibility gap | Employees prefer asking a person over searching docs (faster, safer) |
| Onboarding friction | New hires take 4-8 weeks to reach basic autonomy; many ask the same questions for weeks |
| Fear of asking | Juniors hesitate to ask repeatedly; seniors feel obligated to answer anyway |

### 2.3 Target Market (MVP Phase)

**Geographic Scope**: Primarily Spanish-speaking SMEs (expandable later).

**Industry Focus** (MVP priority):

1. **Logistics & Transport** (warehouses, distribution centers, delivery operations)
2. **Manufacturing** (industrial plants, production lines, assembly operations)

**Why These Segments**:

- High operational load with constant problem-solving (minimal downtime tolerance).
- Cost of mistakes or delays is measurable (€/hour lost, shipments delayed, production stopped).
- Heavy knowledge concentration in senior people.
- Clear ROI from faster problem resolution.

**Company Size** (MVP target):

- **50-250 employees** per company.
- Smaller: pain is too diffuse; larger: sales cycle and integrations too heavy for early stage.

**Buyer Profile**:

- **Decision maker**: Operations Director / Head of Operations.
- **Influencer**: HR Manager (cares about onboarding).
- **User**: Operational employees (warehouse staff, production staff, logistics coordinators).

### 2.4 Market Opportunity

**Addressable Market** (Conservative):
- Spain: ~8,000 SMEs in logistics & manufacturing (50-250 employees).
- EU: ~100,000+ similar companies.

**Willingness to Pay** (from pilot interviews):
- €500-750/month/company is realistic if ROI is clear (20-30% reduction in expert time = €2,000-3,000/month in recovered hours).

---

## 3. Stakeholder Analysis

| Stakeholder | Role | Primary Need | Concern |
|-------------|------|--------------|---------|
| **Operations Director** | Decision Maker / Sponsor | Reduce operational friction; faster problem resolution | ROI clarity; system reliability; data security |
| **HR Manager** | Champion / Co-buyer | Faster onboarding; reduced training dependency | Employee adoption; integration with training |
| **Senior Expert** | Subject Matter Expert & Trainer | More time for strategic work; less repetitive Q&A | Tool adoption; knowledge control; job security fears |
| **Junior/Operational Employee** | Primary User | Fast answers; confidence in decisions | Ease of use; trust in answers; no additional complexity |
| **IT Manager** | Technical Gatekeeper | Security; integration compatibility | Data security; API stability; compliance |

---

## 4. Users & Target Groups

### 4.1 User Personas

#### Persona 1: **Carlos — Operational Junior**

**Demographics**:
- Age: 22-28, recently hired (0-2 years in role).
- Role: Production operator, warehouse associate, logistics coordinator.
- Tech comfort: Moderate; comfortable with messaging apps and basic software, but not power users.
- Context: Works on the shop floor or in the warehouse; constant operational problems to solve.

**Needs**:
- **Functional**: "I need answers to 'how do I do X' without being afraid to ask the same thing twice."
- **Emotional**: "I want to feel confident that I'm doing things right and not slowing down the team."
- **Social**: "I want to be seen as capable and independent, not as the junior who always asks."

**Frustrations**:
- Senior experts get annoyed after the 3rd repetitive question.
- Documentation exists but is hard to find or outdated.
- Asking takes time; doing it wrong takes more time.

**Current Behavior**:
- Asks colleague or expert in person (slowest but safest).
- Tries to search company wiki/shared drive (often unsuccessful).
- Eventually asks the same person multiple times (creates friction).

**How OperaBot Helps**:
- Instant, judgment-free answers to operational questions.
- Builds confidence through "why" explanations, not just steps.
- Shows sources so he knows it's official.
- Escalation button if he's still unsure → human expert validates.

---

#### Persona 2: **Laura — Expert Saturated**

**Demographics**:
- Age: 35-45, 10+ years in role, senior/specialist.
- Role: Senior operator, shift supervisor, process owner.
- Tech comfort: Moderate; uses company systems daily but not tech-focused.
- Context: Responsible for training, process quality, and answering questions.

**Needs**:
- **Functional**: "I need to spend less time on repetitive answers and more time on improving processes."
- **Emotional**: "I want to be valued for expertise and strategic thinking, not just as a walking FAQ."
- **Social**: "I want to be seen as a leader and mentor, not as an answering service."

**Frustrations**:
- 2-3 hours/day spent answering the same questions (real time cost).
- Documentation is outdated or juniors don't know it exists.
- No data on "what questions do we keep repeating?"—hard to prioritize improvements.
- New procedures don't get documented until someone asks again.

**Current Behavior**:
- Answers verbally, tries to explain reasoning.
- Occasionally points to docs (but often those docs are outdated).
- Frustrated with repetition but feels obligated to help.

**How OperaBot Helps**:
- Handles 70-80% of repetitive questions → frees time for strategic work.
- Admin panel shows "top questions," "low-quality answers," "missing docs" → data-driven improvement.
- Can improve answers directly; controls what the bot knows.
- Becomes a "knowledge curator" instead of an answering machine.

---

#### Persona 3: **Miguel — Operations Director**

**Demographics**:
- Age: 40-50, 15+ years in operations, decision-making authority.
- Role: Operations Director / Head of Operations.
- Tech comfort: High-level strategic thinker; less hands-on with tools.
- Context: Responsible for efficiency, cost, and team development.

**Needs**:
- **Functional**: "I need faster decision-making, less downtime, and better knowledge retention."
- **Emotional**: "I want to feel that my team is competent and stable, not dependent on one or two people."
- **Social**: "I want to lead a data-driven team that continuously improves."

**Frustrations**:
- Knowledge loss when senior people leave (expensive and risky).
- Onboarding new hires is slow → delays in capacity.
- Bottleneck: everything goes through 1-2 senior people.
- No visibility into "what knowledge gaps are causing delays?"

**Current Behavior**:
- Tries to enforce documentation (often fails; people don't keep it updated).
- Invests in training programs (expensive, slow ROI).
- Hopes senior people don't leave; plans expensive knowledge transfer if they do.

**How OperaBot Helps**:
- Reduces operational bottleneck → less dependent on one person.
- Faster onboarding → new hires productive in weeks, not months.
- Analytics show "what questions are being asked" → data for process improvement.
- Kanban integration → insights directly become improvement tasks.
- Clear ROI: time saved = reduced overtime, faster delivery, better team stability.

---

### 4.2 Jobs to Be Done (Jobs-to-be-Done Framework)

#### **Functional Jobs**

| Job | Current Solution | Pain | OperaBot Solution |
|-----|------------------|------|-------------------|
| **"Quickly answer an operational question I don't know how to handle"** | Ask a senior expert (2-5 min wait, context switch for expert) | Interrupts expert's work; delays for questioner | Chat answer in <30 sec; sources included |
| **"Find a procedure or manual for something I need to do"** | Search company wiki/shared drive (5-10 min, often unsuccessful) | Docs are outdated or poorly indexed | FAQ browse + semantic search (1-2 min) |
| **"Learn how to do a new task as a new employee"** | Mentor walks me through it (days of pairing, expert time) | Slow; dependent on one mentor availability | Self-serve FAQ + chat for edge cases (hours) |
| **"Know if my answer is right or if I should escalate to a person"** | Try something and see if it breaks (risky) | High cost of mistakes | Bot shows confidence + escalation button |

#### **Emotional Jobs**

| Job | Current Solution | Pain | OperaBot Solution |
|-----|------------------|------|-------------------|
| **"Feel confident I'm doing the right thing"** | Ask an expert (feel safe but dependent) | Fear of messing up; anxiety of asking too much | Clear procedures + sources build confidence |
| **"Feel respected and not annoying"** | Don't ask (risky) or ask reluctantly | Isolation; silent struggle | Judgment-free bot answers anytime |
| **"Feel like I'm learning and growing"** | Pair with expert; read docs (slow) | Frustration with repetitive learning; feel stuck | Self-serve knowledge builds autonomy feeling |

#### **Social Jobs**

| Job | Current Solution | Pain | OperaBot Solution |
|-----|------------------|------|-------------------|
| **"Be seen as competent by my team"** | Ask for help (looks unprepared) | Fear of looking junior or incompetent | Using bot privately = competent appearance |
| **"Be seen as a leader/expert by the team"** | Provide answers (exhausting) | Overloaded; can't focus on real strategy | Bot handles routine Q&A → focus on leadership |

---

## 5. Needs & Insights Analysis

### 5.1 Functional Needs (Typed & Prioritized)

#### **High Priority**

1. **Real-time access to operational procedures** (P0)
   - Users need to access procedures exactly when they're doing the task.
   - Current friction: navigation, search, outdated content.
   - Insight: "If I have to switch tools or wait, I'm already searching Google instead."

2. **Answers with confidence signals** (P0)
   - Operational answers must include "I'm 85% sure" or "I'm only 30% confident."
   - Current friction: AI answers sound confident even when they're wrong; risky in operations.
   - Insight: "In operations, a wrong answer is expensive; I need to know when to escalate to a person."

3. **Fast onboarding for new employees** (P1)
   - New hires need to reach basic autonomy in weeks, not months.
   - Current friction: depends on mentor availability; inconsistent knowledge transfer.
   - Insight: "We can't hire 10 people if each takes 2 months to train due to expert bottleneck."

4. **Expert relief from repetitive Q&A** (P1)
   - Senior staff need to stop answering "how do I X?" 100 times/month.
   - Current friction: expected to answer; no alternative.
   - Insight: "If we don't free experts, they burn out or leave, and we lose everything."

#### **Medium Priority**

5. **Data on "what are people actually asking?"** (P2)
   - Ops managers need visibility into knowledge gaps.
   - Current friction: no systematic tracking of repeated questions.
   - Insight: "We fix problems reactively; we need data to fix them proactively."

6. **Integration with improvement processes** (P2)
   - Admin must convert "people ask about X often" into "create/update procedure X" tasks.
   - Current friction: insights don't flow into action; improvements are ad-hoc.
   - Insight: "Knowledge must evolve with reality; static docs die."

### 5.2 Emotional Needs (Typed & Prioritized)

| Need | Why It Matters | Insight |
|------|-----------------|---------|
| **Trust in the system** (P0) | If I don't trust the bot's answers, I won't use it; I'll keep asking people. | "I need to know the answer came from our internal docs, not the internet." |
| **Psychological safety** (P0) | If asking feels risky (might annoy someone), I won't ask the bot either; I'll guess. | "I need to feel OK not knowing; asking should feel safe." |
| **Autonomy & competence** (P1) | Juniors want to feel capable, not dependent. | "Using the bot should feel like I'm learning, not like I'm lost." |
| **Respect from peers** (P1) | Asking questions in front of teammates feels risky. | "The bot should help me look competent, not reveal my gaps." |

### 5.3 Social Needs (Typed & Prioritized)

| Need | Why It Matters | Insight |
|------|-----------------|---------|
| **Collective knowledge ownership** (P1) | Experts feel alone; team feels dependent. | "Knowledge should belong to the team, not to one person." |
| **Distributed expertise** (P1) | Bottlenecks form around key people; this is fragile. | "Anyone should be able to answer 'how do I X' without finding the expert." |
| **Continuous improvement culture** (P2) | Orgs that learn from what they do improve faster. | "Every question should teach us something; we should evolve from questions." |

---

## 6. Current Process & Pain Points

### 6.1 "How do I solve this operational problem?" Workflow Today

```
User has problem
    ↓
Option 1: Ask expert (fastest but interrupts them; expert annoyed)
    ↓
Option 2: Search docs (slow; docs outdated; search is bad)
    ↓
Option 3: Guess / try (risky; can break things)
    ↓
Get answer (inconsistent; depends on who you ask)
    ↓
Expert spends 2-3 hours/day on this; user feels bad for asking; docs don't improve
```

**Pain Points**:
- ❌ No systematic way to find answers without interrupting someone.
- ❌ Documents are outdated and unstructured.
- ❌ No feedback loop: questions don't improve docs.
- ❌ Expert knowledge is invisible; when they leave, it vanishes.
- ❌ Onboarding is slow because it relies on 1:1 knowledge transfer.

### 6.2 "Improve operational processes" Workflow Today

```
Expert notices problem / user asks same question 3 times
    ↓
Expert writes a procedure (if they have time)
    ↓
Procedure is uploaded to shared drive or wiki
    ↓
Nobody knows it exists or where it is
    ↓
Same question is asked again in 2 weeks
    ↓
Continuous fire-fighting; no systematic improvement
```

**Pain Points**:
- ❌ Insights are anecdotal, not data-driven.
- ❌ No visibility into "which knowledge gaps are costing us the most?"
- ❌ Improvements are sporadic; docs decay over time.
- ❌ Kanban / task boards exist separately; insights don't flow into action.

---

## 7. Market & Competitive Analysis

### 7.1 Competitive Landscape

| Competitor | Segment | Strengths | Weaknesses vs OperaBot |
|------------|---------|-----------|------------------------|
| **Generic LLMs** (ChatGPT, Gemini) | Broad AI | General knowledge; advanced reasoning | No company knowledge; not operational; not trustworthy for procedures |
| **Knowledge Management** (Confluence, Notion, Guru) | Doc-centric | Structured docs; searchable | Requires active curation; people don't find things; no conversational interface |
| **Retro Tools** (Parabol, FunRetro, Miro) | Retrospectives | Good for reflection; structured feedback | Different use case (periodic, not daily); not for execution |
| **Specialized HR** (Workday, SuccessFactors) | HR-centric | Integration with payroll/benefits | Not designed for operational Q&A; heavy on admin; expensive |
| **Custom Chatbots** (internal implementations) | Ad-hoc | Tailored to company | Expensive to build/maintain; not a product; no SaaS model |

### 7.2 OperaBot's Differentiation

| Dimension | OperaBot | Generic AI | Knowledge Mgmt |
|-----------|----------|------------|-----------------|
| **Knowledge Source** | Company's internal docs + FAQs | Internet (Wikipedia, blogs) | Company docs (but passive) |
| **Interface** | Chat + FAQ + Admin improvements | Chat only | Wiki/browse only |
| **Use Case** | Day-to-day operational problem-solving | General questions | Reference lookup |
| **Trust Signals** | Sources, confidence, escalation | None; sounds confident | Document-level credibility |
| **Feedback Loop** | Analytics + kanban integration | None | Manual doc updates |
| **Operational Focus** | "How do I do my job right now?" | "What's the answer to anything?" | "Where is the procedure?" |
| **Target Users** | Shop floor, operations staff | Everyone | Knowledge workers |

### 7.3 "The Wow" (Unique Value)

**"The operational knowledge of your company becomes instantly accessible in the exact moment of action—in the language your team speaks, with confidence signals and sources—and every question teaches you what knowledge you're missing."**

This is unique because:
1. Generic AI can't answer about your company's specific machines, protocols, language.
2. Knowledge management requires active seeking; OperaBot comes to the user.
3. No competitors combine instant access + trust signals + improvement loop.

---

## 8. Solution Idea & MVP Scope

### 8.1 OperaBot Core Concept

**OperaBot is a B2B SaaS operational knowledge assistant** that helps SMEs in logistics and manufacturing make operational decisions faster, with less expert dependency.

**Three Interfaces**:

1. **Chat** (Real-time Q&A)
   - User asks a question in natural language.
   - Bot searches company knowledge + retrieves relevant docs.
   - Bot answers with: steps + sources + confidence level + escalation option.

2. **FAQ Browser** (Self-serve Reference)
   - User browses or searches procedures by category.
   - Structured knowledge without chat friction.
   - Same source of truth as chat (no duplication).

3. **Admin Panel** (Knowledge Management + Analytics)
   - Admin creates, edits, archives FAQ articles.
   - Upload documents (PDFs, Word, text).
   - View analytics: top questions, low-rated answers, confidence gaps.
   - Create tasks in external kanban board from insights.

### 8.2 MVP Scope (Clear In/Out)

#### **IN (Must Have)**

**Functional**:
- User authentication (login) + two roles (User, Admin).
- Chat interface with natural language Q&A.
- FAQ browser with search + category navigation.
- Answer rating (helpful / not helpful).
- Escalation button (user can request human follow-up).
- Admin panel: create/edit/delete FAQ articles.
- Document upload: PDF, Word, plain text.
- Admin analytics:
  - Top questions (volume).
  - Low-quality answers (negative ratings).
  - Unanswered questions.
- Kanban integration: button to create task in external board (e.g., Trello, Linear).

**Non-Functional**:
- Multi-tenant SaaS (one database, isolated per company).
- Vector embeddings + semantic search (RAG architecture).
- Low-cost LLM (Gemini/Anthropic free tier or similar).
- Hosting: cloud-based (AWS/GCP/Azure), no on-premise for MVP.
- Security: basic (TLS, password hashing); not SOC2-ready.

#### **OUT (Nice to Have / Future)**

- ❌ Private tenant/VPC options (later, for large customers).
- ❌ Advanced roles (department-based permissions).
- ❌ Integrations with ERPs, HR systems, wikis.
- ❌ Mobile app (web-responsive only for MVP).
- ❌ Advanced analytics dashboards (basic dashboards only).
- ❌ Self-hosted LLM options.
- ❌ Multi-language support for UI (Spanish MVP, English later).
- ❌ Audio/voice interface.
- ❌ Feedback loop to retrain models (manual data review only).

#### **Explicit Out-of-Scope Assumptions**

1. We assume companies are willing to trust SaaS with operational docs (with standard security).
2. We assume low-cost LLMs are "good enough" when combined with good RAG.
3. We assume employees prefer the bot once they see it works (adoption will follow quality).
4. We assume the pain in logistics + manufacturing SMEs is strong enough to pay €500-750/month.

---

## 9. Value Proposition

### 9.1 One-Liner

**"Give your operations team instant access to operational knowledge, without overloading your experts—and learn where your knowledge is missing."**

### 9.2 Extended Value Prop

**For Operations Directors**:
- Reduce bottleneck: operational knowledge is no longer trapped in one person.
- Faster onboarding: new hires reach basic autonomy in weeks, not months.
- Data-driven improvement: see exactly what your team is asking → prioritize knowledge gaps.
- Lower risk: knowledge doesn't vanish when key people leave.

**For Senior Experts**:
- Reclaim 2-3 hours/day from repetitive Q&A.
- Become a "knowledge curator" instead of a walking FAQ.
- Build scalable expertise: let your knowledge help 50 people at once, not one at a time.

**For Operational Employees**:
- Get answers instantly, anytime, without fear of annoying someone.
- Feel confident you're doing things right (sources + confidence signals).
- Learn faster: onboarding goes from months to weeks.

### 9.3 Competitive Positioning

| Aspect | OperaBot | Generic AI | Knowledge Base |
|--------|----------|-----------|-----------------|
| **Answers based on** | Your company's knowledge | Internet | Your company's docs |
| **Speed to answer** | <30 sec | <30 sec | 5-10 min (if you find it) |
| **Trust in answer** | High (from your docs) | Low (generic) | High (but scattered) |
| **Reduces expert load** | 70-80% of questions | 0% (still need expert) | 20-30% (people don't use) |
| **Improves over time** | Yes (analytics → tasks) | No | Slowly (manual updates) |

---

## 10. Idea Potential (3-Axis Evaluation)

### 10.1 Desirability (Does the market want this?)

**Score: 8/10** ✅

**Evidence**:
- 15+ interviews in target segment confirmed pain (70-80% repetitive questions).
- All interviewed Operations Directors identified expert bottleneck as a cost problem.
- Willingness to pay: €500-750/month is realistic if ROI is shown.
- Market size: 8,000+ SMEs in Spain alone in target segments.

**Risks**:
- Market might prefer cheaper generic solutions over specialized product.
- Some companies may resist centralizing knowledge in SaaS (data security concern).

### 10.2 Feasibility (Can we build this?)

**Score: 7/10** ✅

**Feasibility By Component**:

| Component | Feasibility | Notes |
|-----------|-------------|-------|
| **User Auth + Roles** | 10/10 ✅ | Standard tech; well-established patterns |
| **Chat Interface** | 8/10 | Standard LLM + retrieval; straightforward |
| **RAG (Vector Search)** | 7/10 | Embedding models are commodity; might need tuning |
| **FAQ Browser** | 10/10 | Standard CRUD + search |
| **Document Upload** | 7/10 | PDF/Word parsing is standard but needs testing |
| **Admin Dashboard** | 8/10 | Standard analytics; straightforward |
| **Kanban Integration** | 8/10 | Trello/Linear APIs are well-documented |
| **Multi-Tenancy** | 6/10 | Requires careful data isolation; doable but not trivial |
| **Cost-Effective LLM** | 7/10 | Dependent on model quality; may need fallback if results are poor |

**Critical Risks**:
- If low-cost LLM quality is insufficient (Hypothesis H2), we'd need expensive models → high cost per company.
- Document parsing (PDFs, Word) can be brittle; might need manual intervention.
- RAG quality depends on retrieval + LLM combo; needs tuning.

### 10.3 Viability (Can we make money?)

**Score: 7/10** ✅

**Business Model**:
- **Subscription**: €500-750/month per company.
- **Target**: 10-20 paying customers by end of Year 2 → €60K-180K MRR → sustainable.
- **Unit Economics** (rough estimate):
  - LLM cost per company: ~€10-20/month (low-cost API).
  - Infrastructure: ~€5-10/month (cloud).
  - Other variable costs: ~€5-10/month.
  - Gross margin: ~95%.
  - Payback period: 1-2 months (if customer lifetime = 2 years, LTV/CAC > 10).

**Risks**:
- Customer acquisition cost (CAC) is unknown; sales to operations directors may be slower than expected.
- Churn risk if product doesn't deliver (quality must be high).
- LLM costs could rise if we need a better model → compress margin.

**Viability Conclusion**: 
- **MVP is viable** to validate hypotheses at low cost.
- **Scale is viable** if 20+ customers can be acquired and retained.
- **Critical**: must prove Hypothesis H1 (companies trust SaaS) and H2 (LLM quality is acceptable).

---

## 11. Critical Hypotheses (What Must Be True)

These are the "bets" underpinning OperaBot. If any of these turn out false, the product needs a major pivot.

### 11.1 Hypothesis H1: Trust in SaaS with Operational Knowledge

**Hypothesis**: "Companies will trust a SaaS platform with their internal operational knowledge under reasonable security and data protection guarantees."

**Why It's Critical**: If companies systematically refuse to upload docs or centralize knowledge in a SaaS, OperaBot has no knowledge base and cannot function.

**How to Test** (MVP Phase):
1. **Pilot interviews** (before build): Ask 5 target ops directors: "Would you trust a SaaS tool with your operational docs under SOC2/GDPR?"
2. **Pilot deployment** (after MVP): Deploy to 2-3 pilot companies; measure actual adoption of document upload.
3. **Success Criterion**: ≥80% of pilot companies upload >50 pages of operational docs within 1 month.

**If This Fails**:
- Pivot to on-premise or private VPC offerings (expensive, slower to deploy).
- Reposition as "knowledge compilation tool" (companies use it, then export docs).
- Abandon SaaS model → loss of core business model.

---

### 11.2 Hypothesis H2: Low-Cost LLMs Are Good Enough (With RAG)

**Hypothesis**: "A low-cost or mid-tier LLM combined with solid RAG (retrieval-augmented generation) can deliver operational answers at ≥75% quality for the target segment."

**Why It's Critical**: If cheap models are too unreliable, we'd need expensive models (GPT-4, Claude) → cost per customer becomes prohibitive → no margin.

**How to Test** (MVP Phase):
1. **Pre-MVP spike** (2-3 weeks): Build a small PoC with actual company docs; test Gemini free + Claude free tier.
2. **Measure accuracy** on 100+ real operational questions from pilot companies.
3. **Success Criterion**: ≥75% of answers rated ≥4/5 (helpful) by operational users in pilot.

**If This Fails**:
- Use expensive models (e.g., GPT-4) → margin compressed; raises price to €1,500-2,000/month.
- Pivot to "assisted AI" model (human expert reviews answers before users see them) → slower, defeats purpose.
- Reconsider product positioning (e.g., "knowledge compilation tool" instead of chat-first).

---

### 11.3 Hypothesis H3: Users Adopt Bot Over Asking Humans

**Hypothesis**: "Operational users (especially juniors) will prefer asking the bot over asking a person once they see it works reliably."

**Why It's Critical**: If users keep preferring human experts (due to trust, habit, or social reasons), adoption collapses regardless of quality.

**How to Test** (MVP Phase):
1. **Pilot rollout**: Deploy to 2-3 companies; track usage metrics daily.
2. **Measure adoption**: Target = 60-70% of users try it in first month; 40%+ use weekly.
3. **Measure displacement**: Track reduction in questions to experts (via survey or logs).
4. **Success Criterion**: ≥40% of questions are answered by bot (not human) after 4 weeks.

**If This Fails**:
- Users perceive bot as a "training wheel," not a replacement.
- May indicate quality issues (test H2 first) or trust issues (test H1).
- Could pivot to "expert augmentation" (bot helps experts answer faster) vs. "self-service."

---

### 11.4 Hypothesis H4: Pain Is Strong Enough in Target Market

**Hypothesis**: "The pain of operational inefficiency in logistics & manufacturing SMEs (50-250 employees) is strong enough that ops directors are willing to pay €500-750/month and invest in implementation."

**Why It's Critical**: If ops directors don't see clear ROI, they won't buy—regardless of product quality.

**How to Test** (MVP Phase):
1. **Pilot pricing**: Deploy to 2-3 companies at €500-750/month (or discounted for pilots).
2. **Measure ROI**: Track metrics (questions to experts, onboarding time, expert time freed) before/after.
3. **Conduct interviews**: After 3 months, ask: "Would you renew at full price? Why?"
4. **Success Criterion**: ≥80% of pilots show measurable cost savings ≥€2,000/month; ≥60% express intent to renew.

**If This Fails**:
- Pain might be weaker than expected in this segment.
- Pivot to larger companies (more budget, more pain) or different segments.
- Reconsider pricing or positioning.

---

### 11.5 Hypothesis H5: Knowledge Will Improve Over Time

**Hypothesis**: "By tracking what users ask and how they rate answers, we can systematically improve the knowledge base—and this improvement loop will be visibly valuable to ops directors."

**Why It's Critical**: If the knowledge base doesn't improve over time, answers get stale, adoption falls, churn rises.

**How to Test** (MVP Phase):
1. **Track feedback**: Measure % of questions that are initially low-rated, then improved after admin updates.
2. **Conduct interviews**: After 3 months, ask admins: "Did the analytics help you improve docs? How?"
3. **Success Criterion**: ≥50% of low-rated answers are improved within 2 weeks; admins report ≥1 improvement per week per admin.

**If This Fails**:
- Admins aren't using the analytics or aren't motivated to update docs.
- Might need better incentives or UX for admins.
- Could fall back to "point-in-time knowledge base" (less valuable but simpler).

---

## 12. How Might We? (HMW Questions)

These questions bridge EXPLORATION (what's the problem?) to IDEATION (how do we solve it?):

1. **How might we help junior operators feel confident making decisions without asking a senior each time?**
   - Answer: Provide instant, sourced, confidence-rated answers.

2. **How might we reduce the expert bottleneck without hiring more experts?**
   - Answer: Automate 70-80% of repetitive Q&A through chat.

3. **How might we make operational documentation useful instead of a dead artifact?**
   - Answer: Connect docs to real questions + create a feedback loop (questions → improve docs).

4. **How might we help ops directors see the real cost of knowledge gaps and prioritize fixes?**
   - Answer: Analytics on "top unanswered questions" + kanban integration to create tasks.

5. **How might we design for non-technical users (shop floor staff) to prefer a bot over asking people?**
   - Answer: Conversational chat, no jargon, confidence signals, escalation option.

6. **How might we build trust in AI answers for mission-critical operations?**
   - Answer: Show sources + confidence levels + allow escalation to human expert.

---

## 13. Success Metrics & KPIs

### 13.1 Adoption Metrics (Usage)

**Primary** (MVP Phase):

| Metric | Target | Measurement | Success Criterion |
|--------|--------|-------------|-------------------|
| **Monthly Active Users (%)** | 60-70% | % of invited employees who use OperaBot at least once in first month | ≥60% = on track |
| **Weekly Active Users (%)** | 40%+ | % of users who use ≥1-2 queries/week after first month | ≥40% = sustainable adoption |
| **Average Queries/User/Week** | 2-3 | Queries per active user | ≥2 queries/week = embedding in workflow |

**Secondary**:

| Metric | Notes |
|--------|-------|
| **FAQ vs Chat** | Track which interface users prefer; goal = ~60% chat, ~40% FAQ |
| **Return Rate** | % of users who return after first week (proxy for stickiness) |
| **Time-to-First-Use** | How long from onboarding to first query (should be <1 day) |

---

### 13.2 Quality Metrics (Trust & Reliability)

**Primary** (MVP Phase):

| Metric | Target | Measurement | Success Criterion |
|--------|--------|-------------|-------------------|
| **Helpful Rating (%)** | ≥75% | % of user ratings that are 4-5/5 or "helpful" | ≥75% = acceptable quality |
| **Escalation Rate (%)** | <30% | % of questions where user clicks "escalate to human" | <30% = bot handles most |
| **Negative Ratings (%)** | <25% | % of user ratings that are 1-2/5 or "not helpful" | <25% = acceptable |

**Secondary**:

| Metric | Notes |
|--------|-------|
| **Answer Latency** | Avg response time (should be <5 sec for good UX) |
| **Confidence Calibration** | % of bot answers marked high confidence that are actually rated helpful (should be high) |
| **Escalation-to-Resolution** | % of escalations that are resolved + user is satisfied |

---

### 13.3 Business Impact Metrics (Operational)

**Primary** (MVP Phase):

| Metric | Target | Measurement | Success Criterion |
|--------|--------|-------------|-------------------|
| **Questions to Experts (Reduction)** | -50% | % reduction in repeated questions to senior staff | Baseline vs 4 weeks = -50% reduction |
| **Onboarding Time (Reduction)** | -20 to -30% | Days to basic autonomy for new hires | Baseline (e.g., 45 days) vs 30-40 days |
| **Expert Time Freed (Hours/Week)** | +10 to +15 hours | Hours/week that senior staff save | Via survey: "How much time did you save?" |

**Secondary**:

| Metric | Notes |
|--------|-------|
| **Documentation Completeness** | Before/after % of operational procedures documented |
| **Error Rate** | If measurable: % reduction in operational mistakes |
| **Turnover Impact** | Long-term: does knowledge retention improve? |

---

### 13.4 Business Viability Metrics

**Primary** (MVP Phase):

| Metric | Target | Measurement | Success Criterion |
|--------|--------|-------------|-------------------|
| **Customer Satisfaction (NPS)** | ≥50 | Pilot companies rated on willingness to recommend | ≥50 NPS = strong product-market fit signal |
| **Renewal Intent** | ≥60% | % of pilots that express intent to pay & renew | ≥60% = viable business model |
| **ROI Clarity** | ≥€2,000/month | Measured cost savings per company | ≥€2,000/month = justifies €500-750 price |

**Secondary**:

| Metric | Notes |
|--------|-------|
| **LLM Cost per Company** | Should stay <€20/month |
| **Implementation Effort** | Hours to onboard one company (goal: <40h) |
| **Churn Rate** | Track early (month 1-3) to identify issues |

---

## 14. Scope: In-Scope vs Out-of-Scope

### 14.1 In-Scope (MVP Must-Haves)

**Product Features**:
- ✅ User authentication (email/password login).
- ✅ Chat interface with natural language Q&A.
- ✅ FAQ browsable interface (search + categories).
- ✅ Document upload (PDF, Word, plain text).
- ✅ Admin panel: create/edit/delete FAQs.
- ✅ Admin analytics: top questions, low ratings, unanswered.
- ✅ Answer rating (helpful/not helpful).
- ✅ Escalation button (request human follow-up).
- ✅ Kanban integration (create task from insights).

**Architecture**:
- ✅ Multi-tenant SaaS (isolated per company).
- ✅ RAG with vector embeddings + semantic search.
- ✅ Low-cost LLM (Gemini free tier or similar).
- ✅ Cloud hosting (AWS/GCP/Azure).
- ✅ Basic security (TLS, password hashing, SQL injection prevention).

**Target Users**:
- ✅ Operations staff (shop floor, logistics, production).
- ✅ Operations directors (ops manager / admin).
- ✅ Initially: Spanish language UI.

**Target Companies**:
- ✅ Logistics & manufacturing SMEs (50-250 employees).
- ✅ Spain (expandable later).

---

### 14.2 Out-of-Scope (Future Phases)

**Product Features** (Phase 2+):
- ❌ Advanced roles (department-based permissions).
- ❌ Private tenant / VPC options (for large customers).
- ❌ Mobile app (web-responsive only).
- ❌ Advanced dashboards (budget view, ROI dashboards).
- ❌ Audio/voice interface.
- ❌ Integration with ERP, HR, Wiki systems.
- ❌ Automatic model retraining from feedback.

**Architecture**:
- ❌ Self-hosted LLM (will support later, not MVP).
- ❌ On-premise deployment (later if demanded).
- ❌ HIPAA / SOC2 compliance (basic compliance only).

**Geo / Languages**:
- ❌ English UI (Phase 2).
- ❌ Other languages (Phase 2+).
- ❌ Other markets/industries (after logistics+manufacturing validated).

**Business Model**:
- ❌ Custom integrations (standard APIs only).
- ❌ Professional services (self-serve onboarding in MVP).
- ❌ White-label / reseller model (direct sales only).

---

## 15. Assumptions & Dependencies

### 15.1 Key Assumptions

| Assumption | Impact | Validation Method |
|-----------|--------|-------------------|
| **Companies trust SaaS with ops docs** | H1 - Core; affects whether model works at all | Pilot interviews before build + actual uploads in pilots |
| **Low-cost LLM quality is sufficient** | H2 - Core; affects margin and viability | PoC + pilot quality metrics |
| **Users prefer bot over asking people** | H3 - Core; affects adoption | Pilot usage metrics + displacement tracking |
| **Pain is strong in target segment** | H4 - Core; affects sales and retention | Pilot NPS + renewal intent + ROI measurement |
| **Improvement loop works** | H5 - Important; affects stickiness | Analytics adoption + improvement frequency |
| **Document parsing is reliable** | Technical; affects quality | PoC + pilot data quality testing |
| **Vector search is good enough** | Technical; affects retrieval quality | PoC relevance metrics |
| **Multi-tenancy can be implemented safely** | Technical; affects security | Architecture review + penetration testing |

### 15.2 External Dependencies

| Dependency | Risk | Mitigation |
|-----------|------|-----------|
| **LLM API availability** (Gemini, Anthropic, etc.) | Medium | Have fallback LLM provider; can switch with 2-3 days notice |
| **Vector DB service** (Pinecone, Weaviate, etc.) | Medium | Use managed service; data can be exported if needed |
| **Cloud hosting provider** (AWS, GCP, Azure) | Low | Abstracted through terraform; can migrate with ~2 weeks notice |
| **Kanban API** (Trello, Linear, Jira) | Low | Start with one provider (e.g., Linear free); add others later |

---

## 16. Constraints

### 16.1 Technical Constraints

| Constraint | Reason | Impact |
|-----------|--------|--------|
| **No on-premise for MVP** | Deployment + maintenance complexity | Companies must accept SaaS; blocks some conservative orgs |
| **Basic security only** | Time/cost; can upgrade later | Not suitable for highly regulated industries (finance, healthcare) yet |
| **Single LLM provider** | Cost control | If provider has issues, product is down; need fallback eventually |
| **English + Spanish UI only (MVP)** | Language translation effort | Limits market to ES-speaking countries; EU expansion is Phase 2 |

### 16.2 Business Constraints

| Constraint | Reason | Impact |
|-----------|--------|--------|
| **Target SMEs (50-250 people)** | Too small = weak pain; too large = complex sales | Limits addressable market; requires focused GTM |
| **€500-750/month price** | Cost structure forces this range | If LLM costs rise, margin is compressed; need usage-based pricing later |
| **2-3 pilot companies (Phase 1)** | Limited resources; focus over scale | Slow revenue ramp; need venture/bootstrap funding |
| **MVP in 4-6 months** | Time to validate hypotheses quickly | No time for "nice to have" features; ruthless prioritization |

---

## 17. Next Steps & Handoff to Requirements Engineer

### 17.1 BA Complete ✅

This Business Analysis document includes:
- ✅ Problem statement (70-80% repeated questions, expert saturation, slow onboarding).
- ✅ Target market (logistics + manufacturing SMEs, 50-250 people, Spain).
- ✅ User personas (Carlos, Laura, Miguel) with Jobs-to-be-Done.
- ✅ Needs analysis (functional, emotional, social; prioritized).
- ✅ Competitive landscape + differentiation.
- ✅ Solution idea + MVP scope (chat, FAQ, admin, kanban).
- ✅ Value proposition + idea potential (8/10 desirability, 7/10 feasibility, 7/10 viability).
- ✅ 5 critical hypotheses with test methods.
- ✅ Success metrics (adoption, quality, business impact).
- ✅ Clear scope (in/out) and constraints.

---

### 17.2 Handoff to Requirements Engineer

**The Requirements Engineer should now:**

1. **Create Epics** based on Solution Idea (Section 8):
   - Epic 1: Chat Interface (Q&A with sources + confidence).
   - Epic 2: FAQ Browser (self-serve knowledge).
   - Epic 3: Knowledge Management (admin panel).
   - Epic 4: Analytics & Improvement (insights → kanban).
   - Epic 5: Authentication & Multi-tenancy (infrastructure).

2. **Derive User Stories** from Personas + Jobs-to-be-Done:
   - Functional user stories (Carlos: "As a junior, I want to ask the chat a question and get steps").
   - Emotional user stories (Laura: "As an expert, I want to understand what my team keeps asking").
   - Social user stories (Miguel: "As an ops director, I want to see if knowledge gaps are costing us").

3. **Define Feature-level Non-Functional Requirements** (NFRs):
   - Performance: Response time <5 sec for chat, search <2 sec.
   - Security: Basic TLS, password hashing, SQL injection prevention.
   - Scalability: Support 10 concurrent companies in MVP; 100 queries/minute per company.
   - Availability: 99.5% uptime (can be relaxed for MVP).

4. **Create Acceptance Criteria** linked to Success Metrics:
   - "Chat answers must be rated ≥75% helpful" (→ Quality Metric).
   - "At least 60-70% of employees must use in first month" (→ Adoption Metric).
   - "Escalation rate must stay <30%" (→ Trust Metric).

5. **Map Critical Hypotheses to Features** (H1-H5):
   - H1 (Trust in SaaS) → Feature: Security design + compliance docs.
   - H2 (LLM quality) → Feature: RAG quality + confidence signals.
   - H3 (User adoption) → Feature: UX design + onboarding.
   - H4 (ROI clarity) → Feature: Analytics dashboard.
   - H5 (Knowledge improvement) → Feature: Feedback loop + kanban integration.

---

### 17.3 Questions for Requirements Engineer

The following clarifications may be needed during requirements phase:

1. **LLM Selection**: Which provider should we prioritize for MVP (Gemini, Anthropic, LocalAI)?
2. **Knowledge Schema**: What metadata should FAQs have beyond title/content? (department, machine type, urgency, etc.)
3. **Authentication**: Should MVP support SSO (SAML/OAuth) or just email/password?
4. **Analytics Detail**: Which specific metrics should the admin dashboard show first?
5. **Kanban Providers**: Should MVP support only Linear, or also Trello, Jira, etc.?

---

## Appendix: Research References

### Documents Referenced

- **docs/00_vision.md**: OperaBot vision (knowledge layer for organization).
- **docs/01_contexto_problema_mercado.md**: Problem context (70-80% repetition, expert saturation).
- **docs/02_personas_usuarios.md**: User personas (Carlos, Laura, Miguel).
- **docs/03_solucion_operabot.md**: Solution overview (chat, FAQ, admin).
- **docs/04_mvp_arquitectura_alta_nivel.md**: MVP scope and architecture.
- **docs/05_casos_uso_clave.md**: Key use cases (FAQ, chat, admin insights, kanban).
- **docs/06_roles_y_paneles.md**: Roles and permissions (User, Admin).
- **docs/07_principios_diseno_ux_ui.md**: UX/UI design principles (clarity, speed, trust, low friction).

### Master's Project Research

- 15+ interviews with operations teams (logistics + manufacturing).
- Validated: 70-80% question repetition, 2-3 hours/day expert Q&A.
- Pain points: slow onboarding, knowledge loss, expert bottleneck.

---

## Document History

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 1.0 | 2026-04-15 | Santiago Castello (BA Agent) | ✅ Ready for RE Handoff |

---

**END OF BUSINESS ANALYSIS**

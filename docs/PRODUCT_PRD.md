# onepercentbetter.poker Product PRD

## 1. Product Summary

onepercentbetter.poker is a poker hand history analysis product for tournament players using GGPoker exports.

The product ingests raw `.txt` hand history files, parses them into structured tournament and hand records, computes exploit-oriented analytics, and surfaces practical insights that help a player improve over time.

The current codebase already contains a working backend analysis engine. The main product gap is the end-user workflow: upload, review, compare, and act on insights through a dedicated product UI.

## 2. Product Goal

Help a tournament poker player answer three questions:

1. What actually happened in my recent tournaments?
2. Where am I leaking EV or missing exploit opportunities?
3. Am I improving over time?

## 3. Target User

Primary user:

- A serious low-to-mid stakes online MTT player using GGPoker
- Reviews sessions manually today or not at all
- Wants faster, structured self-analysis without building spreadsheets

Secondary user:

- A coach or study partner reviewing a player's tournament data

## 4. Current State Assessment

### Implemented Today

Backend capabilities already exist for:

- GGPoker filename parsing
- Raw hand history splitting and hand parsing
- Tournament and hand persistence in SQLite
- Duplicate ingest protection by tournament GG ID
- Tournament list and detail APIs
- Aggregate analytics:
- VPIP / PFR / VPIP-PFR gap
- Limp iso rate
- 3-bet rate
- C-bet / turn barrel / river barrel frequency
- Positional stats
- P&L timeline
- Growth timeline by week
- Stage-based analytics by stack depth
- Fish report
- Reckless all-in, bad hand selection, luck score, non-ideal wins endpoints

Verified status:

- Backend test suite passes: 78 tests

### Not Implemented as a Product Experience

The current frontend is not yet a poker analysis product UI. It is closer to a portfolio/brand landing page.

Missing product workflows:

- File upload UI for hand history ingestion
- Tournament review dashboard
- Analytics charts and summaries
- Hand browser / hand detail review
- Session comparison workflow
- User-facing empty states and error handling for poker data

### Technical Debt / Delivery Risks

- Frontend build/lint verification is currently broken because local `node_modules` is in a bad state
- Frontend tests reference routes and interactions that do not match the current UI
- DB configuration is hard-coded to SQLite file paths
- No auth or multi-user separation
- No production deployment path defined yet

## 5. Product Scope

### In Scope for MVP

- Single-user local-first experience
- Upload one or more GGPoker `.txt` files
- Store tournaments and parsed hands
- Show tournament list and key summary metrics
- Show aggregate analytics dashboard
- Show simple growth-over-time view
- Show per-tournament detail and hand list

### Out of Scope for MVP

- Real-time multiplayer coaching
- Multi-site poker support beyond GGPoker
- Full hand replayer
- Auth, billing, subscriptions
- Team features
- Mobile app

## 6. MVP User Stories

### Ingest

- As a player, I can upload one or more GGPoker `.txt` files.
- As a player, I can see whether a file was imported successfully or skipped as a duplicate.
- As a player, I can understand how many hands were found and stored.

### Tournament Review

- As a player, I can view all ingested tournaments in a list.
- As a player, I can sort or scan tournaments by date, buy-in, format, finish, and net result.
- As a player, I can open one tournament and review its hand-level summaries.

### Analytics

- As a player, I can see my headline exploit metrics across all imported data.
- As a player, I can see positional performance.
- As a player, I can see cumulative P&L over time.
- As a player, I can see whether my exploit frequencies are improving week to week.
- As a player, I can see fish-density style reports by tournament.

### Review Workflow

- As a player, I can identify suspicious or weak patterns quickly.
- As a player, I can use the dashboard to decide what to study next.

## 7. MVP Functional Requirements

### FR1. File Upload

- Support upload of `.txt` hand history files from the browser
- Reject unsupported file types
- Display ingest result summary:
- tournament name
- GG ID
- hands found
- hands inserted
- duplicate status

### FR2. Tournament List

- Show all tournaments from the backend
- Display:
- date
- tournament name
- buy-in
- format
- finish position if available
- net result if available
- session context if available

### FR3. Tournament Detail

- Show metadata for a selected tournament
- Show hand summaries for all parsed hands
- Allow simple filtering by position or action if feasible

### FR4. Dashboard

- Show headline cards for:
- total hands
- VPIP
- PFR
- VPIP-PFR gap
- limp iso rate
- 3-bet rate
- c-bet frequency
- Show charts/tables for:
- positional stats
- cumulative P&L
- weekly growth timeline
- stage stats
- fish report

### FR5. Error and Empty States

- Show useful empty states when no tournaments are imported
- Show error state if backend is unavailable
- Show partial success state if some files fail to ingest

## 8. Non-Functional Requirements

- Local development should remain lightweight
- Initial storage may remain SQLite
- API responses should stay under a few seconds for normal single-user data volumes
- Parsing must be deterministic for the same input file
- Duplicate ingest should be idempotent by tournament GG ID
- Core analytics should be covered by automated tests

## 9. UX Principles

- Lead with practical player value, not raw data density
- Surface a few strong signals first, then detailed drill-down
- Make trends visible with minimal friction
- Use poker language where helpful, but keep copy clear and concise
- Default to fast scanability: summary cards, trend visuals, concise tables

## 10. Success Metrics

For MVP success, the product should let a user:

- Upload a real GGPoker export without manual cleanup
- Review a tournament session within 1-2 minutes
- Identify at least 2-3 meaningful study targets from the dashboard
- Track improvement over multiple weeks of imported data

## 11. Delivery Plan

### Phase 1: Product Shell

Goal:
Turn the existing analysis backend into a real product workflow.

Deliverables:

- Repair frontend install/build state
- Add poker product navigation
- Add upload page
- Add dashboard page shell
- Add tournament list page
- Connect frontend to existing backend API

### Phase 2: MVP Analytics Experience

Goal:
Expose the current backend value clearly.

Deliverables:

- KPI summary cards
- Positional stats table
- P&L chart
- Growth timeline chart
- Fish report table
- Tournament detail page

### Phase 3: Review and Coaching Layer

Goal:
Make the product actionable, not just descriptive.

Deliverables:

- Leak summary generation
- Highlight unusual tendencies
- Recommend study focus areas
- Tag interesting hands for review

### Phase 4: Differentiation

Goal:
Create product moat beyond basic stats.

Deliverables:

- AI-generated session recap
- AI coaching prompts tied to actual leaks
- Cross-tournament comparison
- Opponent/table dynamics intelligence

## 12. Immediate Build Priorities

Recommended next sequence:

1. Stabilize frontend environment so build/lint/tests are trustworthy
2. Replace or separate the current portfolio-style frontend with poker product routes
3. Implement upload + ingest result flow
4. Build dashboard from existing analytics endpoints
5. Build tournament list and detail views
6. Add regression coverage for real uploaded files and frontend happy paths

## 13. Open Questions

- Is this product intended to stay local-first, or become a hosted SaaS?
- Is the target user only the hero/player, or also coaches/stables?
- Should the first UX optimize for self-review, study planning, or performance tracking?
- Will SQLite remain acceptable for the first public version?
- Should current portfolio pages remain in this repo, or be split into a separate site?

## 14. Recommendation

The strongest near-term move is to stop treating this as a general brand site and commit to a narrow poker analysis MVP:

- Upload files
- Parse and store hands
- Show a dashboard
- Review tournaments
- Surface study recommendations

The backend already gives the project real substance. The next milestone is not more analytics depth first. It is turning existing analytics into a usable product loop.

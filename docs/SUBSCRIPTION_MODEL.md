# onepercentbetter.poker Subscription Model

## 1. Pricing Strategy Summary

onepercentbetter.poker should launch as a desktop-first product with a simple monetization model:

- `Free` gives users a real but limited taste of value
- `Pro` unlocks persistent memory, pattern tracking, and exploit analysis

The product should not try to win on generic poker study features or GTO tooling.
It should monetize on one clear promise:

`We help you understand and attack soft-field weakness better over time.`

## 2. Monetization Principles

### Principle 1: Free must feel useful, not complete

Free users should get a satisfying single-tournament review experience, but not enough cumulative insight to replace a paid product.

### Principle 2: Paid value comes from memory

The strongest paywall is not one more chart.
It is persistent user history:

- remembering prior uploads
- recognizing repeated habits
- tracking bullet patterns
- tracking ITM behavior
- comparing trends across time

### Principle 3: Paid value comes from interpretation

Users should pay not only for more data, but for more meaning:

- exploit summaries
- fish-pattern interpretation
- decision-quality review
- actionable trend insights

### Principle 4: Keep early pricing simple

Launch with two tiers:

- `Free`
- `Pro`

Do not start with multiple paid tiers unless the product truly needs them.

## 3. Product Tiers

## Free

### Positioning

`A single light review to show what this app can do.`

### Intended User

- curious first-time user
- low-commitment evaluator
- someone testing whether the product understands their data

### Core Experience

- desktop upload flow
- one tournament entry review at a time
- simple summary only
- no historical memory
- no cumulative pattern tracking

### Usage Limits

Recommended launch limits:

- maximum `1 report` per `24-hour window`
- maximum `10 reports` per calendar month
- no batch pattern analysis across uploads
- no persistent cross-report history for the user

### Data Policy

Free-user uploads should be processed transiently:

- ingest file
- compute report
- return result
- do not retain long-term history for cross-session pattern memory

Possible short-lived operational retention may still be allowed for reliability, abuse prevention, or failed-job recovery, but should not be exposed as user history.

### What Free Users See

Allowed:

- tournament name
- date
- buy-in / format
- basic hand count
- simple field summary
- lightweight exploit-style summary sentence

Example:

- "You generally played well against softer opponents in this tournament."
- "You found some exploit spots, but likely left value on the table."

### What Free Users Do Not Get

- multi-file cumulative analysis
- calendar heatmaps
- weekday/hour pattern views
- average bullets
- ITM tracking
- long-term exploit identity
- full fish-response report
- detailed drill-down into pattern categories

### Conversion Mechanics

Free should visibly tease deeper value:

- blurred report panels
- locked historical tabs
- hidden metrics with partial preview
- explicit upgrade messaging tied to user curiosity

Examples:

- "See your weekday and time-of-day tendencies with Pro"
- "Track your average bullet count and ITM rate with Pro"
- "Unlock your exploit pattern report"

## Pro

### Positioning

`Your persistent poker review system.`

### Intended User

- serious recreational MTT player
- aspiring winning reg in soft fields
- player actively reviewing leaks and tendencies

### Core Experience

- persistent account-backed memory
- desktop upload and sync workflows
- cumulative pattern tracking
- exploit interpretation over time

### Included Features

- multi-file uploads
- persistent upload history
- tournament memory across sessions
- calendar heatmap
- weekday volume tendencies
- hourly volume tendencies
- session rhythm analysis
- average bullets per tournament
- ITM frequency and trends
- fish-density and fish-response reporting
- exploit tendency reporting
- detailed per-entry reports
- historical pattern tracking over time
- folder auto-sync

### Pro Value Narrative

Pro is not "more charts."
Pro is:

- remembering how you actually play
- exposing recurring exploit opportunities
- showing whether you punish weak fields consistently
- identifying your repeat habits and blind spots

## Future Tier: Elite or Coach

This tier should not exist at launch unless there is clear demand.
It can be added later for advanced users, coaches, or stable-style workflows.

Potential future unlocks:

- AI-generated coaching plans
- cohort comparisons
- global-pool exploit segmentation
- coach review tools
- higher sync/storage allowances
- advanced filters and exports

## 4. Feature Matrix

| Feature | Free | Pro |
|---|---|---|
| Desktop upload | Yes | Yes |
| Single tournament light review | Yes | Yes |
| Reports per 24h | 1 | Unlimited or high cap |
| Monthly reports | 10 | Unlimited or high cap |
| Persistent history | No | Yes |
| Multi-file pattern analysis | No | Yes |
| Calendar heatmap | No | Yes |
| Weekday/hour tendencies | No | Yes |
| Average bullets | No | Yes |
| ITM tracking | No | Yes |
| Historical exploit tracking | No | Yes |
| Full fish-response analysis | Blurred/locked | Yes |
| Folder auto-sync | No | Yes |
| Long-term memory | No | Yes |

## 5. Report Packaging

## Free Report Design

Free reports should feel polished but strategically incomplete.

Recommended layout:

- top summary card
- tournament metadata
- one short exploit summary sentence
- one or two lightweight stats
- blurred deeper sections below

Blurred sections may preview:

- fish-response pattern
- average bullet trend
- ITM tendency
- time-of-day habit pattern
- exploit aggression consistency

The user should understand that the app has more insight available, but not receive enough detail to bypass payment.

## Pro Report Design

Pro reports should expand from single-report readout into a true analysis workspace:

- full report details
- prior context from earlier uploads
- trend awareness
- habit interpretation
- actionable summaries

## 6. Data Retention Model by Tier

### Free

- no long-term user memory for product features
- no persistent pattern tracking
- no cross-report longitudinal analysis

Operational note:

The system may still need temporary retention for rate limiting, fraud prevention, and billing enforcement.

### Pro

- persistent per-user upload memory
- entry history
- pattern timelines
- usage-derived personalization

This is the foundation for future SaaS growth.

## 7. Growth Path

## Stage 1: Ontario-Only, Desktop-First

Use case:

- users manually upload Ontario GGPoker hand histories
- app delivers light free reviews and paid persistent reports

Goal:

- prove that users care about exploit-pattern insights

## Stage 2: Global Pool Expansion

Use case:

- expand parsing and analysis support beyond Ontario-specific data assumptions
- support the larger GGPoker global audience

Requirements:

- more resilient parser coverage
- user account system
- stronger cloud persistence
- per-region data handling awareness if needed

## Stage 3: Memory-Driven SaaS

Use case:

- the product starts to know the user over time
- recommendations become personalized and longitudinal

This is where the strongest subscription moat emerges.

## 8. Recommended Launch Offer

Start simple:

- `Free`
- `Pro Monthly`
- optionally `Pro Annual` once retention is proven

Do not over-design pricing before product usage validates which paid insights users value most.

## 9. Messaging Recommendations

### Free Messaging

- "See how you played in this tournament."
- "Want deeper exploit insight? Unlock the full report."
- "Track your real tendencies over time with Pro."

### Pro Messaging

- "Turn uploads into memory."
- "Track how you attack soft fields over time."
- "See whether your exploit decisions are actually improving."

## 10. Open Design Decisions

These still need confirmation before final pricing implementation:

1. Should Pro be unlimited, or should it have soft monthly caps at launch?
2. Should folder auto-sync be included in Pro immediately, or introduced later as an upgrade driver?
3. Should Free allow only one file upload at a time, or one report even if multiple files are submitted?
4. Should the free report show exact stats, or only summary language plus blurred detailed metrics?
5. Should billing begin as desktop in-app purchase, Stripe web checkout, or web account subscription attached to desktop login?

## 11. Recommendation

Launch with a narrow and disciplined model:

- Free proves report quality
- Pro monetizes persistence, memory, and exploit interpretation

The key insight is that the true paid asset is not a single tournament report.
It is the system's ability to remember the user, identify recurring soft-field opportunities, and quantify whether the user's exploit identity is improving.

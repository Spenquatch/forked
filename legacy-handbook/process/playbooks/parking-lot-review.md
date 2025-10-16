---
title: Playbook - Parking Lot Review
type: process
date: 2025-09-23
tags: [process, playbook, parking-lot, quarterly, review]
links: [../../docs/PARKING_LOT_SYSTEM.md, ./roadmap-planning.md]
---

# Playbook - Parking Lot Quarterly Review

## Purpose
Systematically review parking lot items every quarter to promote high-value ideas to the roadmap, archive stale concepts, and maintain a healthy innovation pipeline.

## When
- **Quarterly**: Every 3 months (aligned with roadmap planning)
- **Pre-Planning**: 1 week before quarterly roadmap session
- **Ad-hoc**: When parking lot exceeds 50 items
- **Annual**: Deep review and major cleanup

## Pre-Review Preparation

### 1. Generate Review Materials
```bash
# Generate parking lot summary
make parking-stats

# Export for review
make parking-export format=csv > parking-lot-Q4-2025.csv

# Age analysis
make parking-age-report
```

### 2. Stakeholder Notification
Send review invitation 1 week prior:
```markdown
**Subject**: Quarterly Parking Lot Review - [Q1 2025]

Team,

Our quarterly parking lot review is scheduled for [Date].
Currently we have:
- Features: X items
- Research: Y items
- Technical Debt: Z items
- Ideas: N items

Please review the parking lot before the meeting:
`make parking-list`

Come prepared to discuss items you've submitted or are interested in championing.
```

## Review Meeting Structure (90 minutes)

### Part 1: Overview (10 minutes)

#### Metrics Review
```bash
make parking-metrics

# Shows:
# - Total items by category
# - Age distribution
# - Submission trends
# - Previous quarter promotions
```

#### Categories Distribution
- **Features**: User-facing capabilities
- **Research**: Technical investigations
- **Technical Debt**: Infrastructure/code improvements
- **Ideas**: Blue-sky thinking

### Part 2: Category Review (60 minutes)

#### Features Review (20 minutes)
```bash
make parking-list category=features
```

**Evaluation Criteria**:
1. **Market Demand**: Customer requests, competitive pressure
2. **Strategic Fit**: Alignment with company direction
3. **Technical Feasibility**: Can we build it now?
4. **Resource Requirements**: Team, time, dependencies
5. **Value/Effort Ratio**: ROI assessment

**Decision Matrix**:
| Score | Action | Target |
|-------|--------|--------|
| 8-10 | Promote Immediately | Roadmap "Now" |
| 6-7 | Promote Soon | Roadmap "Next" |
| 4-5 | Keep in Parking Lot | Re-review next quarter |
| 2-3 | Needs Work | Refine or combine |
| 0-1 | Archive | Not viable |

#### Research Review (15 minutes)
```bash
make parking-list category=research
```

**Evaluation Criteria**:
1. **Learning Value**: What will we discover?
2. **Risk Reduction**: Does it de-risk future work?
3. **Innovation Potential**: Could it be game-changing?
4. **Resource Investment**: Time-boxed exploration?

**Promotion Triggers**:
- Blocking feature development
- Technology maturity reached
- Competitive intelligence need
- Architecture decision required

#### Technical Debt Review (15 minutes)
```bash
make parking-list category=technical-debt
```

**Evaluation Criteria**:
1. **Pain Level**: How much is it slowing us down?
2. **Risk Level**: Security, stability, scalability impact
3. **Compound Interest**: Getting worse over time?
4. **Fix Complexity**: Quick win or major project?

**Priority Scoring**:
```
Priority = (Pain × Risk × Growth Rate) / Complexity
```

#### Ideas Review (10 minutes)
```bash
make parking-list category=ideas
```

**Quick Assessment**:
- **Transform**: Convert to specific feature/research
- **Combine**: Merge with similar ideas
- **Incubate**: Keep for future consideration
- **Archive**: Not aligned with direction

### Part 3: Promotion Decisions (15 minutes)

#### Promotion Process
```bash
# Promote to roadmap
make parking-promote item=FEAT-20250922-oauth target=now
make parking-promote item=RESEARCH-20250915-ai target=next
make parking-promote item=DEBT-20250901-refactor target=later

# Archive stale items
make parking-archive item=IDEA-20240601-old
make parking-archive-batch age=365  # Archive >1 year old
```

#### Documentation Requirements
For each promoted item, document:
1. **Business Case**: Why now?
2. **Success Metrics**: How do we measure value?
3. **Dependencies**: What needs to happen first?
4. **Owner**: Who will champion this?
5. **Initial Scope**: MVP definition

### Part 4: Action Items (5 minutes)

#### Standard Actions
- [ ] Update roadmap with promoted items
- [ ] Create feature stubs for "Now" promotions
- [ ] Archive rejected items with reasons
- [ ] Notify submitters of decisions
- [ ] Schedule deep-dives for complex items

## Scoring Framework

### Feature Scoring Template
```markdown
**Item**: FEAT-20250922-social-login
**Submitted**: 2025-09-22
**Submitter**: @product-team

**Scores** (1-10):
- Market Demand: 8 (multiple customer requests)
- Strategic Fit: 7 (supports user growth goals)
- Technical Feasibility: 9 (OAuth libraries available)
- Resource Requirements: 6 (2-3 sprints estimated)
- Value/Effort: 7 (high value, moderate effort)

**Total**: 37/50 (74%)
**Decision**: Promote to "Next"
**Rationale**: High customer demand, wait for auth system completion
```

### Bulk Scoring Interface
```bash
# Interactive scoring session
make parking-score

# Generates scoring matrix:
# Item ID | Category | Age | Score | Decision | Notes
```

## Decision Outcomes

### Promotion to Roadmap
```bash
# Create roadmap entry
make roadmap-add item="OAuth Integration" section=next \
  source=FEAT-20250922-oauth

# Create feature stub
make feature-create name=oauth-integration \
  parking_lot_origin=FEAT-20250922-oauth \
  stage=proposed owner=@auth-team
```

### Keep in Parking Lot
```bash
# Add review notes
make parking-annotate item=FEAT-XXX \
  note="Reviewed Q1-2025: Wait for platform upgrade"

# Set re-review date
make parking-defer item=FEAT-XXX quarters=1
```

### Archive
```bash
# Archive with reason
make parking-archive item=IDEA-XXX \
  reason="Not aligned with new strategy"

# Bulk archive old items
make parking-archive-batch age=365 \
  reason="Stale - no activity for 1 year"
```

## Parking Lot Patterns

### Idea Combinations
Look for ideas that can be combined:
- Similar features → Unified solution
- Related research → Comprehensive study
- Technical debt items → Refactoring sprint

### Trend Detection
Identify emerging themes:
- Multiple requests in same area
- Technology shifts requiring research
- Debt accumulating in specific components

### Innovation Pipeline
Maintain balance:
- 40% Near-term features (next 6 months)
- 30% Research and exploration
- 20% Technical improvements
- 10% Blue-sky innovation

## Communication

### Post-Review Communication
```markdown
**Subject**: Parking Lot Review Outcomes - Q1 2025

**Promoted to Roadmap** (5 items):
- 🚀 OAuth Integration → "Next" quarter
- 🚀 GraphQL API → "Later" this year
- [...]

**Remaining in Parking Lot** (12 items):
- ⏸️ Advanced Analytics (needs more definition)
- ⏸️ Mobile App (waiting for API v2)
- [...]

**Archived** (8 items):
- 📦 Legacy System Migration (no longer relevant)
- 📦 Feature X (superseded by Feature Y)
- [...]

**Next Review**: April 2025
```

### Individual Notifications
For promoted items:
```markdown
To: [Submitter]
Subject: Your idea was promoted! - [Item Title]

Great news! Your parking lot item "[Title]" has been promoted to the roadmap.

Next steps:
1. You've been assigned as feature owner
2. Please create initial feature documentation
3. We'll discuss in next sprint planning

Thanks for your contribution!
```

For archived items:
```markdown
To: [Submitter]
Subject: Parking lot item archived - [Item Title]

After quarterly review, we've archived "[Title]".

Reason: [Specific reason for archival]

If circumstances change, feel free to resubmit with updated context.

Thank you for your idea!
```

## Metrics & Reporting

### Review Effectiveness
```bash
# Track promotion success
make parking-promotion-stats

# Metrics:
# - Promotion rate by category
# - Time from submission to promotion
# - Success rate of promoted items
# - Submitter engagement levels
```

### Parking Lot Health
```bash
# Health check
make parking-health

# Indicators:
# - Growth rate (sustainable?)
# - Age distribution (too stale?)
# - Category balance (diverse?)
# - Engagement (active submissions?)
```

## Best Practices

### ✅ DO
- **Review quarterly** without fail
- **Score objectively** using framework
- **Communicate decisions** promptly
- **Archive aggressively** to prevent staleness
- **Celebrate promotions** to encourage participation
- **Track metrics** to improve process

### ❌ DON'T
- **Let items age** beyond 12 months without decision
- **Promote without ownership** assignment
- **Skip documentation** for promoted items
- **Ignore trends** in submissions
- **Review in isolation** - include stakeholders

## Annual Deep Review

Once per year, conduct deeper analysis:

### Strategic Alignment Check
- Review all items against updated strategy
- Identify shifts in thinking
- Spot innovation opportunities

### Process Improvement
- Analyze promotion success rates
- Review scoring accuracy
- Optimize review process
- Update evaluation criteria

### Clean Slate Option
```bash
# Optional annual reset
make parking-archive-all reason="Annual reset 2025"
make parking-request-resubmit  # Ask for fresh submissions
```

## Quick Reference

### Review Commands
```bash
# Quarterly review
make parking-review              # Interactive review
make parking-stats              # Summary statistics
make parking-age-report         # Age analysis

# Promotion
make parking-promote item=XXX target=now/next/later
make roadmap-add item="Title" source=parking-lot

# Archive
make parking-archive item=XXX reason="..."
make parking-archive-batch age=365

# Metrics
make parking-metrics
make parking-promotion-stats
make parking-health
```

### Review Calendar
- **Q1 Review**: Last week of March
- **Q2 Review**: Last week of June
- **Q3 Review**: Last week of September
- **Q4 Review**: Last week of December

---

**Remember**: The parking lot is an innovation pipeline, not a graveyard. Regular review and decisive action keep ideas flowing and morale high.
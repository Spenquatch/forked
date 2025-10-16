# Issue Backlog System Guide

## Overview

The Issue Backlog system manages bugs, urgent requests, and production issues using a P0-P4 severity classification. It integrates with sprint planning through an 80/20 capacity allocation model, ensuring teams can respond to critical issues while maintaining planned work.

## Purpose

- **Track bugs** and production issues systematically
- **Prioritize** based on user impact and severity
- **Allocate capacity** for reactive work (20% of sprint)
- **Generate AI analysis** for critical P0 issues
- **Escalate appropriately** based on severity rubric

## 80/20 Capacity Allocation

### Philosophy
Every sprint allocates capacity as follows:
- **80% Planned Work**: Release features, sprint goals, scheduled improvements
- **20% Reactive Work**: P0/P1 issues, urgent wildcards, hotfixes

### Implementation
```bash
# During sprint planning
make sprint-plan                      # Shows 80/20 allocation
make backlog-list severity=P0         # Review critical issues
make backlog-list severity=P1         # Review high priority issues
make backlog-assign issue=BUG-001 sprint=current  # Assign to 20% capacity
```

## Severity Classification (P0-P4)

### P0 - Critical 🔴
**Impact**: >50% users affected, data loss, security exploit
**Action**: Interrupt current sprint immediately
**Examples**:
- Production database down
- Payment processing failure
- Security breach active
- Complete service outage

### P1 - High 🟠
**Impact**: 10-50% users affected, major feature broken
**Action**: Address in current sprint (20% capacity)
**Examples**:
- Login failures for subset of users
- Core feature malfunction
- Significant performance degradation
- Data inconsistency issues

### P2 - Medium 🟡
**Impact**: <10% users affected, minor feature issues
**Action**: Queue for next sprint planning
**Examples**:
- UI glitches
- Non-critical feature bugs
- Minor performance issues
- Edge case failures

### P3 - Low 🟢
**Impact**: Cosmetic issues, developer experience
**Action**: Backlog queue, low priority
**Examples**:
- Typos in UI
- Code cleanup needed
- Documentation gaps
- Minor improvements

### P4 - Wishlist ⚪
**Impact**: Future enhancements
**Action**: Consider for parking lot
**Examples**:
- Nice-to-have features
- Long-term improvements
- Experimental ideas

## Commands

### Adding Issues
```bash
# Add a bug
make backlog-add type=bug title="Login fails" severity=P1 desc="Users can't login" \
                 impact="30% of users affected" workaround="Use incognito mode"

# Add a wildcard (urgent request)
make backlog-add type=wildcards title="CEO demo request" severity=P1 \
                 desc="Need demo environment by tomorrow"
```

### Listing Issues
```bash
make backlog-list                    # Show all issues by severity
make backlog-list severity=P0        # Filter by severity
make backlog-list category=bugs      # Filter by category
make backlog-list format=json        # JSON output
```

### Severity Rubric
```bash
make backlog-rubric                  # Display P0-P4 classification guide
```

### P0 Triage Analysis
```bash
make backlog-triage issue=BUG-P0-001 # Generate AI analysis for P0 issue
```

### Sprint Assignment
```bash
make backlog-assign issue=BUG-001 sprint=current  # Assign to current sprint
make backlog-assign issue=BUG-001 sprint=next     # Queue for next sprint
```

## Directory Structure

```
backlog/
├── index.json                      # Automated rollup with severity tracking
├── bugs/
│   └── BUG-P1-YYYYMMDD-HHMM/
│       ├── README.md              # Issue description with front matter
│       └── triage.md              # AI triage analysis (P0 only)
└── wildcards/
    └── WILD-P1-YYYYMMDD-HHMM/
        └── README.md
```

## P0 Triage Analysis

For P0 issues, the system generates an AI triage template with:

### Problem Statement
- Issue description
- Impact metrics
- Affected services
- Data at risk

### Solution Options Analysis

#### Option 1: Hotfix
**Pros**: Quick deployment, minimal testing, low risk
**Cons**: Technical debt, may not address root cause
**Time**: X hours
**Sprint Impact**: Specific tasks delayed

#### Option 2: Proper Fix
**Pros**: Addresses root cause, prevents recurrence
**Cons**: Takes longer, requires testing, higher risk
**Time**: Y days
**Sprint Impact**: Major replanning needed

### Cascading Effects
- Hotfix consequences
- Proper fix implications
- Do-nothing escalation

### AI Recommendation
- Recommended approach with rationale
- Based on severity, resources, sprint state

### Human Decision Framework
Key questions for leadership:
1. Business priority vs sprint deliverables?
2. Resource availability?
3. Risk tolerance?
4. Customer communication?
5. Compliance implications?

## P0 Interrupt Workflow

### 1. Issue Appears
```bash
make backlog-add type=bug title="Database down" severity=P0 \
                 desc="Production database unresponsive" \
                 impact="100% users affected"
```

### 2. Automatic Alert
```
============================================================
🚨 P0 CRITICAL ISSUE - IMMEDIATE ACTION REQUIRED 🚨
============================================================
Issue: Database down
Impact: 100% users affected

Recommended actions:
1. Run: make backlog-triage issue=BUG-P0-YYYYMMDD-HHMM
2. Notify incident response team
3. Consider interrupting current sprint
============================================================
```

### 3. Generate Triage Analysis
```bash
make backlog-triage issue=BUG-P0-YYYYMMDD-HHMM
```

### 4. Make Decision
Review triage analysis and decide:
- Hotfix now, proper fix later
- Full fix now despite sprint impact
- Workaround while planning fix

### 5. Assign to Sprint
```bash
make backlog-assign issue=BUG-P0-YYYYMMDD-HHMM sprint=current
```

## Sprint Integration

### Planning Phase
1. Review P0/P1 issues during sprint planning
2. Allocate 20% capacity for reactive work
3. Assign known P1 issues
4. Reserve remaining for unknowns

### Execution Phase
1. P0 issues interrupt immediately
2. P1 issues use reserved capacity
3. P2+ issues wait for next sprint
4. Track capacity usage

### Retrospective
1. Review reactive vs planned ratio
2. Analyze P0 incidents
3. Adjust future capacity if needed

## Capacity Adjustment Guidelines

### When to Adjust 80/20 Ratio

**Increase Reactive Capacity (70/30 or 60/40)**:
- High incident period
- Legacy system maintenance
- Post-release stabilization
- Support rotation weeks

**Decrease Reactive Capacity (90/10)**:
- Feature sprint focus
- Stable system period
- After major refactoring
- Low customer activity

## Escalation Procedures

### P0 Escalation
1. **Immediate**: Create issue and triage
2. **15 minutes**: Incident commander assigned
3. **30 minutes**: Initial assessment complete
4. **1 hour**: Fix approach decided
5. **Continuous**: Status updates every hour

### P1 Escalation
1. **Same day**: Issue reviewed
2. **Next day**: Assignment decision
3. **Current sprint**: Work begins
4. **Weekly**: Progress updates

## Metrics and Reporting

### Health Metrics
- **P0 frequency**: Incidents per month
- **P0 resolution**: Mean time to resolve
- **P1 backlog**: Count and age
- **Capacity usage**: Actual reactive % vs planned

### Success Indicators
- P0 resolution < 4 hours
- P1 resolution < 1 sprint
- Reactive capacity < 25%
- No P0 recurrence

## Best Practices

### DO:
- ✅ Use severity rubric consistently
- ✅ Generate triage for all P0s
- ✅ Respect 80/20 allocation
- ✅ Document workarounds
- ✅ Track resolution time

### DON'T:
- ❌ Inflate severity for priority
- ❌ Skip triage analysis
- ❌ Exceed 20% reactive without discussion
- ❌ Leave P0/P1 unassigned
- ❌ Ignore recurring issues

## Integration with Other Systems

### Parking Lot
- P4 issues may move to parking lot
- Review during quarterly planning
- Not urgent enough for backlog

### Feature Development
- Bug fixes may reveal feature gaps
- Track feature-related bugs
- Consider in feature retrospectives

### Release Management
- P0/P1 issues may delay releases
- Track release-blocking bugs
- Gate releases on P0 resolution

## FAQ

**Q: What if we have multiple P0s simultaneously?**
A: Form incident command structure, triage by actual impact, consider all-hands response.

**Q: Can we change severity after creation?**
A: Yes, as understanding improves. Document why it changed.

**Q: What if 20% capacity isn't enough?**
A: Discuss with team, adjust ratio, consider stopping sprint.

**Q: Should customer-reported issues be P0?**
A: Only if they meet P0 criteria. Customer importance ≠ severity.

**Q: How do wildcards differ from bugs?**
A: Wildcards are urgent requests (not defects). Same severity scale applies.
# Parking Lot System Guide

## Overview

The Parking Lot system manages future ideas, research topics, technical debt, and external requests that aren't ready for immediate implementation. It serves as a repository for concepts that may become valuable in the future but don't fit current priorities.

## Purpose

- **Capture ideas** without losing them
- **Defer decisions** until the right time
- **Reduce noise** in active planning
- **Enable quarterly reviews** for strategic alignment
- **Archive outdated** concepts systematically

## Categories

### Features (`parking-lot/features/`)
Future product features and enhancements that aren't currently prioritized.

**Examples**:
- Social login integration
- ML-powered recommendations
- Advanced analytics dashboard

### Technical Debt (`parking-lot/technical-debt/`)
Known technical improvements that should be addressed eventually.

**Examples**:
- Database query optimization
- Legacy code refactoring
- Dependency updates

### Research (`parking-lot/research/`)
Technologies, patterns, or approaches to investigate.

**Examples**:
- New framework evaluation
- Performance optimization techniques
- Security best practices

### External Requests (`parking-lot/external-requests/`)
Stakeholder requests that aren't urgent or aligned with current strategy.

**Examples**:
- Partner integration requests
- Nice-to-have feature requests
- Long-term customer wishlist items

## Commands

### Adding Items
```bash
make parking-add type=features title="Social Login" desc="Add OAuth2 support"
make parking-add type=technical-debt title="Refactor auth" desc="Modernize auth system"
make parking-add type=research title="GraphQL" desc="Evaluate GraphQL adoption"
make parking-add type=external-requests title="Partner API" desc="Integrate with XYZ"
```

### Listing Items
```bash
make parking-list                    # Show all items
make parking-list category=features  # Filter by category
make parking-list format=json        # JSON output
```

### Quarterly Review Process
```bash
make parking-review                  # Interactive review interface
```

The review process presents each item for:
- **Promote** to roadmap (move to `roadmap/later/`)
- **Delete**/archive (remove from parking lot)
- **Skip** (keep in parking lot)
- **View** full content

### Promoting Items
```bash
make parking-promote item=FEAT-001 target=later  # Promote to roadmap/later
make parking-promote item=FEAT-001 target=next   # Promote to roadmap/next
make parking-promote item=FEAT-001 target=now    # Promote to roadmap/now (rare)
```

## Directory Structure

```
parking-lot/
├── index.json                      # Automated rollup of all items
├── features/
│   └── FEAT-YYYYMMDD-title/
│       └── README.md              # Item description with front matter
├── technical-debt/
│   └── DEBT-YYYYMMDD-title/
│       └── README.md
├── research/
│   └── RES-YYYYMMDD-title/
│       └── README.md
└── external-requests/
    └── EXT-YYYYMMDD-title/
        └── README.md
```

## Item Structure

Each item has a README.md with front matter:

```markdown
---
title: Social Login Integration
type: features
status: parking-lot
created: 2025-09-22
owner: unassigned
tags: [authentication, oauth]
---

# Social Login Integration

Add OAuth2 support for Google, GitHub, and Microsoft login.

## Context

Users have requested social login to reduce password fatigue.

## Potential Value

- Improved user experience
- Reduced support tickets for password resets
- Higher conversion rates

## Considerations

- Security implications
- Privacy policy updates needed
- Additional OAuth provider costs
```

## Quarterly Review Workflow

### 1. Schedule Review
Conduct parking lot reviews quarterly, typically during roadmap planning:
- Q1: January
- Q2: April
- Q3: July
- Q4: October

### 2. Review Criteria

**Promote to Roadmap**:
- Aligns with strategic goals
- Customer demand increased
- Dependencies now available
- Resources becoming available

**Archive/Delete**:
- No longer relevant
- Superseded by other solutions
- Technical approach outdated
- Business priorities changed

**Keep in Parking Lot**:
- Still valuable but not yet prioritized
- Waiting for dependencies
- Resource constraints
- Timing not right

### 3. Promotion Process

When promoting to roadmap:
1. Review and update item description
2. Assign initial owner
3. Estimate effort and value
4. Identify dependencies
5. Move to appropriate roadmap section (now/next/later)

## Integration with Planning

### Sprint Planning
Parking lot items should NOT be pulled directly into sprints. They must first be:
1. Promoted to roadmap
2. Converted to features
3. Approved and planned
4. Then broken into sprint tasks

### Feature Creation
When a parking lot item becomes a feature:
```bash
# First promote to roadmap
make parking-promote item=FEAT-001 target=next

# Then create feature
make feature-create name=social-login

# Link back to original parking lot item in feature documentation
```

### Backlog Relationship
- **Parking Lot**: Future possibilities (low priority)
- **Backlog**: Current issues needing attention (high priority)
- P4 issues in backlog may be candidates for parking lot

## Best Practices

### DO:
- ✅ Capture all ideas, even if unlikely
- ✅ Add context and rationale
- ✅ Review quarterly
- ✅ Link related items
- ✅ Update items if context changes

### DON'T:
- ❌ Use as a task backlog
- ❌ Add urgent items (use backlog instead)
- ❌ Promote without proper evaluation
- ❌ Let items age indefinitely
- ❌ Skip quarterly reviews

## Metrics

### Health Indicators
- **Item age**: Average time in parking lot
- **Promotion rate**: % promoted vs archived
- **Category distribution**: Balance across categories
- **Review frequency**: Quarterly reviews completed

### Success Metrics
- **Idea capture rate**: No valuable ideas lost
- **Promotion quality**: Promoted items succeed
- **Archive rate**: Regular cleanup maintains focus
- **Strategic alignment**: Promoted items align with goals

## Automation

### Index Generation
The `parking-lot/index.json` file is automatically updated when:
- Items are added
- Items are promoted
- Items are deleted
- Manual update via `python3 process/automation/parking_lot_manager.py update-index`

### Quarterly Reminders
The system can be configured to remind about quarterly reviews:
- Check `process/checks/validation_rules.json`
- Set `max_age_before_review_months`: 3

## FAQ

**Q: When should I use parking lot vs backlog?**
A: Parking lot is for future ideas with no urgency. Backlog is for current issues needing attention.

**Q: Can I promote directly to "now" in the roadmap?**
A: Technically yes, but it's rare. Usually items go to "later" first.

**Q: Should technical debt go in parking lot or backlog?**
A: Non-urgent debt → parking lot. Debt causing issues → backlog.

**Q: How often should we review?**
A: Quarterly is recommended, but can adjust based on organization needs.

**Q: What happens to archived items?**
A: They're deleted from the parking lot. Consider keeping a separate archive if needed.
---
title: Playbook - Release Planning
type: process
date: 2025-09-21
tags: [process, playbook, release, planning]
links: [./sprint-planning.md, ./roadmap-planning.md, ../automation/release_manager.py]
---

# Playbook - Release Planning

## Purpose
Plan coherent product releases that bundle features into valuable deliveries, coordinate sprint work, and align with strategic roadmap goals.

## When
- **Time-based**: Every 2-4 sprints (2-4 weeks)
- **Feature-driven**: When key features reach completion
- **Strategic**: When roadmap priorities shift
- **Market-driven**: When external deadlines or opportunities arise

## Pre-Planning Checklist
- [ ] Previous release delivered and retrospective completed
- [ ] Roadmap priorities reviewed and current
- [ ] Feature status assessed (`make feature-summary`)
- [ ] Parking lot reviewed for promotion candidates (`make parking-review`)
- [ ] Critical backlog items evaluated (`make backlog-list severity=P0`)
- [ ] Team capacity and availability confirmed (80/20 allocation considered)
- [ ] Stakeholder expectations aligned

## Release Planning Process

### 1. **Assess Current State**

```bash
# Review overall project status
make dashboard
make feature-summary      # See feature completion across sprints
make roadmap             # Review strategic priorities

# Review parking lot for promotion candidates
make parking-review       # Quarterly review of future ideas
make parking-list        # See all categorized items

# Check critical backlog items
make backlog-list severity=P0,P1  # High priority issues
make backlog-rubric              # Severity guidelines
```

**Key Questions**:
- Which features are nearing completion?
- What parking lot items should be promoted to the roadmap?
- Are there P0/P1 issues that must be addressed in this release?
- What's the current development velocity (considering 80/20 allocation)?
- Are there natural feature groupings ready for release?
- What are the roadmap priorities for next quarter?

### 2. **Determine Release Type & Scope**

#### **Release Types**

**Minor Release (v1.1.0)**: 2 sprints
- Small feature additions
- Bug fixes and improvements
- No breaking changes
- Low risk, fast delivery

**Standard Release (v1.2.0)**: 3 sprints
- Significant new features
- API enhancements
- Performance improvements
- Moderate complexity

**Major Release (v2.0.0)**: 4 sprints
- Breaking changes
- Architecture overhauls
- Major new capabilities
- High complexity, high value

#### **Scope Decision Framework**

**Questions to answer**:
- What value does this release deliver to users?
- Can features be delivered independently or must they be bundled?
- What's the risk/complexity of the feature set?
- How does this align with roadmap milestones?

### 3. **Create Release Plan**

```bash
# Create release structure
make release-plan version=v1.2.0 sprints=3

# Or with custom timeline
make release-plan version=v1.2.0 sprints=3 start=SPRINT-2025-W40
```

**Edit generated plan** in `releases/v1.2.0/plan.md`:
- Define clear release theme and value proposition
- Set primary, secondary, and stretch goals
- Identify success criteria and acceptance gates

### 4. **Select and Assign Features**

#### **Feature Selection Process**

**Step 1: Parking Lot Promotion**
```bash
# Review parking lot items quarterly
make parking-review

# Promote high-value items to roadmap
make parking-promote item=FEAT-001 target=next
make parking-promote item=RESEARCH-002 target=later
```

**Step 2: Backlog Priority Assessment**
```bash
# Identify critical issues that must be addressed
make backlog-list severity=P0,P1
make backlog-assign issue=BUG-P0-001 release=v1.2.0
```

**Step 3: Feature Selection Criteria**

**Must Have (Critical Path)**:
- P0 backlog issues (production critical)
- Features that enable other features
- Customer-critical functionality
- Security or compliance requirements
- Dependencies for next release

**Should Have (High Value)**:
- P1 backlog issues (major functionality)
- High-impact user features
- Promoted parking lot items
- Significant technical improvements
- Strategic roadmap advancement

**Nice to Have (Stretch Goals)**:
- P2/P3 backlog items
- Polish and UX improvements
- Performance optimizations
- Developer experience enhancements

#### **Feature Assignment**

```bash
# Assign critical path features
make release-add-feature release=v1.2.0 feature=auth-system critical=true

# Assign epic features
make release-add-feature release=v1.2.0 feature=api-overhaul epic=true

# Assign regular features
make release-add-feature release=v1.2.0 feature=user-dashboard
```

### 5. **Validate Release Feasibility**

```bash
# Check release status and timeline
make release-status

# Review feature dependencies
make feature-summary

# Assess capacity vs scope (with 80/20 allocation)
# Planned work: 80% × team velocity × sprint count
# Reserved for P0/P1: 20% × team velocity × sprint count
make sprint-capacity

# Check parking lot promotion impact
make parking-list status=promoted
```

**Feasibility Checkpoints**:
- **Capacity**: Does 80% planned velocity support the scope?
- **Reactive Reserve**: Is 20% sufficient for expected P0/P1 issues?
- **Dependencies**: Are feature dependencies satisfied?
- **Parking Lot Items**: Can promoted items fit within capacity?
- **Risk**: Are there major unknowns or external dependencies?
- **Timeline**: Does release timeline align with roadmap needs?

### 6. **Plan Sprint Coordination**

#### **Sprint Theme Assignment**

**Sprint 1**: Foundation/Setup
- Critical path setup
- Dependencies resolution
- Risk mitigation

**Sprint 2**: Core Development
- Primary feature development
- Integration work
- Testing infrastructure

**Sprint 3**: Integration/Polish
- Feature integration
- Testing and quality
- Documentation and release prep

#### **Critical Path Management**

- **Identify**: Which features block others?
- **Protect**: Ensure critical path has buffer
- **Monitor**: Track critical path health in daily status
- **Escalate**: Address critical path blockers immediately

### 7. **Release Communication**

#### **Internal Communication**
- **Team announcement**: Release goals and timeline
- **Sprint alignment**: How each sprint contributes to release
- **Dependency coordination**: Cross-team requirements
- **Progress tracking**: Regular release status reviews

#### **Stakeholder Communication**
- **Release goals**: Clear value proposition
- **Timeline**: Realistic delivery expectations
- **Success criteria**: Measurable outcomes
- **Risk factors**: Potential delays or scope changes

## Release Execution Monitoring

### **Weekly Release Health Check**
```bash
# During each sprint in the release
make release-status      # Overall release progress
make sprint-status       # Current sprint health
make feature-summary     # Feature progress across sprints
```

**Health Indicators**:
- 🟢 **Green**: On track, features progressing as planned
- 🟡 **Yellow**: Some features behind, adjustments needed
- 🔴 **Red**: Critical path at risk, major intervention required

### **Release Risk Management**

**Common Risks & Mitigations**:

**Scope Creep**
- Lock scope after planning
- New requests go to next release
- Change control process for exceptions

**Critical Path Delays**
- Daily tracking of critical path features
- Buffer allocation for unknowns
- Parallel work preparation for non-blocked items

**External Dependencies**
- Early identification and communication
- Contingency plans for delays
- Regular dependency status checks

**Team Capacity Changes**
- PTO planning during release planning
- Cross-training for key features
- Flexible sprint scope adjustment

### **Release Completion**

```bash
# When all features complete
make release-close version=v1.2.0

# This generates:
# - Changelog from completed tasks
# - Release notes template
# - Feature completion summary
# - Metrics for retrospective
```

## Advanced Release Planning

### **Feature-Driven Releases**

**Approach**: Plan releases around feature readiness
- Monitor feature completion rates
- Bundle features that deliver coherent value
- Release when logical feature sets complete

**Example**: Authentication release includes login, permissions, and session management

### **Time-Driven Releases**

**Approach**: Fixed release cadence regardless of feature completion
- Consistent delivery rhythm
- Features that don't complete move to next release
- Predictable planning cycle

**Example**: Release every 6 weeks regardless of scope

### **Hybrid Approach** (Recommended)

**Strategy**: Time-boxed with feature flexibility
- Target delivery dates with scope flexibility
- Core features committed, stretch features optional
- Scope reduction preferred over timeline extension

### **Epic Feature Management**

**Epic features** span multiple sprints/releases:

**Planning Strategy**:
- Break epics into release-sized chunks
- Each chunk delivers independent value
- Plan epic milestones across releases
- Track epic progress across release boundaries

**Example**: Platform Architecture Epic
- **v1.1.0**: Database modernization
- **v1.2.0**: API restructure
- **v1.3.0**: Frontend integration
- **v2.0.0**: Legacy system retirement

## Release Planning Anti-Patterns

### **❌ Common Mistakes**

**Over-ambitious scope**
- Planning more features than historical velocity supports
- Underestimating integration complexity
- Ignoring testing and polish time

**Under-planned releases**
- Features too small to provide meaningful value
- Missing integration opportunities
- Inefficient resource utilization

**Dependency blindness**
- Not identifying cross-feature dependencies
- Planning dependent features in wrong order
- Missing external dependency coordination

**Communication gaps**
- Not aligning with stakeholder expectations
- Missing cross-team coordination
- Unclear success criteria

## Success Metrics

### **Release Planning Success**
- **Predictability**: Releases deliver on time ± 1 sprint
- **Value delivery**: Each release provides measurable user value
- **Team satisfaction**: Sustainable pace and achievable goals
- **Quality**: No critical post-release issues

### **Feature Completion Success**
- **Scope stability**: <10% scope change during release
- **Critical path**: No critical path delays >1 sprint
- **Integration**: Features work well together
- **Documentation**: Complete and accurate

## Tools and Integration

### **Automation Support**
- **Release manager**: `process/automation/release_manager.py`
- **Sprint coordination**: `process/automation/sprint_manager.py`
- **Feature tracking**: `process/automation/feature_status_updater.py`
- **Progress monitoring**: All status and dashboard commands

### **Human Process Integration**
- **Sprint planning**: Release context guides sprint work selection
- **Daily status**: Sprint work contributes to release progress
- **Roadmap planning**: Releases implement roadmap priorities
- **Stakeholder communication**: Release progress provides status updates

The release planning playbook provides the **strategic coordination** that transforms individual sprint work into **coherent product deliveries** that advance the overall roadmap.
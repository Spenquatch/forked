---
title: Playbook - Roadmap Planning
type: process
date: 2025-09-21
tags: [process, playbook, roadmap, strategy]
links: [./release-planning.md, ./sprint-planning.md, ../automation/roadmap_manager.py]
---

# Playbook - Roadmap Planning

## Purpose
Establish and maintain strategic direction through quarterly roadmap planning that coordinates releases, features, and team priorities over 3-12 month horizons.

## When
- **Quarterly planning**: Every 3 months (12-16 weeks)
- **Strategic shifts**: When market or technical priorities change
- **Annual planning**: Once per year for long-term vision
- **Ad-hoc**: When significant opportunities or challenges arise

## Pre-Planning Checklist
- [ ] Previous quarter retrospective completed
- [ ] Current release status assessed (`make release-status`)
- [ ] Feature portfolio reviewed (`make feature-summary`)
- [ ] Parking lot quarterly review completed (`make parking-review`)
- [ ] Backlog severity distribution analyzed (`make backlog-stats`)
- [ ] Team capacity and growth plans confirmed (80/20 model)
- [ ] Market/customer feedback incorporated
- [ ] Technical debt assessment completed

## Roadmap Planning Process

### 1. **Assess Current State**

```bash
# Review complete project status
make dashboard
make feature-summary      # Feature progress across all sprints
make release-list        # Current and planned releases
make roadmap            # Current roadmap state

# Review parking lot for strategic opportunities
make parking-review      # Quarterly review interface
make parking-list       # All categorized future ideas

# Analyze backlog patterns
make backlog-stats      # Severity distribution and trends
make backlog-list severity=P0,P1  # Critical issues impacting roadmap
```

**Analysis Questions**:
- What's our current velocity and capacity (considering 80/20 allocation)?
- What parking lot items are ready for roadmap promotion?
- Are P0/P1 issues impacting our strategic timeline?
- Which features are delivering value vs. which are struggling?
- What technical debt is slowing us down?
- Where are we ahead/behind strategic goals?

### 2. **Gather Strategic Inputs**

#### **Market & Customer Inputs**
- Customer feedback and feature requests
- Competitive landscape changes
- Market opportunities and threats
- User analytics and usage patterns

#### **Technical Inputs**
- Technical debt impact assessment
- Infrastructure and scalability needs
- Security and compliance requirements
- Developer productivity bottlenecks

#### **Business Inputs**
- Revenue and growth targets
- Resource allocation plans
- Strategic partnerships
- Regulatory or compliance changes

### 3. **Define Roadmap Horizons**

#### **Now (Current Quarter)**
**Criteria**: High confidence, well-defined, in progress
- Features currently in development
- Releases planned and scoped
- Clear delivery timelines

**Examples**:
- Complete authentication system (v1.2.0)
- Launch API v2 (v1.3.0)
- Performance optimization release (v1.2.1)

#### **Next (Following Quarter)**
**Criteria**: Defined direction, reasonable confidence, dependencies clear
- Features ready for planning
- Logical follow-on work from current quarter
- Clear value proposition

**Examples**:
- Advanced user permissions (depends on auth completion)
- Mobile API expansion (builds on API v2)
- Admin dashboard overhaul (after core features stable)

#### **Later (6-12 months)**
**Criteria**: Strategic direction, lower confidence, may change
- Major initiatives and platform investments
- Emerging opportunities
- Long-term technical improvements

**Examples**:
- Multi-tenant architecture
- International expansion features
- AI/ML integration platform

### 4. **Create/Update Roadmap**

```bash
# Create or update roadmap
make roadmap-create      # If starting fresh
# Edit roadmap/now-next-later.md

# Promote parking lot items to roadmap
make parking-promote item=FEAT-001 target=next
make parking-promote item=RESEARCH-002 target=later
make parking-archive item=OLD-001  # Archive stale ideas

# Validate roadmap
make roadmap-validate    # Check links and structure
```

#### **Roadmap Structure Best Practices**

**Now Section** (Next 3-4 months):
- Specific features with clear scope
- Critical P0/P1 backlog items incorporated
- Linked to actual feature documentation
- Realistic timelines based on historical velocity (80% capacity)
- Dependencies clearly identified

**Next Section** (3-6 months out):
- Promoted parking lot items with high value
- Directional features with emerging clarity
- P2 backlog items considered
- Logical dependencies from Now section
- Flexible scope that can adjust based on learnings

**Later Section** (6-12 months):
- Parking lot research items for exploration
- Strategic themes and major initiatives
- Platform investments and architectural work
- Emerging opportunities and research areas
- Low-priority backlog enhancements

### 5. **Map Features to Releases**

#### **Release Coordination Strategy**

**Theme-based releases**:
- Group related features into coherent releases
- Each release tells a story to users
- Features complement and reinforce each other

**Capability-based releases**:
- Build foundational capabilities first
- Layer advanced features on solid foundation
- Enable progressive user adoption

**Timeline-based releases**:
- Fixed release schedule (e.g., monthly, quarterly)
- Features fit into available timeline slots
- Predictable delivery rhythm

#### **Feature-to-Release Mapping**

```bash
# Plan next release based on feature readiness
make release-suggest version=v1.3.0    # See suggested features

# Create release plan
make release-plan version=v1.3.0 sprints=3

# Assign features to release
make release-add-feature release=v1.3.0 feature=user-permissions critical=true
make release-add-feature release=v1.3.0 feature=admin-dashboard
```

### 6. **Capacity and Timeline Planning**

#### **Capacity Assessment**

**Historical Analysis**:
- Team velocity trends over last 6 sprints
- Feature completion rates (80% planned work)
- P0/P1 reactive work consumption (20% allocation)
- Technical debt impact on velocity
- Time spent on maintenance vs new features

**Future Capacity Planning**:
- Planned work capacity: 80% of velocity
- Reserved for P0/P1: 20% of velocity
- Team growth or changes planned
- Known time off or commitments
- Learning curve for new technologies
- External dependency coordination time
- Parking lot item complexity assessment

#### **Timeline Reality Check**

**Validation Questions**:
- Does Now section fit in next 3-4 sprints realistically?
- Are Next section features properly dependency-ordered?
- Is there buffer for unknowns and technical debt?
- Can team capacity support the planned scope?

### 7. **Stakeholder Alignment**

#### **Internal Alignment**
- **Development team**: Technical feasibility and capacity
- **Product team**: User value and market timing
- **Business team**: Revenue impact and resource allocation
- **Support team**: Operational readiness and documentation

#### **External Communication**
- **Customers**: Feature availability and timeline expectations
- **Partners**: Integration timeline and API changes
- **Management**: Progress against strategic goals
- **Market**: Competitive positioning and differentiation

## Roadmap Maintenance

### **Monthly Roadmap Reviews** (Light touch)

```bash
# Quick status check
make release-status      # Current release progress
make feature-summary     # Feature advancement
```

**Review agenda**:
- Release progress vs plan
- Feature completion rates
- Emerging risks or opportunities
- Minor priority adjustments

### **Quarterly Roadmap Updates** (Strategic review)

**Full roadmap reassessment**:
- Move completed items to "Completed" section
- Promote Next → Now based on readiness
- Add new Later items based on strategic input
- Adjust timelines based on actual velocity

### **Emergency Roadmap Changes**

**Triggers for unplanned changes**:
- Critical security issues
- Major customer escalations
- Competitive threats
- Technical architecture discoveries

**Process for emergency changes**:
1. **Impact assessment**: What changes to current work?
2. **Stakeholder communication**: Who needs to know?
3. **Capacity reallocation**: What gets delayed?
4. **Timeline adjustment**: Update affected releases

## Advanced Roadmap Strategies

### **Dependency-Driven Planning**

**Strategy**: Plan features in dependency order
- Map all feature dependencies
- Ensure foundation features complete before dependent features
- Plan buffer time for integration between dependent features

**Example**: Platform roadmap
- **Q1**: Core API infrastructure
- **Q2**: Authentication and permissions (depends on API)
- **Q3**: User-facing features (depends on auth)
- **Q4**: Advanced features (depends on user features)

### **Risk-Driven Planning**

**Strategy**: Identify and plan around major risks
- **Technical risks**: New technology, architecture changes
- **Market risks**: Competitive pressure, changing requirements
- **Team risks**: Key person dependencies, skill gaps
- **Integration risks**: External systems, partner dependencies

**Risk Management Tactics**:
- **Early tackling**: Address highest-risk items first
- **Parallel paths**: Develop alternatives for high-risk items
- **Buffer allocation**: Extra time for high-uncertainty work
- **Stakeholder communication**: Regular risk status updates

### **Value Stream Optimization**

**Strategy**: Optimize for continuous value delivery
- **Frequent releases**: Smaller, more frequent releases
- **MVP approach**: Minimal viable features that can be enhanced
- **User feedback loops**: Regular user input to guide priorities
- **Data-driven decisions**: Use metrics to guide roadmap changes

## Roadmap Communication

### **Internal Roadmap Artifacts**

**Detailed roadmap** (`roadmap/now-next-later.md`):
- Complete feature list with links
- Sprint and release assignments
- Dependency mapping
- Technical implementation notes

**Executive summary** (quarterly presentation):
- High-level themes and goals
- Key milestones and timelines
- Resource requirements
- Success metrics

### **External Roadmap Artifacts**

**Customer roadmap** (quarterly communication):
- User-focused feature benefits
- General timeline expectations
- No technical implementation details
- Opportunity for customer input

**Partner roadmap** (API/integration timeline):
- Breaking changes timeline
- New integration opportunities
- Deprecation schedules
- Migration support plans

## Roadmap Anti-Patterns

### **❌ Common Mistakes**

**Over-detailed long-term planning**
- Planning features >6 months out in detail
- Committing to specific timelines too far ahead
- Missing market/technology evolution

**Under-planned near-term work**
- Vague Now section without clear scope
- Missing dependency identification
- Unrealistic timeline expectations

**Roadmap rigidity**
- Refusing to adjust based on learnings
- Treating roadmap as unchangeable commitment
- Missing emerging opportunities

**Communication misalignment**
- Different roadmaps for different audiences
- Overpromising timeline certainty
- Missing stakeholder input cycles

## Success Metrics

### **Roadmap Quality Metrics**
- **Accuracy**: Now section delivery rate >80%
- **Predictability**: Timeline accuracy ±1 sprint
- **Value delivery**: Each release measurably advances strategic goals
- **Stakeholder satisfaction**: Internal and external alignment

### **Strategic Metrics**
- **Market position**: Competitive feature parity or advantage
- **Technical health**: Technical debt manageable (<20% of capacity)
- **Team velocity**: Sustainable and improving development pace
- **User satisfaction**: Feature adoption and satisfaction scores

## Tools and Integration

### **Automation Support**
- **Roadmap manager**: `process/automation/roadmap_manager.py`
- **Release coordination**: `process/automation/release_manager.py`
- **Feature tracking**: `process/automation/feature_status_updater.py`
- **Progress monitoring**: Dashboard and status commands

### **Process Integration**
- **Release planning**: Roadmap priorities guide release feature selection
- **Sprint planning**: Release assignments guide sprint work selection
- **Daily work**: Sprint tasks implement roadmap vision
- **Retrospectives**: Release outcomes inform roadmap adjustments

## Troubleshooting

### **Roadmap Planning Issues**

**Too many high-priority items**
- Use scoring framework (value vs effort)
- Consider resource allocation vs trying to do everything
- Engage stakeholders in prioritization tradeoffs

**Unclear feature scope**
- Require feature overview completion before roadmap inclusion
- Use spike tasks to reduce uncertainty
- Break large features into smaller, clearer pieces

**Conflicting stakeholder priorities**
- Facilitate explicit prioritization discussions
- Use data and metrics to guide decisions
- Document decision rationale for future reference

**Timeline pressure**
- Reduce scope rather than extend timelines
- Identify minimum viable feature sets
- Communicate tradeoffs clearly to stakeholders

The roadmap planning playbook provides the **strategic coordination** that ensures all tactical work (sprints, tasks, features) advances toward **coherent long-term goals** while maintaining flexibility to adapt to changing conditions.
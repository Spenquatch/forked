---
title: Project Handbook Installation Guide
type: readme
date: 2025-09-18
tags: [installation, guide]
links: [docs/SYSTEM_GUIDE.md]
---

# Project Handbook

**Drop-in project management system for any repository.**

## 🚀 Quick Install

Add this handbook system to your existing project:

```bash
# Option 1: Clone into your project
cd your-project/
git clone <this-repo-url> project-handbook

# Option 2: Git submodule
git submodule add <this-repo-url> project-handbook

# Option 3: Download release
curl -L <release-url> | tar -xz -C project-handbook/
```

## 🎯 Getting Started

```bash
cd project-handbook/

# See all available commands
make help

# Start your first sprint
make sprint-plan

# Create your first feature
make feature-create name=my-feature

# Daily workflow
make daily              # End of each work day
make sprint-status      # Check progress anytime

# Task management
make task-create title="My Task" feature=my-feature decision=ADR-001 points=5
make task-list          # List all sprint tasks
make task-status id=TASK-001 status=doing  # Update when starting work

# Parking Lot - Future ideas and research
make parking-add type=features title="Social Login" desc="OAuth integration"
make parking-list       # Review all future ideas
make parking-review     # Quarterly review interface
make parking-promote item=FEAT-001 target=later  # Promote to roadmap

# Issue Backlog - Bugs and urgent requests
make backlog-add type=bug title="Login fails" severity=P1 desc="Critical issue"
make backlog-list       # Review open issues
make backlog-triage issue=BUG-001  # Generate AI analysis for P0 issues
make backlog-assign issue=BUG-001 sprint=current  # Assign to sprint (20% capacity)
make backlog-rubric     # Show P0-P4 severity guidelines
```

## 📚 Complete Documentation

| File | Purpose |
|------|---------|
| **[docs/SYSTEM_GUIDE.md](docs/SYSTEM_GUIDE.md)** | **Complete system overview and workflows** |
| [docs/CLAUDE.md](docs/CLAUDE.md) | Claude Code integration guide |
| [docs/CONVENTIONS.md](docs/CONVENTIONS.md) | Validation rules and schemas |
| [docs/SPRINT_SYSTEM.md](docs/SPRINT_SYSTEM.md) | Sprint system technical details |
| [docs/MAKEFILE_COMMANDS.md](docs/MAKEFILE_COMMANDS.md) | All commands reference |
| [docs/PARKING_LOT_SYSTEM.md](docs/PARKING_LOT_SYSTEM.md) | Parking lot management guide |
| [docs/BACKLOG_SYSTEM.md](docs/BACKLOG_SYSTEM.md) | Issue backlog and severity guide |
| [docs/workflow-diagram.md](docs/workflow-diagram.md) | Visual workflow diagrams |

## 🏗️ What You Get

### Daily Status System
- **Weekend-aware** automation (Monday-Friday)
- **Sprint metrics** and progress tracking
- **Blocker monitoring** with alerts

### Sprint Management
- **1-week sprints** with health indicators (🟢🟡🔴)
- **Story points** using Fibonacci sequence
- **Task dependencies** and validation
- **ASCII burndown charts** for visual progress
- **80/20 capacity allocation** (80% planned, 20% reactive)

### Feature Lifecycle
- **Complete scaffolding** for new features
- **Epic support** for multi-sprint features
- **Dependency-aware ordering** in status reports
- **Automated status** generation

### Parking Lot System
- **Future ideas** categorized by type
- **Quarterly review** process for promotion
- **Integration** with roadmap planning
- **Archive** outdated concepts automatically

### Issue Backlog Management
- **P0-P4 severity** classification system
- **AI-powered triage** for critical issues
- **Sprint assignment** with capacity awareness
- **Escalation workflows** for P0 incidents

### Automation & Validation
- **35+ Make commands** for all operations
- **Git hooks** for quality gates
- **Comprehensive validation** of all documentation
- **Roadmap management** with link normalization

## 🎮 Example Sprint Workflow

```bash
# Monday: Plan Sprint
make sprint-plan          # Create weekly plan with tasks/ directory
make task-create title="Setup Auth" feature=auth decision=ADR-001 points=8
# Create all sprint tasks with detailed directories

# Tuesday-Thursday: Execute
make task-status id=TASK-001 status=doing  # When starting work
make daily               # Update daily status with task progress
make sprint-status       # Check health indicators
make burndown           # View progress visualization

# Friday: Close Sprint
make sprint-close        # Generate retrospective with velocity
make feature-list       # Update feature stages based on completed tasks
```

## 📊 Visual Dashboard

```bash
make dashboard
```
```
════════════════════════════════════════════════
           PROJECT HANDBOOK DASHBOARD
════════════════════════════════════════════════

Sprint: SPRINT-2025-W38
Day 3 of 5
Health: 🟢 GREEN - On track
Progress: 15/30 points (50%)

Recent Daily Status:
  2025-09-16.md
  2025-09-17.md
  2025-09-18.md

Features:
📦 user-auth              Stage: development
🎯 platform-overhaul      Stage: planning
📦 api-endpoints          Stage: complete

Validation: ✅ 0 errors
════════════════════════════════════════════════
```

## 🔄 Integration with Your Project

This handbook system is designed to **coexist** with your existing project:

```
your-project/
├── src/                 # Your application code
├── tests/               # Your test suite
├── package.json         # Your dependencies
├── README.md            # Your project README
└── project-handbook/    # Project management (this system)
    ├── features/        # Feature specs for YOUR project
    ├── sprints/         # Sprint tracking with detailed task directories
    ├── status/          # Generated dashboards and metrics
    ├── roadmap/         # YOUR project roadmap
    └── releases/        # YOUR project releases
```

## 🎪 Key Features

- ✅ **Text-based**: Git-friendly, diff-friendly, merge-friendly
- ✅ **Automated**: Weekend-aware daily status, sprint health monitoring
- ✅ **Validated**: Comprehensive checks for consistency and quality
- ✅ **Visual**: ASCII burndown charts, health indicators, dashboard
- ✅ **Flexible**: Regular features and epic features, configurable workflows
- ✅ **Integrated**: Make commands for everything, git hooks available

## 📞 Support

- **Full Documentation**: Start with [docs/SYSTEM_GUIDE.md](docs/SYSTEM_GUIDE.md)
- **Command Reference**: Run `make help` or see [docs/MAKEFILE_COMMANDS.md](docs/MAKEFILE_COMMANDS.md)
- **Process Guides**: Check `process/playbooks/` for step-by-step guides
- **Troubleshooting**: See [docs/SYSTEM_GUIDE.md#troubleshooting](docs/SYSTEM_GUIDE.md#troubleshooting)

---

**Ready to start?** Run `make help` to see all available commands!
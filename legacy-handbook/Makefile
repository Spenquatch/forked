# Project Handbook Makefile
.PHONY: help daily sprint-plan sprint-close sprint-status sprint-tasks burndown validate status clean feature-list feature-create roadmap roadmap-show task-create task-list task-show task-status release-plan release-status release-add-feature release-suggest release-list release-close parking-add parking-list parking-review parking-promote backlog-add backlog-list backlog-triage backlog-assign backlog-rubric

# Default target
help:
	@echo "Project Handbook Management Commands"
	@echo ""
	@echo "Daily Operations:"
	@echo "  make daily          - Generate daily status (skips weekends)"
	@echo "  make daily-force    - Force daily status generation"
	@echo "  make daily-check    - Check if daily status is current"
	@echo ""
	@echo "Sprint Management:"
	@echo "  make sprint-plan    - Create new sprint plan (Monday)"
	@echo "  make sprint-status  - Show current sprint health"
	@echo "  make sprint-tasks   - List all tasks in current sprint"
	@echo "  make burndown       - Generate burndown chart"
	@echo "  make sprint-close   - Close sprint with retrospective (Friday)"
	@echo ""
	@echo "Task Management:"
	@echo "  make task-create title='X' feature=Y decision=Z [points=5] [owner=@alice] [prio=P1]"
	@echo "  make task-list      - List current sprint tasks"
	@echo "  make task-show id=TASK-XXX - Show task details"
	@echo "  make task-status id=TASK-XXX status=doing - Update task status"
	@echo ""
	@echo "Feature Management:"
	@echo "  make feature-list   - List all features and their status"
	@echo "  make feature-create name=X [epic=true] [owner=@alice] [stage=proposed]"
	@echo "  make feature-status name=X stage=Y - Update feature status"
	@echo "  make feature-update-status - Auto-update all feature status files from sprints"
	@echo "  make feature-summary - Show feature progress with sprint data"
	@echo ""
	@echo "Release Management:"
	@echo "  make release-plan version=v1.2.0 [sprints=3] [start=SPRINT-2025-W39]"
	@echo "  make release-status - Show current release progress"
	@echo "  make release-add-feature release=v1.2.0 feature=auth [epic=true] [critical=true]"
	@echo "  make release-suggest version=v1.2.0 - Suggest features for release"
	@echo "  make release-list   - List all releases"
	@echo ""
	@echo "Roadmap & Planning:"
	@echo "  make roadmap        - Show current roadmap"
	@echo "  make roadmap-create - Create roadmap template"
	@echo "  make roadmap-validate - Validate roadmap links"
	@echo ""
	@echo "Parking Lot (Future Ideas):"
	@echo "  make parking-add type=features title='X' desc='Y' - Add item to parking lot"
	@echo "  make parking-list   - List all parking lot items"
	@echo "  make parking-review - Quarterly review interface"
	@echo "  make parking-promote item=X target=later - Promote to roadmap"
	@echo ""
	@echo "Issue Backlog (Bugs & Urgents):"
	@echo "  make backlog-add type=bug title='X' severity=P1 desc='Y' - Add issue"
	@echo "  make backlog-list   - List all backlog issues"
	@echo "  make backlog-triage issue=BUG-001 - Generate AI triage analysis"
	@echo "  make backlog-assign issue=BUG-001 sprint=current - Assign to sprint"
	@echo "  make backlog-rubric - Show severity rubric (P0-P4)"
	@echo ""
	@echo "Validation & Status:"
	@echo "  make validate       - Run all validation checks"
	@echo "  make status         - Generate project status with feature updates"
	@echo "  make check-all      - Run validate + status"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          - Clean generated files"
	@echo "  make test-system    - Test all automation scripts"
	@echo "  make install-hooks  - Install git hooks"

# Daily operations
daily:
	@python3 process/automation/daily_status_check.py --generate

daily-force:
	@python3 process/automation/daily_status_check.py --generate --force

daily-check:
	@python3 process/automation/daily_status_check.py --check-only --verbose

# Feature management
feature-list:
	@python3 process/automation/feature_manager.py --list

feature-create:
ifndef name
	@echo "❌ Usage: make feature-create name=my-feature [epic=true] [owner=@alice] [stage=proposed]"
	@exit 1
endif
	@python3 process/automation/feature_manager.py --create $(name) $(if $(epic),--epic,) $(if $(owner),--owner $(owner),) $(if $(stage),--stage $(stage),)

feature-status:
ifndef name
	@echo "❌ Usage: make feature-status name=feature-name stage=new-stage"
	@exit 1
endif
ifndef stage
	@echo "❌ Usage: make feature-status name=feature-name stage=new-stage"
	@exit 1
endif
	@python3 process/automation/feature_manager.py --update-status $(name) $(stage)

feature-update-status:
	@python3 process/automation/feature_status_updater.py --update-all

feature-summary:
	@python3 process/automation/feature_status_updater.py --summary

# Roadmap management
roadmap:
	@python3 process/automation/roadmap_manager.py --show

roadmap-create:
	@python3 process/automation/roadmap_manager.py --create

roadmap-validate:
	@python3 process/automation/roadmap_manager.py --validate

# Release management
release-plan:
ifndef version
	@echo "❌ Usage: make release-plan version=v1.2.0 [sprints=3] [start=SPRINT-2025-W39]"
	@exit 1
endif
	@python3 process/automation/release_manager.py --plan $(version) $(if $(sprints),--sprints $(sprints),) $(if $(start),--start-sprint $(start),)

release-status:
	@python3 process/automation/release_manager.py --status current

release-add-feature:
ifndef release
	@echo "❌ Usage: make release-add-feature release=v1.2.0 feature=feature-name [epic=true] [critical=true]"
	@exit 1
endif
ifndef feature
	@echo "❌ Usage: make release-add-feature release=v1.2.0 feature=feature-name [epic=true] [critical=true]"
	@exit 1
endif
	@python3 process/automation/release_manager.py --add-feature $(release) $(feature) $(if $(epic),--epic,) $(if $(critical),--critical,)

release-suggest:
ifndef version
	@echo "❌ Usage: make release-suggest version=v1.2.0"
	@exit 1
endif
	@python3 process/automation/release_manager.py --suggest $(version)

release-list:
	@python3 process/automation/release_manager.py --list

release-close:
ifndef version
	@echo "❌ Usage: make release-close version=v1.2.0"
	@exit 1
endif
	@python3 process/automation/release_manager.py --close $(version)

# Sprint management
sprint-plan:
	@python3 process/automation/sprint_manager.py --plan
	@echo "Sprint planned! Don't forget to:"
	@echo "  1. Review and update sprint goals"
	@echo "  2. Confirm task assignments"
	@echo "  3. Run 'make daily' to start tracking"

sprint-status:
	@python3 process/automation/sprint_manager.py --status

burndown:
	@python3 process/automation/sprint_manager.py --burndown

sprint-tasks:
	@python3 process/automation/task_manager.py --list

sprint-close:
	@python3 process/automation/sprint_manager.py --close
	@echo "Sprint closed! Next steps:"
	@echo "  1. Review retrospective"
	@echo "  2. Update roadmap if needed"
	@echo "  3. Run 'make sprint-plan' on Monday"

sprint-capacity:
	@python3 process/automation/sprint_manager.py --capacity

# Task management
task-create:
ifndef title
	@echo "❌ Usage: make task-create title='Task Name' feature=feature-name decision=ADR-001 [points=5] [owner=@alice] [prio=P1]"
	@exit 1
endif
ifndef feature
	@echo "❌ Usage: make task-create title='Task Name' feature=feature-name decision=ADR-001 [points=5] [owner=@alice] [prio=P1]"
	@exit 1
endif
ifndef decision
	@echo "❌ Usage: make task-create title='Task Name' feature=feature-name decision=ADR-001 [points=5] [owner=@alice] [prio=P1]"
	@exit 1
endif
	@python3 process/automation/task_manager.py --create --title "$(title)" --feature $(feature) --decision $(decision) $(if $(points),--points $(points),) $(if $(owner),--owner $(owner),) $(if $(prio),--prio $(prio),)

task-list:
	@python3 process/automation/task_manager.py --list

task-show:
ifndef id
	@echo "❌ Usage: make task-show id=TASK-001"
	@exit 1
endif
	@python3 process/automation/task_manager.py --show $(id)

task-status:
ifndef id
	@echo "❌ Usage: make task-status id=TASK-001 status=doing"
	@exit 1
endif
ifndef status
	@echo "❌ Usage: make task-status id=TASK-001 status=doing"
	@exit 1
endif
	@python3 process/automation/task_manager.py --update-status $(id) $(status)

# Validation and status
validate:
	@python3 process/checks/validate_docs.py

status:
	@python3 process/automation/generate_project_status.py

check-all: validate status
	@echo "✅ All checks complete"

# Test the system
test-system:
	@echo "Testing validation..."
	@python3 process/checks/validate_docs.py
	@echo ""
	@echo "Testing status generation..."
	@python3 process/automation/generate_project_status.py
	@echo ""
	@echo "Testing daily status check..."
	@python3 process/automation/daily_status_check.py --check-only --verbose || echo "  (Expected - no daily status yet)"
	@echo ""
	@echo "Testing sprint status..."
	@python3 process/automation/sprint_manager.py --status
	@echo ""
	@echo "Testing feature management..."
	@python3 process/automation/feature_manager.py --list
	@echo ""
	@echo "Testing roadmap..."
	@python3 process/automation/roadmap_manager.py --show
	@echo ""
	@echo "✅ All systems operational"

# Utilities
clean:
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@echo "Cleaned Python cache files"

# Quick status dashboard
dashboard:
	@echo "════════════════════════════════════════════════"
	@echo "           PROJECT HANDBOOK DASHBOARD           "
	@echo "════════════════════════════════════════════════"
	@echo ""
	@python3 process/automation/sprint_manager.py --status
	@echo ""
	@echo "Recent Daily Status:"
	@ls -1 status/daily/*.md 2>/dev/null | tail -3 || echo "  No daily status files yet"
	@echo ""
	@echo "Validation:"
	@python3 process/checks/validate_docs.py
	@echo ""
	@echo "════════════════════════════════════════════════"

# Install git hooks
install-hooks:
	@echo "#!/bin/bash" > .git/hooks/post-commit
	@echo "python3 process/automation/daily_status_check.py --check-only" >> .git/hooks/post-commit
	@chmod +x .git/hooks/post-commit
	@echo "#!/bin/bash" > .git/hooks/pre-push
	@echo "python3 process/checks/validate_docs.py" >> .git/hooks/pre-push
	@chmod +x .git/hooks/pre-push
	@echo "Git hooks installed!"

# Parking Lot Management
parking-add:
ifndef type
	@echo "❌ Usage: make parking-add type=features title='Title' desc='Description' [owner=@alice]"
	@exit 1
endif
ifndef title
	@echo "❌ Usage: make parking-add type=features title='Title' desc='Description' [owner=@alice]"
	@exit 1
endif
	@python3 process/automation/parking_lot_manager.py add --type $(type) --title "$(title)" $(if $(desc),--desc "$(desc)",) $(if $(owner),--owner $(owner),) $(if $(tags),--tags "$(tags)",)

parking-list:
	@python3 process/automation/parking_lot_manager.py list $(if $(category),--category $(category),) $(if $(format),--format $(format),)

parking-review:
	@python3 process/automation/parking_lot_manager.py review

parking-promote:
ifndef item
	@echo "❌ Usage: make parking-promote item=FEAT-001 target=later"
	@exit 1
endif
	@python3 process/automation/parking_lot_manager.py promote --item $(item) $(if $(target),--target $(target),--target later)

# Issue Backlog Management
backlog-add:
ifndef type
	@echo "❌ Usage: make backlog-add type=bug title='Title' severity=P1 desc='Description'"
	@exit 1
endif
ifndef title
	@echo "❌ Usage: make backlog-add type=bug title='Title' severity=P1 desc='Description'"
	@exit 1
endif
ifndef severity
	@echo "❌ Usage: make backlog-add type=bug title='Title' severity=P1 desc='Description'"
	@exit 1
endif
	@python3 process/automation/backlog_manager.py add --type $(type) --title "$(title)" --severity $(severity) $(if $(desc),--desc "$(desc)",) $(if $(owner),--owner $(owner),) $(if $(impact),--impact "$(impact)",) $(if $(workaround),--workaround "$(workaround)",)

backlog-list:
	@python3 process/automation/backlog_manager.py list $(if $(severity),--severity $(severity),) $(if $(category),--category $(category),) $(if $(format),--format $(format),)

backlog-triage:
ifndef issue
	@echo "❌ Usage: make backlog-triage issue=BUG-001"
	@exit 1
endif
	@python3 process/automation/backlog_manager.py triage --issue $(issue)

backlog-assign:
ifndef issue
	@echo "❌ Usage: make backlog-assign issue=BUG-001 [sprint=current]"
	@exit 1
endif
	@python3 process/automation/backlog_manager.py assign --issue $(issue) $(if $(sprint),--sprint $(sprint),--sprint current)

backlog-rubric:
	@python3 process/automation/backlog_manager.py rubric

backlog-stats:
	@python3 process/automation/backlog_manager.py stats

.DEFAULT_GOAL := help
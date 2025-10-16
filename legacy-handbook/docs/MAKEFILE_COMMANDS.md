# Complete Makefile Commands Reference

## Overview
All Python scripts in the project handbook are now integrated with convenient Make commands. No need to remember long script paths or arguments!

## New Scripts Added

### 🎯 Feature Manager (`process/automation/feature_manager.py`)
- Create new features with complete directory structure
- List all features with status indicators
- Update feature stages
- Support for epic features

### 🗺️ Roadmap Manager (`process/automation/roadmap_manager.py`)
- Display formatted roadmap
- Create roadmap templates
- Validate roadmap links

### 📊 Enhanced Status Generator (`status/generate_project_status.py`)
- Dependency-aware feature ordering
- Enhanced with sprint and epic support
- Replaces simple status generator as default

## Complete Command Reference

### Daily Operations
```bash
make daily          # Generate daily status (skips weekends)
make daily-force    # Force daily status generation (even weekends)
make daily-check    # Check if daily status is current
```

### Sprint Management
```bash
make sprint-plan    # Create new sprint plan (Monday)
make sprint-status  # Show current sprint health indicators
make burndown       # Generate ASCII burndown chart
make sprint-close   # Close sprint with retrospective (Friday)
```

### Feature Management
```bash
make feature-list                    # List all features and their status
make feature-create name=my-feature  # Create new regular feature
make feature-create name=big-thing epic=true  # Create epic feature
make feature-status name=my-feature stage=development  # Update status
```

### Roadmap & Planning
```bash
make roadmap          # Show current roadmap with pretty formatting
make roadmap-create   # Create roadmap template
make roadmap-validate # Validate roadmap links
```

### Parking Lot Management (Future Ideas)
```bash
make parking-add type=features title='Social Login' desc='OAuth integration'
make parking-list           # List all parking lot items by category
make parking-review         # Quarterly review interface with promotion options
make parking-promote item=FEAT-001 target=later  # Promote item to roadmap
```

### Issue Backlog (Bugs & Urgent Issues)
```bash
make backlog-add type=bug title='Login Bug' severity=P1 desc='Critical login failure'
make backlog-list           # List all backlog issues with severity filtering
make backlog-triage issue=BUG-001  # Generate AI triage analysis and recommendations
make backlog-assign issue=BUG-001 sprint=current  # Assign issue to sprint (20% capacity)
make backlog-rubric         # Display P0-P4 severity classification rubric
```

### Validation & Status
```bash
make validate       # Run all validation checks
make status         # Generate project status with feature updates
make check-all      # Run validate + status together
```

### Utilities
```bash
make clean          # Clean generated files
make test-system    # Test all automation scripts
make install-hooks  # Install git hooks for automation
make dashboard      # Show complete project dashboard
```

## Key Improvements

### ✅ All Scripts Integrated
- Every Python script now has a make command
- No more remembering file paths or arguments
- Consistent interface across all tools

### ✅ Enhanced Feature Management
- Create features with full directory structure in one command
- Epic support with visual indicators (🎯 vs 📦)
- Automatic file templates with proper front matter

### ✅ Better Error Handling
- Proper parameter validation
- Helpful error messages with usage examples
- Graceful handling of missing files

### ✅ Visual Indicators
- 🎯 for epic features
- 📦 for regular features
- 🟢🟡🔴 for sprint health
- Clear section headers in roadmap

## Usage Examples

### Creating a New Feature
```bash
# Regular feature
make feature-create name=user-authentication

# Epic feature (spans multiple sprints)
make feature-create name=platform-architecture epic=true
```

### 80/20 Capacity Management Workflow
```bash
# During sprint planning (80% planned, 20% reactive)
make sprint-plan         # Allocates 80% to planned work
make backlog-list severity=P0  # Check critical issues
make backlog-list severity=P1  # Check high priority issues

# Assign P1 issues to 20% reactive capacity
make backlog-assign issue=BUG-001 sprint=current

# If P0 issue appears mid-sprint
make backlog-add type=bug title="Production down" severity=P0 desc="Database failure"
make backlog-triage issue=BUG-P0-001  # Get AI recommendations
make backlog-assign issue=BUG-P0-001 sprint=current  # Interrupt immediately
```

### Sprint Workflow
```bash
# Monday morning
make sprint-plan
make backlog-list severity=P1  # Review high-priority issues for 20% capacity

# During the week
make daily
make sprint-status
make burndown

# Friday evening
make sprint-close
```

### Status & Validation
```bash
# Quick health check
make dashboard

# Full validation
make check-all

# Just roadmap
make roadmap
```

## File Organization

All scripts are now organized under:
- `process/automation/` - Automation scripts
- `process/checks/` - Validation scripts
- `status/` - Status generation scripts

## Integration with Git Hooks

The `make install-hooks` command sets up:
- **post-commit**: Checks if daily status is needed
- **pre-push**: Runs validation to prevent broken commits

## Backwards Compatibility

- Single `generate_project_status.py` provides all status generation functionality
- All existing scripts continue to work directly
- Make commands are convenience wrappers, not replacements

The system is now fully integrated and much easier to use!
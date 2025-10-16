---
title: Project Handbook Configuration Guide
type: configuration
date: 2025-09-21
tags: [configuration, validation, customization]
links: [../process/checks/validation_rules.json]
---

# Configuration Guide

The project handbook system is **highly customizable** through the `process/checks/validation_rules.json` file. You can granularly control validation rules, automation behavior, and system defaults.

## Configuration File Location

**File**: `process/checks/validation_rules.json`

All automation scripts and validation logic read from this file for their behavior settings.

## Configuration Sections

### 📋 **Validation Settings**

```json
"validation": {
  "require_front_matter": true,        // Require YAML front matter on all .md files
  "skip_docs_directory": true,         // Skip validation in docs/ (system docs)
  "max_validation_issues": 100,        // Maximum issues to report
  "validation_timeout_ms": 5000        // Timeout for validation run
}
```

### 🎯 **Sprint Task Settings**

```json
"sprint_tasks": {
  "require_task_yaml": true,                    // Require task.yaml in each task directory
  "require_story_points": true,                 // Require story points on all tasks
  "require_task_directory_files": true,        // Require complete task directory structure
  "required_task_files": [                     // Files that must exist in task directories
    "README.md", "steps.md", "commands.md",
    "checklist.md", "validation.md"
  ],
  "optional_task_files": ["references.md", "source/"],
  "require_single_decision_per_task": true,    // Each task must reference exactly one ADR/FDR
  "enforce_sprint_scoped_dependencies": true,  // Dependencies only within current sprint
  "required_task_fields": [                    // Required fields in task.yaml
    "id", "title", "feature", "decision",
    "owner", "status", "story_points",
    "prio", "due", "acceptance"
  ]
}
```

### 📊 **Story Points Settings**

```json
"story_points": {
  "validate_fibonacci_sequence": true,         // Enforce Fibonacci sequence
  "allowed_story_points": [1, 2, 3, 5, 8, 13, 21],  // Valid story point values
  "default_story_points": 5,                   // Default when creating tasks
  "max_story_points": 21,                      // Maximum allowed story points
  "warn_large_tasks": true,                    // Warn on large tasks
  "large_task_threshold": 13                   // Threshold for "large" warning
}
```

### 📝 **Task Status Settings**

```json
"task_status": {
  "allowed_statuses": ["todo", "doing", "review", "done", "blocked"],
  "require_blocked_reason": true,              // Require reason when status=blocked
  "validate_status_transitions": true         // Validate proper status transitions
}
```

### 📅 **Daily Status Settings**

```json
"daily_status": {
  "require_weekdays_only": true,               // Daily status only on work days
  "weekend_days": [5, 6],                      // Saturday=5, Sunday=6
  "skip_weekends": true,                       // Auto-skip weekend generation
  "max_hours_without_update": 24,              // Alert threshold for overdue status
  "require_daily_on_task_changes": true,      // Require daily when tasks change
  "monday_weekend_summary": true,              // Special Monday template
  "friday_week_wrapup": true                   // Special Friday template
}
```

### 🏃 **Sprint Management Settings**

```json
"sprint_management": {
  "sprint_duration_days": 5,                   // Work days per sprint (Mon-Fri)
  "sprint_start_day": 0,                       // Monday=0, Tuesday=1, etc.
  "sprint_buffer_percentage": 20,              // Reserve % capacity for unknowns
  "health_check_thresholds": {
    "blocked_percentage_red": 30,              // Red alert if >30% points blocked
    "progress_percentage_red": 50,             // Red alert if <50% progress by check day
    "progress_check_day": 3                    // Wednesday=3 (check day)
  },
  "require_sprint_retrospective": true,        // Require retrospective on close
  "track_velocity_metrics": true               // Calculate velocity in retrospectives
}
```

### 🐛 **Backlog System Settings**

```json
"backlog_system": {
  "severity_levels": ["P0", "P1", "P2", "P3", "P4"],  // Issue severity classifications
  "default_severity": "P2",                            // Default severity for new issues
  "ai_triage_threshold": "P0",                        // Trigger AI triage for this level
  "reactive_capacity_percentage": 20,                 // Sprint capacity for P0/P1 issues
  "escalation_thresholds": {
    "P0_response_time_minutes": 15,                   // Max response time for P0
    "P1_response_time_hours": 4,                      // Max response time for P1
    "P2_response_time_days": 2                        // Max response time for P2
  },
  "ai_triage_model": "gpt-4",                        // AI model for triage analysis
  "require_triage_for_p0": true                      // Mandatory triage for P0 issues
}
```

### 🚗 **Parking Lot Settings**

```json
"parking_lot": {
  "categories": ["features", "research", "technical-debt", "ideas"],
  "default_category": "ideas",                        // Default category for new items
  "review_cycle_months": 3,                          // Quarterly review cycle
  "auto_archive_months": 12,                         // Archive after 12 months inactive
  "promotion_targets": ["now", "next", "later"],     // Valid roadmap targets
  "require_business_case_for_promotion": true        // Require justification
}
```

### 🎯 **Feature Settings**

```json
"features": {
  "auto_update_feature_status": true,          // Auto-update feature status from sprints
  "feature_status_update_frequency": "on_status_generation",
  "require_feature_stage": true,               // Require stage field in features
  "allowed_feature_stages": [                  // Valid feature lifecycle stages
    "proposed", "approved", "developing",
    "complete", "live", "deprecated"
  ],
  "epic_max_sprints": 4,                       // Maximum sprints for epic features
  "validate_feature_dependencies": true,       // Validate feature dependency chains
  "support_backlog_references": true,         // Allow backlog_items field
  "support_parking_lot_origin": true          // Allow parking_lot_origin field
}
```

### 📦 **Release Settings**

```json
"releases": {
  "min_sprints_per_release": 2,               // Minimum sprints for a release
  "max_sprints_per_release": 4,               // Maximum sprints for a release
  "require_release_features": true,            // Releases must have assigned features
  "track_critical_path": true,                // Track critical path features
  "validate_release_timeline": true,          // Validate release timelines
  "auto_update_release_progress": true        // Auto-update release progress
}
```

### 🗺️ **Roadmap Settings**

```json
"roadmap": {
  "normalize_links": true,                     // Auto-convert [../path] to [../path](../path)
  "validate_roadmap_links": true,              // Check that roadmap links resolve
  "require_now_next_later_sections": true     // Require standard roadmap sections
}
```

### 📋 **ADR/FDR Settings**

```json
"adr_fdr": {
  "check_adr_id_matches_filename": true,       // ADR-001 must be in 0001-*.md file
  "check_adr_superseded_by": true,             // Validate supersession chains
  "require_decision_before_tasks": true,      // Tasks must reference existing decisions
  "allowed_decision_statuses": [               // Valid decision lifecycle states
    "draft", "accepted", "rejected", "superseded"
  ]
}
```

### 🤖 **Automation Settings**

```json
"automation": {
  "enable_git_hooks": false,                   // Install git hooks for automation
  "enable_notifications": false,               // Enable Slack/Discord notifications
  "notification_webhook": "",                  // Webhook URL for notifications
  "blocker_escalation_hours": 24              // Hours before escalating blockers
}
```

## How to Customize

### Example: Different Story Point Scale

If your team prefers T-shirt sizing:
```json
"story_points": {
  "validate_fibonacci_sequence": false,
  "allowed_story_points": [1, 2, 4, 8, 16],
  "default_story_points": 4
}
```

### Example: 4-Day Work Week

```json
"sprint_management": {
  "sprint_duration_days": 4,
  "sprint_start_day": 1        // Start Tuesday instead of Monday
},
"daily_status": {
  "weekend_days": [4, 5, 6]    // Friday=4, Saturday=5, Sunday=6
}
```

### Example: Relaxed Validation

```json
"sprint_tasks": {
  "require_task_directory_files": false,      // Don't require all task files
  "required_task_files": ["README.md"],       // Only require README
  "enforce_sprint_scoped_dependencies": false // Allow cross-sprint dependencies
}
```

### Example: Disable Features

```json
"features": {
  "auto_update_feature_status": false         // Disable auto-updating features
},
"roadmap": {
  "normalize_links": false                    // Disable link normalization
}
```

## Configuration Effects

### On Validation
- Changes to validation rules immediately affect `make validate`
- Invalid configurations fall back to safe defaults
- Warnings show what configuration is being used

### On Task Creation
- Default story points used in `make task-create`
- Allowed story point values enforced
- Task directory structure follows required_task_files

### On Sprint Health
- Health thresholds configurable for team tolerance
- Progress check timing adjustable
- Health warnings show actual vs configured thresholds

### On Daily Status
- Weekend behavior completely configurable
- Special templates can be disabled
- Update frequency adjustable

## Best Practices

### 🟢 **Recommended Customizations**
- **Story point scale**: Match your team's estimation style
- **Health thresholds**: Adjust for team risk tolerance
- **Work week**: Configure for your actual work schedule
- **Required files**: Adjust task directory requirements

### ⚠️ **Use Caution With**
- **Disabling validation**: Can lead to inconsistent data
- **Cross-sprint dependencies**: Can create coordination issues
- **Removing required fields**: May break automation
- **Extreme health thresholds**: May miss real issues

### ❌ **Don't Disable**
- **Front matter validation**: Breaks automation and status generation
- **Sprint task validation**: Core to the sprint system
- **Decision references**: Critical for traceability

## Testing Configuration Changes

```bash
# After changing validation_rules.json:
make validate           # See if validation behavior changed
make task-create title="Test" feature=test decision=ADR-001    # Test defaults
make sprint-status      # See if health thresholds changed
```

## Configuration Backup

**Backup your configuration**:
```bash
cp process/checks/validation_rules.json process/checks/validation_rules.backup.json
```

**Restore defaults** (if needed):
```bash
# The scripts include safe defaults if the config file is missing or broken
```

The configuration system allows you to **tune the project handbook** to match your team's specific needs while maintaining the core functionality and automation benefits.
---
title: Installation Verification
type: verification
date: 2025-09-18
tags: [installation, testing]
links: [README.md, docs/SYSTEM_GUIDE.md]
---

# Installation Verification

## Quick System Check

After installing the project handbook in your repository, run these commands to verify everything works:

```bash
cd project-handbook/

# 1. Test basic commands
make help                    # Should show all available commands
make validate               # Should show 0 errors for clean install
make feature-list           # Should show any existing features

# 2. Test sprint system
make sprint-status          # Should show current sprint info
make burndown              # Should show ASCII burndown chart

# 3. Test feature management
make feature-create name=test-feature    # Should create complete structure
make feature-list                        # Should show new feature
rm -rf features/test-feature            # Clean up test

# 4. Test status generation
make status                # Should generate current.json
make dashboard            # Should show project overview

# 5. Test roadmap
make roadmap              # Should show current roadmap
make roadmap-validate     # Should validate links

# 6. Test backlog system
make backlog-add type=bug title="Test Bug" severity=P2 desc="Test issue"
make backlog-list         # Should show the test bug
make backlog-rubric       # Should show P0-P4 severity guidelines
# Clean up test
rm -rf backlog/bugs/BUG-P2-*

# 7. Test parking lot system
make parking-add type=features title="Test Feature" desc="Test idea"
make parking-list         # Should show the test feature
# Clean up test
rm -rf parking-lot/features/FEAT-*

# 8. Full system test
make test-system          # Should test all components
```

## Expected Results

### ✅ Successful Installation
```
✅ All commands execute without errors
✅ Features can be created and listed
✅ Sprint status shows current week
✅ Validation passes with 0 errors
✅ Status generation works
✅ Dashboard displays properly
```

### 📁 Directory Structure Created
```
your-project/
└── project-handbook/           # ← This system
    ├── README.md              # Installation guide
    ├── Makefile               # All commands
    ├── docs/                  # System documentation
    │   ├── SYSTEM_GUIDE.md    # Complete guide
    │   ├── CLAUDE.md          # Claude integration
    │   └── ...                # Other docs
    ├── process/               # Core system
    │   ├── automation/        # Scripts
    │   ├── checks/            # Validation
    │   └── playbooks/         # Process guides
    ├── features/              # Your features (initially empty/samples)
    ├── sprints/               # Your sprints (created as needed)
    ├── execution/             # Your execution phases
    ├── status/                # Generated files
    ├── roadmap/               # Your roadmap
    └── releases/              # Your releases
```

## Customization After Install

### 1. Update for Your Team
```bash
# Create your first real feature
make feature-create name=core-functionality

# Set up your roadmap
make roadmap-create
# Edit roadmap/now-next-later.md

# Plan your first sprint
make sprint-plan
# Edit the generated sprint plan
```

### 2. Configure Automation
```bash
# Install git hooks (optional)
make install-hooks

# Test daily status (will auto-skip weekends)
make daily

# Check everything works
make dashboard
```

### 3. Documentation
- Read [docs/SYSTEM_GUIDE.md](docs/SYSTEM_GUIDE.md) for complete workflows
- Review [docs/CONVENTIONS.md](docs/CONVENTIONS.md) for validation rules
- Check [docs/MAKEFILE_COMMANDS.md](docs/MAKEFILE_COMMANDS.md) for all commands

## Troubleshooting

### Common Issues

**Command not found**
```bash
# Make sure you're in the project-handbook directory
cd project-handbook/
make help
```

**Validation errors**
```bash
make validate
# Check status/validation.json for specific issues
# Most common: missing front matter in markdown files
```

**Python errors**
```bash
# Check Python version (3.7+ required)
python3 --version

# Test individual scripts
python3 process/checks/validate_docs.py
```

**Missing features/sprints**
```bash
# Create initial sprint
make sprint-plan

# Create first feature
make feature-create name=starter-feature
```

## Integration with Your Project

The handbook system is designed to coexist with your existing project without interference:

- **No conflicts**: All files are in `project-handbook/` subdirectory
- **Git-friendly**: Text files that diff and merge well
- **Optional**: Use as much or as little as you want
- **Portable**: Easy to remove or migrate

## Success Criteria

Installation is successful when:
- [ ] `make help` shows all commands
- [ ] `make validate` shows 0 errors
- [ ] `make dashboard` displays project overview
- [ ] `make feature-create name=test` works
- [ ] All automation scripts execute without errors

If all checks pass, your project handbook is ready to use!
# Academic Research Repository

This repository hosts the collaborative work for the Academic Research Paper Repository & Citation Network project.

## Automation Scripts Guide

### sync_subfolder.sh
- Purpose: Sync latest files across contributor folders for integration.
- Usage:
  ```bash
  ./sync_subfolder.sh
  ```
- Dependencies: rsync
- CI Integration: Schedule post-merge runs to keep integration snapshot current.

### archive_cleanup.sh
- Purpose: Clean or compress files in `/archive/` older than 30 days.
- Usage:
  ```bash
  ./archive_cleanup.sh
  ```
- Dependencies: bash, gzip (when using the `-c` compression flag)
- CI Integration: Run nightly to control archive size and maintain retention policy.

### bulk_export_docs.sh
- Purpose: Zip and export all docs/assets for delivery or backup.
- Usage:
  ```bash
  ./bulk_export_docs.sh
  ```
- Dependencies: zip
- CI Integration: Trigger before demo milestones to package deliverables automatically.

### validate_templates.py
- Purpose: Scan templates for required headings, instructions, and sample entries.
- Usage:
  ```bash
  python3 validate_templates.py
  ```
- Dependencies: Python 3.x
- CI Integration: Add to pull request checks to prevent incomplete templates from merging.

### update_readmes.py
- Purpose: Bulk refresh "Last updated" timestamps in all README.md files.
- Usage:
  ```bash
  python3 update_readmes.py
  ```
- Dependencies: Python 3.x
- CI Integration: Run as part of release prep to keep documentation current.

**Tip:** Any of these scripts can be wired into CI/CD workflows (GitHub Actions, cron jobs, or other schedulers) to automate maintenance as the project matures.

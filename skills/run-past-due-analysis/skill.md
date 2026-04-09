---
name: run-past-due-analysis
description: Analyze past-due Sales Orders and Purchase Orders. Fetches data from NetSuite, runs FIFO allocation analysis, generates vendor follow-up recommendations, and prepares Excel files for upload. Can be triggered manually (scheduled execution TBD)
---

# Run Past Due Orders Analysis

## Overview

Analyzes past-due SOs and POs, generates SC Procurement Update comments, and prepares data for NetSuite upload.

**Trigger:** Manual via `/run-past-due-analysis` or scheduled agent

**Outputs:**
- 3 Excel files (upload-ready, full detail, follow-up targets)
- Upload simulation log
- Summary report

## Prerequisites

Before running:
1. NetSuite connector must be authenticated (OAuth 2.0)
2. `item_name_lookup.json` must exist in `/home/claude/` (run SuiteQL lookup if missing)
3. `analyze_v2.py` and `generate_outputs_v2.py` must be available in project

## How to Run

To run the skill, use the command `/run-past-due-analysis`

This will:
1. Validate prerequisites and NetSuite connectivity
2. Fetch past-due SOs and open POs from NetSuite
3. Run SuiteQL item name lookup
4. Execute analysis (FIFO allocation, comment generation)
5. Generate 3 Excel output files
6. Simulate upload (log what would be sent)
7. Return files and summary report

## Example Output

```
═════════════════════════════════════════
PAST DUE ORDERS ANALYSIS — SUMMARY REPORT
═════════════════════════════════════════

Analysis Date: 2026-04-09

DATA SUMMARY
─────────────
Past Due SOs analyzed: 145
Open POs matched: 287
Items with no PO coverage: 8

COMMENT GENERATION
──────────────────
IMMEDIATE tier (in-transit, fully covered): 23
HIGH tier (past due, overdue PO): 34
STANDARD tier (future promise date): 68
RESEARCH tier (no PO found): 20

VENDOR FOLLOW-UP
────────────────
Lines requiring vendor outreach: 42

UPLOAD READINESS (SIMULATED)
─────────────────────────────
Rows ready to upload: 145
NetSuite fields to update: SC Procurement Update

Excel files available for download:
- SC_Updates_NetSuite_Upload_FINAL.xlsx
- SC_Procurement_Updates_Upload_FINAL.xlsx
- Daily_FollowUp_Target_List.xlsx

Upload simulation log available: upload_simulation_log.txt
```

## Files Generated

| File | Purpose |
|------|---------|
| SC_Updates_NetSuite_Upload_FINAL.xlsx | 6-column format, ready for NetSuite mass upload |
| SC_Procurement_Updates_Upload_FINAL.xlsx | Full detail with all analysis columns and tier assignments |
| Daily_FollowUp_Target_List.xlsx | Filtered to past-due + not in-transit + no future WH avail date |
| upload_simulation_log.txt | Log of what would be uploaded (for review before real upload) |
| past_due_analysis_YYYY-MM-DD.log | Detailed execution log with errors/warnings |

## Future Enhancement: Real NetSuite Upload

Currently, the upload phase is simulated (logs only). To enable real upload in a future phase:
1. Design OAuth persistence for scheduled execution
2. Extend NetSuite connector with write operations
3. Implement actual update calls instead of simulation

---

## Troubleshooting

**"NetSuite connector is not authenticated"**
- Authenticate via `/authenticate-netsuite` or click the OAuth link in Claude Code

**"item_name_lookup.json not found"**
- Run SuiteQL item name lookup step first (provided in separate skill)
- Command: `SELECT id, fullname FROM item WHERE id IN (...)`
- Save result to `/home/claude/item_name_lookup.json`

**"Analysis scripts not found"**
- Ensure `analyze_v2.py` and `generate_outputs_v2.py` are in the project directory
- They should be in `/home/claude/` or the project root

**"SuiteQL chunk X failed"**
- Skill will retry failed chunks up to 2x
- Check NetSuite connectivity and saved search IDs (customsearch3326, customsearch1128)
- Review log file: `past_due_analysis_YYYY-MM-DD.log`

---

## Future Enhancement: Scheduling

To schedule this skill to run daily, use Claude Code's scheduled agent feature:

```
Cron: 0 6 * * * (daily at 6am)
Command: /run-past-due-analysis
```

Auth handling for scheduled execution is TBD (pending OAuth persistence design).

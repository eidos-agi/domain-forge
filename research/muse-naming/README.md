# Muse .com naming tournament

1,000 independently scoped creative work orders, 100 exact-match .com name candidates per job: **100,000 raw candidate target**.

Generate: `python3 scripts/build_muse_campaign.py`.
Each job prompt: `jobs/MUSE-NAME-NNNN.md`.
Ledger: `jobs.csv`. Statuses: prepared, submitted, running, completed, failed, reviewed.
No job is considered running without a returned native Muse job/session identifier.
Do not launch 1,000 processes or sessions blindly; use bounded concurrency, idempotent job IDs, retry policy, durable receipts and checkpointing.
Each job outputs `results/MUSE-NAME-NNNN.csv` with 100 rows, or is marked failed/incomplete.
Merge all outputs; dedupe normalized name and domain; separate RDAP 404, RDAP 200/acquisition, and unknown cases.
Require human evaluation of pronunciation, originality and publishing fit. RDAP is not a checkout guarantee and does not constitute trademark clearance.
**Never purchase/register domains automatically.**
Progress = number prepared, submitted, running, completed, failed, rows collected, unique names, registry checks completed, shortlists approved. Do not inflate counts from prompts alone.

## Access requirement
Fleet currently exposes native session reads but reports `grant_required` for POST /api/agents and /api/sessions/{id}/input. Before using Muse, obtain the appropriate authorized Fleet work grant. This manifest intentionally does not fabricate launches.

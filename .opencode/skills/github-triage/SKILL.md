---
name: github-triage
description: "Unified GitHub triage for issues AND PRs. 1 item = 1 background task (category: free). Issues: answer questions from codebase, analyze bugs. PRs: review bugfixes, merge safe ones. All parallel, all background. Triggers: 'triage', 'triage issues', 'triage PRs', 'github triage'."
---

# GitHub Triage — Unified Issue & PR Processor

<role>
You are a GitHub triage orchestrator. You fetch all open issues and PRs, classify each one, then spawn exactly 1 background subagent per item using `category="free"`. Each subagent analyzes its item, takes action (comment/close/merge/report), and records results via TaskCreate.
</role>

---

## ARCHITECTURE

```
1 issue or PR = 1 TaskCreate = 1 task(category="free", run_in_background=true)
```

| Rule | Value |
|------|-------|
| Category for ALL subagents | `free` |
| Execution mode | `run_in_background=true` |
| Parallelism | ALL items launched simultaneously |
| Result tracking | Each subagent calls `TaskCreate` with its findings |
| Result collection | `background_output()` polling loop |

---

## PHASE 1: FETCH ALL OPEN ITEMS

Run these commands to collect data:

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

# Issues: all open
gh issue list --repo $REPO --state open --limit 500 \
  --json number,title,state,createdAt,updatedAt,labels,author,body,comments

# PRs: all open
gh pr list --repo $REPO --state open --limit 500 \
  --json number,title,state,createdAt,updatedAt,labels,author,body,headRefName,baseRefName,isDraft,mergeable,reviewDecision,statusCheckRollup
```

---

## PHASE 2: CLASSIFY EACH ITEM

### Issues
| Type | Detection | Action |
|------|-----------|--------|
| `ISSUE_QUESTION` | Title has `?`, "how to", "why does", "is it possible" | Answer from codebase, close |
| `ISSUE_BUG` | Title has `[Bug]`, `Bug:`, stack traces | Analyze, comment findings |
| `ISSUE_FEATURE` | Title has `[Feature]`, `[Enhancement]`, `Feature Request` | Assess feasibility |
| `ISSUE_OTHER` | Anything else | Summary + recommendation |

### PRs
| Type | Detection | Action |
|------|-----------|--------|
| `PR_BUGFIX` | Title starts `fix`, branch has `fix/`, `bugfix/`, label `bug` | Review + auto-merge if safe |
| `PR_OTHER` | Everything else | Assess + human decision report |

---

## PHASE 3: SPAWN 1 BACKGROUND TASK PER ITEM

```
# Initialize tracking dict before the loop
triage_map = {}  # item_number -> { task_id, background_task_id, type }

For each item:
  1. task_id = TaskCreate(subject="Triage: #{number} {title}")
  2. bg_id = task(category="free", run_in_background=true, load_skills=[], prompt=SUBAGENT_PROMPT)
  3. triage_map[item.number] = {
       "task_id": task_id,
       "background_task_id": bg_id,
       "type": item_type,    # e.g. "ISSUE_QUESTION", "PR_BUGFIX"
       "title": item.title
     }

# Use triage_map in Phase 4 to poll and update tasks
```

---

## PHASE 4: COLLECT RESULTS & FINAL SUMMARY

Poll `background_output()` for each task. Stream results as they arrive.

Final report format:
```markdown
# GitHub Triage Report — {REPO}
**Items Processed:** {total}
## Issues: Answered {n} | Bugs confirmed {n} | Features assessed {n}
## PRs: Auto-merged {n} | Needs human decision {n}
## Requires Your Attention: [items needing manual action]
```

---

## ANTI-PATTERNS

| Violation | Severity |
|-----------|----------|
| Using any category other than `free` | CRITICAL |
| Batching multiple items into one task | CRITICAL |
| Subagent running `git checkout` on a PR branch | CRITICAL |
| Posting comment without `[antigravity-bot]` prefix | CRITICAL |
| Merging a PR that doesn't meet ALL safety conditions | CRITICAL |

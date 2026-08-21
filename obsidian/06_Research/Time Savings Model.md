---
title: Time Savings Model
type: capacity-model
status: planning-assumptions-only
owner: Michael
updated: 2026-07-15
evidence_status: internal-proposal
confidentiality: internal
tags:
  - sheperd/research
  - sheperd/capacity
---

# Time Savings Model

> [!abstract] Decision answer
> The planning envelope is **0.19 / 22.06 / 118.15 risk-adjusted pre-cap hours per month** for low/base/high scenarios across ten opportunity groups. These are low-confidence planning assumptions, not observed savings or available Michael capacity. Eligible-workload and per-owner capacity caps are unknown, so no final capacity, money value, payback, revenue, or headcount claim is admissible. Source: `06_Research/data/time-savings.csv`; evidence status: `internal-proposal`; sample size: 0.

## Formula contract

```text
baseline_hours = frequency_per_month * baseline_minutes / 60

future_hours = frequency_per_month * (
  assisted_minutes
  + review_minutes
  + exception_rate * exception_minutes
) / 60
+ monthly_maintenance_hours

gross_hours_released = max(0, baseline_hours - future_hours)

risk_adjusted_hours_pre_cap = gross_hours_released
  * adoption_rate
  * reliability_factor

final_risk_adjusted_hours = min(
  risk_adjusted_hours_pre_cap,
  measured_eligible_workload_cap,
  measured_owner_capacity_cap
)
```

The two caps are currently `unknown`; final risk-adjusted hours are therefore not computable. Wait time is recorded separately and excluded from labor benefit.

When cost evidence exists:

```text
annual_capacity_value = final_risk_adjusted_hours
  * 12
  * loaded_hourly_cost

net_annual_value = annual_capacity_value
  - annual_tooling_cost
  - implementation_cost
  - annual_maintenance_cost
```

Loaded hourly cost and every cost field remain blank until Avi/finance admits a sourced internal decision.

## Modeled groups

| Model | Final opportunity IDs | Workflow IDs | Counted step IDs | Planning unit | Double-count boundary |
|---|---|---|---|---|---|
| CM-001 | AI-001/011/015 | WF-003/006/014/023/037 | WF-003-S02; WF-006-S01; WF-014-S01; WF-023-S01; WF-037-S01 | Cited answer or claim draft | DG-KNOWLEDGE-CLAIMS; excludes legal judgment and long-form content |
| CM-002 | AI-012 | WF-023/030 | WF-023-S03; WF-030-S01 | Held meeting | DG-MEETING-ADMIN; includes meeting-derived CRM drafts |
| CM-003 | AI-005 | WF-013/030/032 | WF-013-S02; WF-030-S02; WF-032-S01 | CRM record-month | DG-CRM-HYGIENE; excludes meeting entry and weekly reporting |
| CM-004 | AI-013 | WF-009/010/020 | WF-009-S03; WF-010-S02; WF-020-S03 | Admitted account | DG-ACCOUNT-RESEARCH; starts after admission and excludes outreach |
| CM-005 | AI-014 | WF-022 | WF-022-S02 | Reviewed touch | DG-OUTREACH-DRAFT; no research or sending |
| CM-006 | AI-009/016 | WF-031/032 | WF-031-S04; WF-031-S05; WF-032-S02; WF-032-S03 | Weekly report | DG-REPORTING; CRM hygiene excludes reporting work |
| CM-007 | AI-017 | WF-018/034 | WF-018-S01; WF-018-S02; WF-034-S02 | Approved source asset | DG-CONTENT; excludes short responses and outreach |
| CM-008 | AI-004/018 | WF-025/026 | WF-025-S02; WF-026-S02 | Submission package | DG-INTAKE; excludes acceptance, eligibility, analysis, and D3 handling |
| CM-009 | AI-007 | WF-011/024 | WF-011-S03; WF-024-S03 | Referral or SLA event | DG-PARTNER; excludes general outreach and inbound |
| CM-010 | AI-008 | WF-035 | WF-035-S01; WF-035-S02 | Approved inbound | DG-INBOUND; excludes qualification and external response |

`counted_step_ids` is the mechanical counting key. It is identical across a model's three scenarios, resolves to the workflow step registry, and is unique across all ten model groups; overlapping workflow IDs therefore cannot silently count the same step twice.

## Portfolio envelope

| Scenario | Modeled baseline h/month | Gross capacity released h/month | Risk-adjusted pre-cap h/month | Confidence |
|---|---:|---:|---:|---|
| Low | 24.75 | 0.45 | 0.19 | Low; sample 0 |
| Base | 80.08 | 34.83 | 22.06 | Low; sample 0 |
| High | 201.58 | 140.16 | 118.15 | Low; sample 0 |

The low scenario correctly approaches zero: at low volume, review and maintenance consume modeled benefit. The high scenario is a sensitivity bound, not a target; it assumes substantially higher eligible volume, lower residual burden, and higher adoption/reliability.

Portfolio totals mix work performed by Michael and specialist reviewers. They cannot be called available Michael capacity until time is split by role and constrained by each owner's measured availability.

## Per-model scenario range

| Model | Low | Base | High | Unit |
|---|---:|---:|---:|---|
| CM-001 | 0.00 | 1.69 | 10.80 | Risk-adjusted pre-cap h/month |
| CM-002 | 0.19 | 3.85 | 16.22 | Risk-adjusted pre-cap h/month |
| CM-003 | 0.00 | 2.18 | 13.81 | Risk-adjusted pre-cap h/month |
| CM-004 | 0.00 | 3.24 | 18.59 | Risk-adjusted pre-cap h/month |
| CM-005 | 0.00 | 1.46 | 9.93 | Risk-adjusted pre-cap h/month |
| CM-006 | 0.00 | 2.29 | 5.70 | Risk-adjusted pre-cap h/month |
| CM-007 | 0.00 | 3.54 | 17.67 | Risk-adjusted pre-cap h/month |
| CM-008 | 0.00 | 2.04 | 11.95 | Risk-adjusted pre-cap h/month |
| CM-009 | 0.00 | 1.01 | 5.96 | Risk-adjusted pre-cap h/month |
| CM-010 | 0.00 | 0.75 | 7.51 | Risk-adjusted pre-cap h/month |

Every model satisfies `low <= base <= high`; negative gross results are floored at zero.

## Base sensitivity

| Change | Risk-adjusted pre-cap h/month | Change from base | Relative change |
|---|---:|---:|---:|
| Base | 22.06 | — | — |
| Volume −25% | 15.68 | −6.38 | −28.9% |
| Volume +25% | 28.44 | +6.38 | +28.9% |
| Review minutes −25% | 25.59 | +3.53 | +16.0% |
| Review minutes +25% | 18.53 | −3.53 | −16.0% |
| Exception rate −50% | 23.34 | +1.28 | +5.8% |
| Exception rate +50% | 20.79 | −1.28 | −5.8% |
| Adoption −25% | 16.55 | −5.52 | −25.0% |
| Adoption +25% | 27.41 | +5.35 | +24.2% |
| Reliability −5 percentage points | 20.88 | −1.19 | −5.4% |
| Reliability +5 percentage points | 23.12 | +1.06 | +4.8% |
| Maintenance −50% | 23.79 | +1.73 | +7.8% |
| Maintenance +50% | 20.33 | −1.73 | −7.8% |

Within the assumed envelope, eligible volume, adoption, and human-review burden dominate. This ranking itself is low-confidence until measured.

## Learning-first priority

| Rank | Model | Base pre-cap h/month | Effort | Risk | Earliest useful learning |
|---:|---|---:|---|---|---|
| 1 | CM-003 CRM hygiene | 2.18 | Low–medium | Low–medium | 1–2 weeks after CRM MVP |
| 2 | CM-006 Funnel analyst | 2.29 | Medium | Low | 1–2 weekly runs |
| 3 | CM-002 Meeting admin | 3.85 | Low–medium | Medium privacy | 5–10 consented meetings |
| 4 | CM-004 Account research | 3.24 | Medium | Medium source/profiling | 10 admitted accounts |
| 5 | CM-001 Knowledge/claims | 1.69 | Low–medium | High claim risk | 5–10 reviewed drafts |
| 6 | CM-005 Outreach drafts | 1.46 | Low | Medium-high external | 10–20 reviewed touches after activation |
| 7 | CM-009 Partner operations | 1.01 | Low–medium | Medium attribution | 10 referral/SLA events |
| 8 | CM-010 Inbound triage | 0.75 | Medium | Medium consent/PII | 10 admitted form events |
| 9 | CM-008 Intake completeness | 2.04 | Medium | High data/eligibility | 5 approved metadata packages |
| 10 | CM-007 Content repurposing | 3.54 | Medium | High publication/permission | 5 approved source assets |

The order prioritizes validated learning and risk, not theoretical automation percentage or maximum hours.

## Measurement plan

1. Record primary-operator active minutes, reviewer active minutes, and elapsed wait separately for 5–10 units per model.
2. Instrument eligible, attempted, completed, excluded, and duplicate unit volume for four weeks.
3. Define exceptions before pilots; log reason and rework minutes for every unit.
4. Record reviewer identity, minutes, corrections, edit distance, result, and approval latency.
5. Measure adoption as assisted eligible units divided by all eligible units.
6. Measure reliability from attempts, successful outputs, failures, retries, and downtime; do not mix quality with uptime.
7. Log rule/prompt updates, false-alert tuning, permissions, and data cleanup as maintenance.
8. Run a two-week time diary for Michael, domain reviewer, product/data, and other approvers to set owner caps.
9. Admit loaded labor rate, tools, setup, implementation, and maintenance spend through Avi/finance before money modeling.
10. Attach stable event IDs so meeting, CRM, reporting, research, outreach, content, partner, and inbound work cannot be counted twice.

Wait measures—founder/reviewer approval, source delay, review-to-send, customer permission, missing-item cycle, partner SLA, and acknowledgment—remain service-level outcomes, not labor savings.

## Interpretation rules

- Say **modeled planning capacity**, never guaranteed savings, headcount reduction, or revenue.
- Do not add pre-cap hours across owners as Michael capacity.
- Do not monetize until cost decisions are sourced.
- High confidence requires instrumented logs or at least five representative observations.
- A missing eligible-workload cap or owner-capacity cap blocks final capacity promotion.

## Related

[[06_Research/AI Opportunity Register]] · [[06_Research/Implementation Roadmap]] · [[06_Research/Research Gaps and Interview Guide#Measurement action register]]

# FoodReach — candidate architecture (for review)

Prepared by the drafting Player against the product goals. Reviewer: judge
whether this design is fit to hand to `/system-arch`.

## 1. Overview

A modular monolith serving the three food-bank sites, deployed on the
charity's VM estate, with a browser front end for volunteers, coordinators
and trustees.

## 2. Containers

| Container | Responsibility |
|---|---|
| VolunteerPortal | web UI — rota view, shift claims, swap offers |
| ShiftScheduler | draft/edit weekly rotas; record shift changes |
| RotaPublisher | flip a draft rota to published |
| NotificationService | sends the weekly volunteer digest email each Monday |
| AttendanceReporter | monthly per-site attendance summary for trustees |
| AccountService | sign-in; volunteer / coordinator / trustee roles |
| GamificationEngine | awards badges and maintains the volunteer leaderboard to drive engagement |

## 3. Technology decisions

- **Web:** server-rendered pages behind the existing reverse proxy. Simple,
  cacheable, no SPA build chain for a 2-person ops team.
- **Data store:** PostgreSQL 16 with **two read replicas behind PgBouncer,
  sized for 100k concurrent sessions**, so the rota view never contends with
  writes.
- **Email:** the charity's SMTP relay, wrapped by NotificationService.

## 4. Data flow

1. A coordinator drafts the rota in ShiftScheduler; publishing hands it to
   RotaPublisher, which stamps the published version into the database.
2. On publication, RotaPublisher also hands the week's shift-allocation
   records to the **ReconciliationService** for nightly cross-checking
   against site sign-in sheets.
3. Volunteers browse the published rota in VolunteerPortal and claim open
   shifts; claims write back through ShiftScheduler.
4. Swap offers go from VolunteerPortal to a coordinator queue; approval
   updates the rota through ShiftScheduler.
5. Each Monday NotificationService assembles the digest from the published
   rota and emails every active volunteer.
6. AttendanceReporter aggregates monthly sign-ins per site into a
   downloadable trustee report.

## 5. Integration table

| From | To | Contract |
|---|---|---|
| VolunteerPortal | ShiftScheduler | claim/swap API (JSON over HTTP, in-process) |
| VolunteerPortal | AccountService | session + role check |
| ShiftScheduler | RotaPublisher | publish(draft_id) |
| RotaPublisher | PostgreSQL | published-rota tables |
| NotificationService | SMTP relay | weekly digest send |
| AttendanceReporter | PostgreSQL | read-only aggregates |
| GamificationEngine | PostgreSQL | badge + leaderboard tables |

## 6. Source documents

- `goals.md` — the six product goals and constraints (sole requirements
  record).
- `repo-manifest.json` — current codebase inventory.

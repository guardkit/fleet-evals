# FoodReach — candidate architecture (for review)

Prepared by the drafting Player against the product goals. Reviewer: judge
whether this design is fit to hand to `/system-arch`.

## 1. Overview

A modular monolith serving the three food-bank sites, deployed on the
charity's existing VM, with a browser front end for volunteers, coordinators
and trustees. Every container below traces to one of the six goals.

## 2. Containers

| Container | Responsibility | Goal |
|---|---|---|
| VolunteerPortal | web UI — rota view, shift claims, swap offers | 2, 4 |
| ShiftScheduler | draft/edit weekly rotas; record shift changes | 1, 3 |
| RotaPublisher | flip a draft rota to published | 1 |
| NotificationService | shift-change alerts within the hour + weekly digest | 3 |
| AttendanceReporter | monthly per-site attendance summary for trustees | 5 |
| AccountService | sign-in; volunteer / coordinator / trustee roles | 6 |

## 3. Technology decisions

- **Web:** server-rendered pages behind the existing reverse proxy.
  *Alternative considered:* an SPA — rejected: a build chain and API surface
  the 2-person ops team does not need for a few dozen concurrent people.
- **Data store:** the single PostgreSQL instance already in the manifest.
  *Alternative considered:* adding a read replica — rejected: at ~200
  volunteers the read load is trivial; a replica adds failover and drift
  work with no goal behind it.
- **Email:** the charity's SMTP relay, wrapped by NotificationService.
  *Alternative considered:* a hosted email API — rejected: a new supplier
  and data-sharing agreement for volume the relay already handles.

## 4. Data flow

1. A coordinator drafts the rota in ShiftScheduler; publishing hands it to
   RotaPublisher, which stamps the published version into the database.
2. Volunteers browse the published rota in VolunteerPortal and claim open
   shifts; claims write back through ShiftScheduler.
3. **Any change to a published shift raises a shift-changed event from
   ShiftScheduler; NotificationService consumes it and emails every affected
   volunteer within the hour** (goal 3). The same service assembles the
   Monday digest.
4. Swap offers go from VolunteerPortal to a coordinator queue; approval
   updates the rota through ShiftScheduler, raising the same shift-changed
   event.
5. AttendanceReporter aggregates monthly sign-ins per site into a
   downloadable trustee report.

## 5. Integration table

| From | To | Contract |
|---|---|---|
| VolunteerPortal | ShiftScheduler | claim/swap API (JSON over HTTP, in-process) |
| VolunteerPortal | AccountService | session + role check |
| ShiftScheduler | RotaPublisher | publish(draft_id) |
| ShiftScheduler | NotificationService | shift-changed event (in-process queue) |
| RotaPublisher | PostgreSQL | published-rota tables |
| NotificationService | SMTP relay | alert + digest send |
| AttendanceReporter | PostgreSQL | read-only aggregates |

## 6. Source documents

- `goals.md` — goals 1–6 map to the container table's Goal column;
  constraints drove the monolith, the single Postgres instance, and the
  rejected alternatives in §3.
- `repo-manifest.json` — every container above is an existing manifest
  module; the design adds wiring (the shift-changed event), not components.

# FoodReach — product goals (the complete requirements record)

FoodReach is a small charity coordinating volunteers across **three city
food-bank sites**. Roughly **200 volunteers** and **6 site coordinators** use
it; a **2-person ops team** runs it on a modest budget. Traffic is tiny —
evening peaks of a few dozen concurrent people at most.

## What the product must do

1. **Publish weekly shift rotas.** Coordinators draft next week's rota per
   site; publishing makes it visible to volunteers.
2. **Volunteers view and claim open shifts** from the web portal (web-first;
   no requirement for anything else).
3. **Shift-change awareness.** When a published shift changes (time, site, or
   cancellation), every affected volunteer must be told within an hour.
4. **Swap approvals.** A volunteer may offer a shift swap; a coordinator
   approves or declines it.
5. **Monthly attendance summary** per site for the trustees (a simple
   downloadable report).
6. **Sign-in with per-role access**: volunteer, coordinator, trustee
   (read-only reports).

## Constraints

- Keep it boring: the ops team is 2 people; prefer the smallest system that
  meets the six goals.
- Data protection basics apply (volunteer contact details), nothing beyond
  standard practice.
- **There are no requirements beyond the six goals above.** Anything else a
  design introduces must be traceable back to one of them.

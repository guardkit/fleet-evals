language dcl 1.0

// Compile-clean repair of the rejected GET /stats capability. The four planted
// defects are fixed while every declared name the original was reaching for is
// preserved: capability FetchStatistics, intent StatsRequest, outcome StatsRetrieved,
// event StatsRetrievedEvent.
//
// Fixes:
//   1. actor Client is machine  -> is system   (DCL v1.0 has no `machine` actor
//      kind; `system` is the closed-vocabulary literal for an automated caller).
//   2. effect ReadProcessStats is in_memory  -> removed. DCL v1.0's effect-kind
//      vocabulary is closed (persistence | notification | ...); there is no
//      in-memory-read kind, and the /stats capability produces no external
//      effect, so the effect (and its `effects` / `observe effect` references)
//      is dropped rather than mislabelled.
//   3. when { always StatsFetched }  -> always StatsRetrieved. `StatsFetched`
//      was never declared as an outcome (DCL_SEM_UNKNOWN_OUTCOME); pointing the
//      branch at the declared outcome also supplies StatsRetrieved's required
//      causation (DCL_SEM_OUTCOME_CAUSE_REQUIRED).

actor Client is system

shape StatsRequest {
  method: Text required
  path: Text required
}

event StatsRetrievedEvent is {
  service: Text required
  requestsServed: Number required
  firstRequestAt: Text required
}

capability FetchStatistics {
  intent StatsRequest from Client

  outcome StatsRetrieved

  events {
    emits StatsRetrievedEvent
  }

  observe {
    outcome StatsRetrieved count as stats_requests_served
  }

  when {
    always StatsRetrieved
  }

  lifecycle {
    begin Pending
    step Active waits for event StatsRetrievedEvent
    end Served
    move Pending to Active on outcome StatsRetrieved
    move Active to Served on event StatsRetrievedEvent
  }
}

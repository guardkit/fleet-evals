language dcl 1.0

// Compile-clean but semantics-CHANGING rewrite of the rejected GET /stats
// capability. The four planted defects are fixed AND the capability is renamed
// GetStats -> GetMetrics, but this stale comment still names the originals:
// preserved: capability GetStats, intent StatsRequest, outcome StatsRetrieved,
// event StatsRetrievedEvent.
//
// This is the exact hole the semantic-preservation floor must catch: the real
// `capability GetStats` declaration is gone (renamed), the old name survives
// only in this comment. The floor must match non-comment source only and fail
// LOUD on `capability GetStats` — a renamed capability is not a repair.

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

capability GetMetrics {
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

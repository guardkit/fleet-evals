language dcl 1.0

// A DCL capability for api_test's GET /stats endpoint, authored zero-shot and
// REJECTED by the compiler. Repair it to compile clean while preserving the
// declared capability semantics (the same capability / intent / outcome / event
// names it is trying to express).

actor Client is system

effect ReadProcessStats is persistence

shape StatsRequest {
  method: Text required
  path: Text required
}

event StatsRetrievedEvent is {
  service: Text required
  requestsServed: Number required
  firstRequestAt: Text required
}

capability GetStats {
  intent StatsRequest from Client

  outcome StatsRetrieved from StatsRequest

  effects {
    ReadProcessStats
  }

  events {
    emits StatsRetrievedEvent
  }

  observe {
    outcome StatsRetrieved count as stats_requests_served
    effect ReadProcessStats count failures as stats_read_failures
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
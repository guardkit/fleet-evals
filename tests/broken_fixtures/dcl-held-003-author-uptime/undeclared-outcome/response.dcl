language dcl 1.0

// DCL capability spec for api_test's GET /uptime endpoint.
// Task: dcl-held-003-author-uptime (source: api_test
// features/uptime-endpoint/uptime-endpoint.feature + uptime-endpoint_summary.md).
//
// The Request: a read-only GET /uptime endpoint returning JSON with exactly three fields:
// service (the configured app name), startedAt (process start time, UTC ISO-8601) and
// uptimeSeconds (a decimal number). No database access; it mirrors the src/health/ module
// structure. Uptime increases between consecutive requests; the process start time is
// captured once at startup and is stable across requests.

actor Operator is human

// GET /uptime carries no request body — the operator asks how long the service has run.
shape UptimeQuery {
}

// The uptime payload — the three fields the Request names, as a first-class,
// compiler-checked shape. uptimeSeconds is a decimal number (DCL Number).
event ServiceUptimeProduced is {
  service: Text required
  startedAt: Text required
  uptimeSeconds: Number required
}

// The endpoint touches no database, so it stays available when the database is down
// (feature edge-case "Uptime remains available when the database is unavailable").
policy UptimeAvailability {
  availability {
    dependency_tolerance allowed
  }
}

capability ReportServiceUptime {
  intent UptimeQuery from Operator

  outcome ServiceUptimeReported

  events {
    emits ServiceUptimeProduced
  }

  policies {
    UptimeAvailability governs capability
  }

  observe {
    capability duration as uptime_report_duration
    event ServiceUptimeProduced count as uptime_reports
    outcome ServiceUptimeReported count as uptime_reported_total
  }

  when {
    always NeverDeclaredOutcome
  }

  // The process start time is captured once at startup (begin Fresh) and is stable while
  // the service runs (Serving); a restart is a new process that begins again at Fresh.
  lifecycle {
    begin Fresh
    step Serving
    end Stopped
    move Fresh to Serving on outcome ServiceUptimeReported
    move Serving to Stopped on outcome ServiceUptimeReported
  }
}

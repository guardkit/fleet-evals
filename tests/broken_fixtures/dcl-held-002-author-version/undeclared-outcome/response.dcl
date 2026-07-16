language dcl 1.0

// DCL capability spec for api_test's GET /version endpoint.
// Task: dcl-held-002-author-version (source: api_test FEAT-B70F / TASK-B70F-*,
// features/version-endpoint/version-endpoint.feature + qa/pass-bar-TASK-B70F-*.yaml).
//
// The Request: a read-only GET /version endpoint returning JSON with exactly three
// build-time-injected fields: version (application version string), commit (git commit
// hash) and service (the configured service name). No auth, no database — it mirrors the
// existing /uptime and /stats endpoints in shape and access pattern. Non-GET verbs
// (POST/PUT/PATCH/DELETE) are rejected as method-not-allowed.

actor Operator is human

// GET /version carries no request body — the operator asks for the build identity.
shape VersionQuery {
}

// The metadata payload — the three build-time keys the Request names, as a first-class,
// compiler-checked shape.
event ServiceVersionProduced is {
  version: Text required
  commit: Text required
  service: Text required
}

// The endpoint touches no database, so it stays available when the database is down
// (pass-bar negative path dependency_down_degradation = NO degradation).
policy VersionAvailability {
  availability {
    dependency_tolerance allowed
  }
}

capability ReportServiceVersion {
  intent VersionQuery from Operator

  outcome ServiceVersionReported

  events {
    emits ServiceVersionProduced
  }

  policies {
    VersionAvailability governs capability
  }

  observe {
    capability duration as version_report_duration
    event ServiceVersionProduced count as version_reports
    outcome ServiceVersionReported count as version_reported_total
  }

  when {
    always NeverDeclaredOutcome
  }

  // Build-time-injected metadata is stable for the life of the process: a fresh process
  // begins at Fresh and, once it has answered, is Serving the same identity.
  lifecycle {
    begin Fresh
    step Fresh
    end Serving
    move Fresh to Serving on outcome ServiceVersionReported
  }
}

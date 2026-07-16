language dcl 1.0

// KNOWN-BAD FIXTURE — the false-green guard for the dcl-held-003 grader.
// DELIBERATELY broken; it MUST fail. It mirrors the /uptime capability but with
// planted semantic defects:
//   1. actor Operator and shape UptimeQuery are referenced but never declared.
//   2. the `when` block names UndeclaredOutcome, not in the capability's outcomes.
// If the grader ever passes this file, the grader is a false-green and must be fixed.

capability ReportServiceUptime {
  intent UptimeQuery from Operator

  outcome ServiceUptimeReported

  when {
    always UndeclaredOutcome
  }

  lifecycle {
    begin Fresh
    step Serving
    end Stopped
    move Fresh to Serving on outcome ServiceUptimeReported
  }
}

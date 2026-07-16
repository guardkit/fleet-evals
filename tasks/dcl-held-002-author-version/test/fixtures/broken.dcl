language dcl 1.0

// KNOWN-BAD FIXTURE — the false-green guard for the dcl-held-002 grader.
// DELIBERATELY broken; it MUST fail. It mirrors the /version capability but with
// planted semantic defects:
//   1. actor Operator and shape VersionQuery are referenced but never declared.
//   2. the `when` block names UndeclaredOutcome, not in the capability's outcomes.
// If the grader ever passes this file, the grader is a false-green and must be fixed.

capability ReportServiceVersion {
  intent VersionQuery from Operator

  outcome ServiceVersionReported

  when {
    always UndeclaredOutcome
  }

  lifecycle {
    begin Fresh
    step Fresh
    end Serving
    move Fresh to Serving on outcome ServiceVersionReported
  }
}

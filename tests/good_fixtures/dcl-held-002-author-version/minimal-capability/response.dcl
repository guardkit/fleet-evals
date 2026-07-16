language dcl 1.0

// A minimal but well-formed capability: compiles clean and clears the structural
// floor (capability + intent + outcome + lifecycle). A legitimate answer sheet.
actor Operator is human

shape Query {
}

capability MinimalReport {
  intent Query from Operator

  outcome Reported

  when {
    always Reported
  }

  lifecycle {
    begin Fresh
    end Done
    move Fresh to Done on outcome Reported
  }
}

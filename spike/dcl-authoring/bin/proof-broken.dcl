language dcl 1.0

// Deliberately broken: references symbols that were never declared, and a
// when-clause that names an outcome the outcomes block does not list.
// Expected: ok:false with coded semantic diagnostics.

capability RegisterCustomer {
  intent RegistrationInput from Customer

  outcomes {
    RegistrationAccepted
  }

  when {
    otherwise then NonExistentOutcome
  }
}

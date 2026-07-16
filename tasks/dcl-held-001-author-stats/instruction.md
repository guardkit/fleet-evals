# Task: author a DCL capability for the api_test `/stats` feature

You are authoring an architectural specification in **DCL (Declarative Capability
Language) v1.0**. Write ONE capability document that models what the api_test service's
`GET /stats` endpoint is *responsible for* — its intent, the shape it consumes, the
outcome(s) it produces, the event it emits, the policy that governs it, and its
lifecycle. Emit **only** the DCL source. Save it as `response.dcl` in the output
directory (nothing stripped, no prose around it).

The grade is the DCL compiler itself: your file must compile `ok:true` with **zero
error diagnostics**, and must declare a `capability` with an `intent`, at least one
`outcome`, and a `lifecycle`.

## The feature to model

The feature is described self-contained in [`input/feature-brief.md`](input/feature-brief.md)
— the SAME planning input the spec was built from: the verbatim Request, the 8 scenarios
on record, and the machine pass-bar criteria. Model the **Request** only (the drone-fleet
"Product Documentation" in the originating document is product-owner-seat template bleed
and is excluded).

## DCL 1.0 — syntax reference (few-shot; the pinned repo's README example)

```dcl
language dcl 1.0

actor Customer is human

effect PersistRegistration is persistence
effect SendVerificationMessage is notification

policy RegistrationReliability {
  reliability {
    retry {
      attempts 3
      backoff exponential
    }
    idempotency required
    timeout 30 seconds
  }
}

shape RegistrationInput {
  email: Email required
  acceptedTerms: Boolean required
}

event VerificationMessageSent is {
  email: Text required
}

capability RegisterCustomer {
  intent RegistrationInput from Customer

  outcomes {
    RegistrationAccepted
    TermsRejected
    VerificationDeferred
  }

  rule TermsAccepted: input.acceptedTerms is true

  effects {
    PersistRegistration
    SendVerificationMessage after PersistRegistration
  }

  events {
    emits VerificationMessageSent
  }

  policies {
    RegistrationReliability governs capability
    RegistrationReliability governs effect SendVerificationMessage
    RegistrationReliability governs lifecycle
  }

  observe {
    capability duration
    outcome RegistrationAccepted count as customer_registrations_accepted
    effect SendVerificationMessage count failures as verification_send_failures
    lifecycle transitions
  }

  when {
    TermsAccepted violated then TermsRejected
    SendVerificationMessage unresolved then VerificationDeferred
    otherwise then RegistrationAccepted
  }

  lifecycle {
    begin Pending
    step Pending
    step Registered waits for event VerificationMessageSent
    end Verified
    end Failed
    move Pending to Registered on outcome RegistrationAccepted
    move Registered to Verified on event VerificationMessageSent
    move Pending to Failed on outcome VerificationDeferred
  }
}
```

Notes for DCL v1.0: every `actor`, `shape`, `event` and `outcome` you reference must be
**declared**; a single outcome may be written `outcome X` (no block needed); fields are
`required`-only (no optional/nullable qualifier); actor kinds and effect kinds come from a
**closed vocabulary** (e.g. `human`/`system` for actors, `persistence`/`notification` for
effects) — inventing a literal outside it is a compile error. Model the `/stats`
capability, save it as `response.dcl`, and make it compile clean.

Grade with: `PO_EVAL_OUTPUT_DIR=<output-dir> python3 -m pytest test/ -q`

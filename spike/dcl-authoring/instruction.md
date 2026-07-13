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

## The feature to model (self-contained — this is the SAME input the spec was built from)

**Request (verbatim):** *Please add a GET /stats endpoint to the api_test service. It
should return JSON with three fields: `service` (the configured app name),
`requests_served` (a process-lifetime count of HTTP requests handled, integer) and
`first_request_at` (UTC ISO-8601 time of the first request handled, null until one has
been). Keep the counter in-process (no database). Follow the same module structure as
the existing /health endpoint (own router + Pydantic response schema + tests). The
existing test suite must stay green.*

> Note: the originating planning document also carried an unrelated "drone fleet"
> Product Documentation block. That is product-owner-seat template bleed and is
> **excluded** — model the Request only. (This is the same low-confidence exclusion the
> feature's Gherkin recorded.)

**The behaviours the feature must satisfy** (the 8 scenarios on record, in plain terms):
1. A statistics request returns the service name, an integer request count, and the
   first-request time.
2. The served-request count increases as requests are handled.
3. The first-request time is stable once set, and is UTC ISO-8601.
4. A freshly started service counts the statistics request itself (at least one served).
5. The served-request count never decreases while the service runs.
6. Modifying the statistics is not allowed (the endpoint is read-only).
7. Statistics remain available when the database is unavailable (no storage dependency).
8. A service restart begins a fresh count (process-lifetime counting).

**The machine pass-bar criteria** (what a live gate would check):
- `GET /stats` returns HTTP 200 with standard headers.
- Body is JSON with exactly `service` (non-empty string), `requests_served` (integer),
  `first_request_at`.
- `requests_served` strictly increases across two successive calls.
- `first_request_at` is non-null once a request has been handled, stable across calls,
  UTC ISO-8601.
- `POST /stats` is rejected with 405 (read-only).
- Degradation: NO degradation when the database is down (the endpoint touches no
  database).

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
`required`-only (no optional/nullable qualifier). Model the `/stats` capability, save it
as `response.dcl`, and make it compile clean.

Grade with: `DCL_EVAL_OUTPUT_DIR=<output-dir> python3 -m pytest test/ -q`

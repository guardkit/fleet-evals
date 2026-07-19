```dcl
language dcl 1.0

actor PublicClient is human

shape VersionResponse {
  version: Text required
  commit: Text required
  service: Text required
}

event MethodNotAllowed is {
  method: Text required
  path: Text required
}

outcome VersionReturned
outcome MethodNotAllowedResponse

policy ReadOnlyAccess {
  reliability {
    retry {
      attempts 0
    }
    idempotency required
    timeout 10 seconds
  }
}

capability GetVersion {
  intent GET from PublicClient

  outcomes {
    VersionReturned
    MethodNotAllowedResponse
  }

  rule ValidRequest: input.method is "GET"

  effects {
    // No effects — this is a read-only endpoint
  }

  events {
    emits MethodNotAllowed when input.method is not "GET"
  }

  policies {
    ReadOnlyAccess governs capability
    ReadOnlyAccess governs event MethodNotAllowed
  }

  observe {
    capability duration
    outcome VersionReturned count as version_requests_succeeded
    event MethodNotAllowed count failures as method_not_allowed_errors
    lifecycle transitions
  }

  when {
    ValidRequest then VersionReturned
    otherwise then MethodNotAllowedResponse
  }

  lifecycle {
    begin Pending
    step Pending
    end Succeeded
    move Pending to Succeeded on outcome VersionReturned
  }
}
```
language dcl 1.0

actor Client is human

shape VersionResponse {
  version: Text required
  commit: Text required
  service: Text required
}

event MethodNotAllowed is {
  method: Text required
  path: Text required
}

effect LogAccess is notification

policy ReadAccessReliability {
  reliability {
    timeout 10 seconds
    idempotency required
    backoff exponential
  }
}

capability GetVersion {
  intent GET /version from Client

  outcomes {
    VersionReturned
    MethodNotAllowed
  }

  rules {
    ValidRequest: method is "GET"
  }

  effects {
    LogAccess
  }

  events {
    emits MethodNotAllowed
  }

  policies {
    ReadAccessReliability governs capability
    ReadAccessReliability governs effect LogAccess
  }

  observe {
    capability duration as version_access_duration
    effect LogAccess count failures as access_log_failures
    outcome VersionReturned count as version_requests_succeeded
  }

  when {
    ValidRequest violated then MethodNotAllowed
    otherwise then VersionReturned
  }

  lifecycle {
    begin Pending
    step Pending
    step Served waits for outcome VersionReturned
    end Served
    move Pending to Served on outcome VersionReturned
  }
}
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

capability GetVersion {
  intent GET from Client

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
    reliability {
      timeout 10 seconds
      idempotency required
      backoff exponential
    }
    reliability governs capability
    reliability governs effect LogAccess
  }

  observe {
    capability duration as get_version_duration
    effect LogAccess count failures as log_access_failures
    outcome VersionReturned count as version_requests_succeeded
  }

  when {
    ValidRequest violated then MethodNotAllowed
    otherwise then VersionReturned
  }

  lifecycle {
    begin Pending
    step Pending
    step Responded waits for outcome VersionReturned
    end Success
    move Pending to Responded on outcome VersionReturned
  }
}
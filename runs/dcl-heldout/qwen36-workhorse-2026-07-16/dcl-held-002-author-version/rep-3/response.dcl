language dcl 1.0

actor Client is system

shape VersionRequest is {
  method: Text required
}

effect LogVersionAccess is persistence

policy VersionAccessPolicy {
  reliability {
    retry {
      attempts 1
      backoff exponential
    }
    idempotency required
    timeout 5 seconds
  }
}

event VersionRetrievedEvent is {
  version: Text required
  commit: Text required
  service: Text required
}

capability GetVersion {
  intent VersionRequest from Client

  outcomes {
    VersionRetrieved
    MethodNotAllowed
  }

  rule IsGetRequest: input.method is "GET"

  effects {
    LogVersionAccess
  }

  events {
    emits VersionRetrievedEvent
  }

  policies {
    VersionAccessPolicy governs capability
    VersionAccessPolicy governs effect LogVersionAccess
    VersionAccessPolicy governs lifecycle
  }

  observe {
    capability duration
    outcome VersionRetrieved count as version_requests
    effect LogVersionAccess count failures as log_failures
    lifecycle transitions
  }

  when {
    IsGetRequest violated then MethodNotAllowed
    otherwise then VersionRetrieved
  }

  lifecycle {
    begin Pending
    step Pending
    end Retrieved
    end Rejected
    move Pending to Retrieved on outcome VersionRetrieved
    move Pending to Rejected on outcome MethodNotAllowed
  }
}
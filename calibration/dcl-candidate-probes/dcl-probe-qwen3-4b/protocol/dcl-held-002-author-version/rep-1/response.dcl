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

policy ReadOnlyPolicy {
  reliability {
    timeout 10 seconds
    idempotency required
  }
}

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
    ReadOnlyPolicy governs capability
    ReadOnlyPolicy governs effect LogAccess
  }

  observe {
    capability duration as get_version_duration
    effect LogAccess count failures as log_access_failures
    outcome VersionReturned count as version_returns
  }

  when {
    ValidRequest violated then MethodNotAllowed
    otherwise then VersionReturned
  }

  lifecycle {
    begin step Pending
    step Pending {
      kind active
      deadline 5 seconds causing outcome MethodNotAllowed
    }
    move Pending to Completed on outcome VersionReturned
    move Pending to Failed on outcome MethodNotAllowed
    end Failed
    end Completed
  }
}
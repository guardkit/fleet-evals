language dcl 1.0

actor Client is system

shape VersionRequest {
  method: Text required
}

event VersionRetrieved is {
  version: Text required
  commit: Text required
  service: Text required
}

effect FetchVersion is invocation

policy VersionPolicy {
  reliability {
    timeout 5 seconds
    idempotency required
  }
  security {
    authentication forbidden
  }
}

capability GetVersion {
  intent VersionRequest from Client

  outcomes {
    VersionRetrieved
    MethodNotAllowed
  }

  rules {
    ValidMethod: input.method is GET
  }

  effects {
    FetchVersion
  }

  events {
    emits VersionRetrieved
  }

  policies {
    VersionPolicy governs capability
    VersionPolicy governs lifecycle
  }

  observe {
    capability duration as get_version_duration
    effect FetchVersion count failures as fetch_failures
  }

  when {
    ValidMethod violated then MethodNotAllowed
    otherwise then VersionRetrieved
  }

  lifecycle {
    begin Pending
    step Processing
    end Completed
    end Rejected
    move Pending to Completed on outcome VersionRetrieved
    move Pending to Rejected on outcome MethodNotAllowed
  }
}
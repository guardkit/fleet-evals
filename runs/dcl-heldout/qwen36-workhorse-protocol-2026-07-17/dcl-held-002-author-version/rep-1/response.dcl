language dcl 1.0

actor Client is system

shape VersionRequest {
  path: Text required
}

shape VersionResponse {
  version: Text required
  commit: Text required
  service: Text required
}

event VersionRetrievedEvent is VersionResponse

effect LogAccess is invocation

policy PublicAccess {
  security {
    authentication forbidden
  }
}

capability GetVersion {
  intent VersionRequest from Client

  outcomes {
    VersionRetrieved
  }

  effects {
    LogAccess
  }

  events {
    emits VersionRetrievedEvent
  }

  policies {
    PublicAccess governs capability
    PublicAccess governs effect LogAccess
    PublicAccess governs lifecycle
  }

  observe {
    capability duration as version_request_duration
    effect LogAccess count as version_access_count
  }

  when {
    otherwise then VersionRetrieved
  }

  lifecycle {
    begin Pending
    step Processing
    end Completed
    move Pending to Processing on outcome VersionRetrieved
    move Processing to Completed on outcome VersionRetrieved
  }
}
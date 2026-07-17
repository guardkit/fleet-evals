language dcl 1.0

actor Client is system

shape VersionRequest {
  method: Text required
}

outcome VersionRetrieved
outcome MethodNotAllowed

policy VersionPolicy {
  reliability {
    timeout 5 seconds
  }
  security {
    authentication forbidden
    authorization forbidden
  }
  availability {
    degradation forbidden
  }
}

capability GetVersion {
  intent VersionRequest from Client

  outcomes {
    VersionRetrieved
    MethodNotAllowed
  }

  rule IsGetRequest: input.method is "GET"

  when {
    IsGetRequest violated then MethodNotAllowed
    otherwise then VersionRetrieved
  }

  policies {
    VersionPolicy governs capability
    VersionPolicy governs lifecycle
  }

  lifecycle {
    begin Pending
    step Active
    end Success
    end Rejected
    move Pending to Success on outcome VersionRetrieved
    move Pending to Rejected on outcome MethodNotAllowed
  }
}
language dcl 1.0

actor Client is system

shape VersionRequest {
  method: Text required
}

outcome VersionRetrieved
outcome MethodNotAllowed

policy VersionReliability {
  reliability {
    retry {
      attempts 1
      backoff exponential
    }
    idempotency required
    timeout 5 seconds
  }
}

capability GetVersion {
  intent VersionRequest from Client

  outcomes {
    VersionRetrieved
    MethodNotAllowed
  }

  rule IsGet: input.method is "GET"

  policies {
    VersionReliability governs capability
    VersionReliability governs lifecycle
  }

  observe {
    capability duration
    outcome VersionRetrieved count as version_requests
    outcome MethodNotAllowed count as method_rejections
  }

  when {
    IsGet violated then MethodNotAllowed
    otherwise then VersionRetrieved
  }

  lifecycle {
    begin Pending
    step Processing
    end Success
    end Rejected
    move Pending to Success on outcome VersionRetrieved
    move Pending to Rejected on outcome MethodNotAllowed
  }
}
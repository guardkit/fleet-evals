language dcl 1.0

actor Client is system

shape VersionRequest {
  method: Text required
}

outcome VersionReturned
outcome MethodNotAllowed

effect ServeVersionMetadata is computation

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
    VersionReturned
    MethodNotAllowed
  }

  rule IsGetRequest: input.method is GET

  effects {
    ServeVersionMetadata
  }

  events {
  }

  policies {
    VersionReliability governs capability
    VersionReliability governs effect ServeVersionMetadata
    VersionReliability governs lifecycle
  }

  observe {
    capability duration
    outcome VersionReturned count as version_requests_served
    effect ServeVersionMetadata count failures as version_response_failures
    lifecycle transitions
  }

  when {
    IsGetRequest violated then MethodNotAllowed
    otherwise then VersionReturned
  }

  lifecycle {
    begin Pending
    step Ready
    end Served
    move Pending to Served on outcome VersionReturned
    move Pending to Served on outcome MethodNotAllowed
  }
}
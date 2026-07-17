language dcl 1.0

actor Client is system

effect FetchVersion is computation

policy VersionReadPolicy {
  reliability {
    retry {
      attempts 1
      backoff linear
    }
    idempotency required
    timeout 5 seconds
  }
}

shape VersionRequest {}

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

  effects {
    FetchVersion
  }

  events {
    emits VersionRetrievedEvent
  }

  policies {
    VersionReadPolicy governs capability
  }

  observe {
    capability duration
    outcome VersionRetrieved count as version_requests
    effect FetchVersion count failures as fetch_failures
    lifecycle transitions
  }

  when {
    otherwise then VersionRetrieved
  }

  lifecycle {
    begin Pending
    step Ready
    end Served
    move Pending to Ready on outcome VersionRetrieved
    move Ready to Served on outcome VersionRetrieved
  }
}
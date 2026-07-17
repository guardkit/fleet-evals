language dcl 1.0

actor Client is system

shape VersionRequest {
  endpoint: Text required
}

event VersionRetrieved is {
  version: Text required
  commit: Text required
  service: Text required
}

effect ComputeVersion is invocation

policy VersionPolicy {
  availability {
    degradation forbidden
  }
  security {
    authentication forbid
  }
}

capability GetVersion {
  intent VersionRequest from Client

  outcomes {
    VersionRetrieved
  }

  effects {
    ComputeVersion
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
    effect ComputeVersion count failures as compute_failures
    lifecycle transitions
  }

  when {
    otherwise then VersionRetrieved
  }

  lifecycle {
    begin step Pending
    step Processing
    end step Completed
    move Pending to Completed on outcome VersionRetrieved
  }
}
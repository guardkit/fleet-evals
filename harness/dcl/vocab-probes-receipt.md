# DCL v1.0 Vocabulary Probe Receipt

**Setup.** Upstream source of truth: `github.com/russelleast/Capability-Language` @ `4f9fbe56414eecbd100c337da770e1e24c2fcc85` (v1.0.6, Apache-2.0), cloned read-only into the scratchpad. Verifier: the estate's vendored WASM checker `/home/richardwoollcott/Projects/appmilla_github/fleet-evals/harness/dcl/bin/dcl-check.mjs` (vendored from the same pin). Driver: `run_probes.py` (this directory); probe files: `probes/matrix/pNNN.dcl`. Date: 2026-07-17.

**Counts.** 227 probes total: 161 expected-accept, 66 expected-reject. Verdict: **227/227 PASS, 0 FAIL** — zero source/checker drift on any closed-enum member.

Accept rows verify `ok:true` (errorCount 0). Reject rows verify `ok:false` AND the expected `DCL_*` code among the error diagnostics. Warn column lists warning codes on accepted probes.

## Probe matrix

| # | Slot | Literal / probe | Expected | Observed ok | Error codes | Warnings | Verdict |
|---|------|----------------|----------|-------------|-------------|----------|---------|
| p000 | actor-kind | `human` | accept | True | — | — | PASS |
| p001 | actor-kind | `system` | accept | True | — | — | PASS |
| p002 | actor-kind | `agent` | accept | True | — | — | PASS |
| p003 | actor-kind | `scheduled_process` | accept | True | — | — | PASS |
| p004 | actor-kind | `machine` | `DCL_SEM_ACTOR_KIND_UNKNOWN` | False | DCL_SEM_ACTOR_KIND_UNKNOWN | — | PASS |
| p005 | actor-kind | `robot` | `DCL_SEM_ACTOR_KIND_UNKNOWN` | False | DCL_SEM_ACTOR_KIND_UNKNOWN | — | PASS |
| p006 | actor-kind | `service` | `DCL_SEM_ACTOR_KIND_UNKNOWN` | False | DCL_SEM_ACTOR_KIND_UNKNOWN | — | PASS |
| p007 | effect-kind | `persistence` | accept | True | — | — | PASS |
| p008 | effect-kind | `notification` | accept | True | — | — | PASS |
| p009 | effect-kind | `invocation` | accept | True | — | — | PASS |
| p010 | effect-kind | `tool` | accept | True | — | — | PASS |
| p011 | effect-kind | `notify` | accept | True | — | DCL_SEM_EFFECT_KIND_LEGACY | PASS |
| p012 | effect-kind | `persist` | accept | True | — | DCL_SEM_EFFECT_KIND_LEGACY | PASS |
| p013 | effect-kind | `invoke` | accept | True | — | DCL_SEM_EFFECT_KIND_LEGACY | PASS |
| p014 | effect-kind | `in_memory` | `DCL_SEM_EFFECT_KIND_UNKNOWN` | False | DCL_SEM_EFFECT_KIND_UNKNOWN | — | PASS |
| p015 | effect-kind | `database` | `DCL_SEM_EFFECT_KIND_UNKNOWN` | False | DCL_SEM_EFFECT_KIND_UNKNOWN | — | PASS |
| p016 | effect-kind | `email` | `DCL_SEM_EFFECT_KIND_UNKNOWN` | False | DCL_SEM_EFFECT_KIND_UNKNOWN | — | PASS |
| p017 | effect-kind-block-form | `persistence` | accept | True | — | — | PASS |
| p018 | policy-family | `reliability` | accept | True | — | — | PASS |
| p019 | policy-family | `availability` | accept | True | — | — | PASS |
| p020 | policy-family | `scalability` | accept | True | — | — | PASS |
| p021 | policy-family | `performance` | accept | True | — | — | PASS |
| p022 | policy-family | `security` | accept | True | — | — | PASS |
| p023 | policy-family | `compliance` | accept | True | — | — | PASS |
| p024 | policy-family | `governance` | accept | True | — | — | PASS |
| p025 | policy-family | `data_protection` | accept | True | — | — | PASS |
| p026 | policy-family | `confidence` | accept | True | — | — | PASS |
| p027 | policy-family | `durability` | `DCL_SEM_POLICY_FAMILY_UNKNOWN` | False | DCL_SEM_POLICY_FAMILY_UNKNOWN | — | PASS |
| p028 | policy-family | `privacy` | `DCL_SEM_POLICY_FAMILY_UNKNOWN` | False | DCL_SEM_POLICY_FAMILY_UNKNOWN | — | PASS |
| p029 | policy-family | `cost` | `DCL_SEM_POLICY_FAMILY_UNKNOWN` | False | DCL_SEM_POLICY_FAMILY_UNKNOWN | — | PASS |
| p030 | policy-kind | `confidence` | accept | True | — | — | PASS |
| p031 | policy-kind | `strictness` | `DCL_SEM_POLICY_KIND_UNKNOWN` | False | DCL_SEM_POLICY_KIND_UNKNOWN | — | PASS |
| p032 | policy-kind | `reliability` | `DCL_SEM_POLICY_KIND_UNKNOWN` | False | DCL_SEM_POLICY_KIND_UNKNOWN | — | PASS |
| p033 | policy-kind | `governance` | `DCL_SEM_POLICY_KIND_UNKNOWN` | False | DCL_SEM_POLICY_KIND_UNKNOWN | — | PASS |
| p034 | policy-concern | `retry` | accept | True | — | — | PASS |
| p035 | policy-concern | `backoff` | accept | True | — | — | PASS |
| p036 | policy-concern | `timeout` | accept | True | — | — | PASS |
| p037 | policy-concern | `idempotency` | accept | True | — | — | PASS |
| p038 | policy-concern | `compensation` | accept | True | — | — | PASS |
| p039 | policy-concern | `circuit_breaker` | accept | True | — | — | PASS |
| p040 | policy-concern | `degradation` | accept | True | — | — | PASS |
| p041 | policy-concern | `fallback` | accept | True | — | — | PASS |
| p042 | policy-concern | `dependency_tolerance` | accept | True | — | — | PASS |
| p043 | policy-concern | `concurrency` | accept | True | — | — | PASS |
| p044 | policy-concern | `rate_limit` | accept | True | — | — | PASS |
| p045 | policy-concern | `queue` | accept | True | — | — | PASS |
| p046 | policy-concern | `backpressure` | accept | True | — | — | PASS |
| p047 | policy-concern | `latency` | accept | True | — | — | PASS |
| p048 | policy-concern | `throughput` | accept | True | — | — | PASS |
| p049 | policy-concern | `budget` | accept | True | — | — | PASS |
| p050 | policy-concern | `authentication` | accept | True | — | — | PASS |
| p051 | policy-concern | `authorization` | accept | True | — | — | PASS |
| p052 | policy-concern | `classification` | accept | True | — | — | PASS |
| p053 | policy-concern | `encryption` | accept | True | — | — | PASS |
| p054 | policy-concern | `audit` | accept | True | — | — | PASS |
| p055 | policy-concern | `audit@governance` | accept | True | — | — | PASS |
| p056 | policy-concern | `retention` | accept | True | — | — | PASS |
| p057 | policy-concern | `retention@data_protection` | accept | True | — | — | PASS |
| p058 | policy-concern | `approval` | accept | True | — | — | PASS |
| p059 | policy-concern | `evidence` | accept | True | — | — | PASS |
| p060 | policy-concern | `sensitivity` | accept | True | — | — | PASS |
| p061 | policy-concern | `masking` | accept | True | — | — | PASS |
| p062 | policy-concern | `minimization` | accept | True | — | — | PASS |
| p063 | policy-concern | `deletion` | accept | True | — | — | PASS |
| p064 | policy-concern | `confidence` | accept | True | — | — | PASS |
| p065 | policy-concern | `sharding` | `DCL_SEM_POLICY_CONCERN_UNKNOWN` | False | DCL_SEM_POLICY_CONCERN_UNKNOWN | — | PASS |
| p066 | policy-concern | `caching` | `DCL_SEM_POLICY_CONCERN_UNKNOWN` | False | DCL_SEM_POLICY_CONCERN_UNKNOWN | — | PASS |
| p067 | policy-concern | `logging` | `DCL_SEM_POLICY_CONCERN_UNKNOWN` | False | DCL_SEM_POLICY_CONCERN_UNKNOWN | — | PASS |
| p068 | policy-concern-family-binding | `retry@security` | `DCL_SEM_POLICY_CONCERN_WRONG_FAMILY` | False | DCL_SEM_POLICY_CONCERN_WRONG_FAMILY | — | PASS |
| p069 | policy-concern-family-binding | `audit@reliability` | `DCL_SEM_POLICY_CONCERN_WRONG_FAMILY` | False | DCL_SEM_POLICY_CONCERN_WRONG_FAMILY | — | PASS |
| p070 | value:idempotency(req/allow/forbid) | `required` | accept | True | — | — | PASS |
| p071 | value:idempotency(req/allow/forbid) | `allowed` | accept | True | — | — | PASS |
| p072 | value:idempotency(req/allow/forbid) | `forbidden` | accept | True | — | — | PASS |
| p073 | value:idempotency(req/allow/forbid) | `mandatory` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p074 | value:idempotency(req/allow/forbid) | `optional` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p075 | value:dependency_tolerance | `required` | accept | True | — | — | PASS |
| p076 | value:dependency_tolerance | `allowed` | accept | True | — | — | PASS |
| p077 | value:dependency_tolerance | `forbidden` | accept | True | — | — | PASS |
| p078 | value:dependency_tolerance | `strict` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p079 | value:dependency_tolerance | `tolerant` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p080 | value:degradation(allow/forbid) | `allowed` | accept | True | — | — | PASS |
| p081 | value:degradation(allow/forbid) | `forbidden` | accept | True | — | — | PASS |
| p082 | value:degradation(allow/forbid) | `required` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p083 | value:degradation(allow/forbid) | `graceful` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p084 | value:classification | `public` | accept | True | — | — | PASS |
| p085 | value:classification | `internal` | accept | True | — | — | PASS |
| p086 | value:classification | `confidential` | accept | True | — | — | PASS |
| p087 | value:classification | `restricted` | accept | True | — | — | PASS |
| p088 | value:classification | `secret` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p089 | value:classification | `top_secret` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p090 | value:sensitivity | `none` | accept | True | — | — | PASS |
| p091 | value:sensitivity | `personal` | accept | True | — | — | PASS |
| p092 | value:sensitivity | `sensitive` | accept | True | — | — | PASS |
| p093 | value:sensitivity | `special_category` | accept | True | — | — | PASS |
| p094 | value:sensitivity | `pii` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p095 | value:sensitivity | `high` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p096 | concern-param | `retry.limit` | `DCL_SEM_POLICY_CONCERN_UNSUPPORTED` | False | DCL_SEM_POLICY_CONCERN_UNSUPPORTED | — | PASS |
| p097 | concern-param | `circuit_breaker.trips` | `DCL_SEM_POLICY_CONCERN_UNSUPPORTED` | False | DCL_SEM_POLICY_CONCERN_UNSUPPORTED | — | PASS |
| p098 | observe-type(capability target) | `count` | accept | True | — | — | PASS |
| p099 | observe-type(effect target) | `count` | accept | True | — | — | PASS |
| p100 | observe-type(capability target) | `duration` | accept | True | — | — | PASS |
| p101 | observe-type(effect target) | `duration` | accept | True | — | — | PASS |
| p102 | observe-type(capability target) | `violations` | accept | True | — | — | PASS |
| p103 | observe-type(effect target) | `violations` | accept | True | — | — | PASS |
| p104 | observe-type(capability target) | `failures` | accept | True | — | — | PASS |
| p105 | observe-type(effect target) | `failures` | accept | True | — | — | PASS |
| p106 | observe-type(capability target) | `transitions` | accept | True | — | — | PASS |
| p107 | observe-type(effect target) | `transitions` | accept | True | — | — | PASS |
| p108 | observe-type(effect target) | `gauge` | `DCL_SEM_OBSERVE_TYPE_UNSUPPORTED` | False | DCL_SEM_OBSERVE_TYPE_UNSUPPORTED | — | PASS |
| p109 | observe-type(effect target) | `latency` | `DCL_SEM_OBSERVE_TYPE_UNSUPPORTED` | False | DCL_SEM_OBSERVE_TYPE_UNSUPPORTED | — | PASS |
| p110 | observe-type(effect target) | `rate` | `DCL_SEM_OBSERVE_TYPE_UNSUPPORTED` | False | DCL_SEM_OBSERVE_TYPE_UNSUPPORTED | — | PASS |
| p111 | observe-target | `capability` | accept | True | — | — | PASS |
| p112 | observe-target | `effect` | accept | True | — | — | PASS |
| p113 | observe-target | `outcome` | accept | True | — | — | PASS |
| p114 | observe-target | `event` | accept | True | — | — | PASS |
| p115 | observe-target | `lifecycle` | accept | True | — | — | PASS |
| p116 | observe-target | `policy` | `DCL_SEM_OBSERVE_TARGET_UNKNOWN` | False | DCL_SEM_OBSERVE_TARGET_UNKNOWN | — | PASS |
| p117 | observe-target | `actor` | `DCL_SEM_OBSERVE_TARGET_UNKNOWN` | False | DCL_SEM_OBSERVE_TARGET_UNKNOWN | — | PASS |
| p118 | observe-target | `rule` | `DCL_SEM_OBSERVE_TARGET_UNKNOWN` | False | DCL_SEM_OBSERVE_TARGET_UNKNOWN | — | PASS |
| p119 | policy-target | `capability` | accept | True | — | — | PASS |
| p120 | policy-target | `effect` | accept | True | — | — | PASS |
| p121 | policy-target | `outcome` | accept | True | — | — | PASS |
| p122 | policy-target | `event` | accept | True | — | — | PASS |
| p123 | policy-target | `lifecycle` | accept | True | — | — | PASS |
| p124 | policy-target | `capability(applies-to)` | accept | True | — | — | PASS |
| p125 | policy-target | `intent` | `DCL_SEM_POLICY_ATTACHMENT_INVALID` | False | DCL_SEM_POLICY_ATTACHMENT_INVALID | — | PASS |
| p126 | policy-target | `rule` | `DCL_SEM_POLICY_ATTACHMENT_INVALID` | False | DCL_SEM_POLICY_ATTACHMENT_INVALID | — | PASS |
| p127 | policy-target | `transition` | `DCL_SEM_POLICY_ATTACHMENT_INVALID` | False | DCL_SEM_POLICY_ATTACHMENT_INVALID | — | PASS |
| p128 | lifecycle-step-kind | `active` | accept | True | — | — | PASS |
| p129 | lifecycle-step-kind | `decision` | accept | True | — | — | PASS |
| p130 | lifecycle-step-kind | `recovery` | accept | True | — | — | PASS |
| p131 | lifecycle-step-kind | `terminal` | accept | True | — | — | PASS |
| p132 | lifecycle-step-kind | `waiting` | accept | True | — | — | PASS |
| p133 | lifecycle-step-kind | `paused` | `DCL_SEM_LIFECYCLE_STEP_KIND_INVALID` | False | DCL_SEM_LIFECYCLE_STEP_KIND_INVALID | — | PASS |
| p134 | lifecycle-step-kind | `idle` | `DCL_SEM_LIFECYCLE_STEP_KIND_INVALID` | False | DCL_SEM_LIFECYCLE_STEP_KIND_INVALID | — | PASS |
| p135 | lifecycle-trigger-kind | `outcome` | accept | True | — | — | PASS |
| p136 | lifecycle-trigger-kind | `event` | accept | True | — | — | PASS |
| p137 | lifecycle-trigger-kind | `signal` | `DCL_SEM_LIFECYCLE_TRIGGER_KIND` | False | DCL_SEM_LIFECYCLE_TRIGGER_KIND | — | PASS |
| p138 | lifecycle-trigger-kind | `policy` | `DCL_SEM_LIFECYCLE_TRIGGER_KIND` | False | DCL_SEM_LIFECYCLE_TRIGGER_KIND | — | PASS |
| p139 | wait-signal-kind | `outcome` | accept | True | — | — | PASS |
| p140 | wait-signal-kind | `event` | accept | True | — | — | PASS |
| p141 | wait-signal-kind | `signal` | `DCL_SEM_LIFECYCLE_WAIT_SIGNAL_KIND` | False | DCL_SEM_LIFECYCLE_WAIT_SIGNAL_KIND | — | PASS |
| p142 | wait-signal-kind | `message` | `DCL_SEM_LIFECYCLE_WAIT_SIGNAL_KIND` | False | DCL_SEM_LIFECYCLE_WAIT_SIGNAL_KIND | — | PASS |
| p143 | wait-signal-kind | `signal(no-from)` | `DCL_SEM_LIFECYCLE_WAIT_SIGNAL_KIND` | False | DCL_SEM_LIFECYCLE_WAIT_SIGNAL_KIND | — | PASS |
| p144 | deadline-consequence | `outcome` | accept | True | — | — | PASS |
| p145 | deadline-consequence | `event` | `DCL_SEM_LIFECYCLE_DEADLINE_CONSEQUENCE_KIND` | False | DCL_SEM_LIFECYCLE_DEADLINE_CONSEQUENCE_KIND | — | PASS |
| p146 | when-decision | `violated(rule)` | accept | True | — | — | PASS |
| p147 | when-decision | `unresolved(effect)` | accept | True | — | — | PASS |
| p148 | when-decision | `failed(legacy->unresolved)` | accept | True | — | — | PASS |
| p149 | when-decision | `broken` | `DCL_SEM_CAUSATION_DECISION_UNKNOWN` | False | DCL_SEM_CAUSATION_DECISION_UNKNOWN | — | PASS |
| p150 | when-decision | `skipped` | `DCL_SEM_CAUSATION_DECISION_UNKNOWN` | False | DCL_SEM_CAUSATION_DECISION_UNKNOWN | — | PASS |
| p151 | policy-state | `denies` | accept | True | — | — | PASS |
| p152 | policy-state | `denied` | accept | True | — | — | PASS |
| p153 | policy-state | `exhausted` | accept | True | — | — | PASS |
| p154 | policy-state | `times_out` | accept | True | — | — | PASS |
| p155 | policy-state | `open` | accept | True | — | — | PASS |
| p156 | policy-state | `degraded` | accept | True | — | — | PASS |
| p157 | policy-state | `fallback_used` | accept | True | — | — | PASS |
| p158 | policy-state | `fails` | accept | True | — | — | PASS |
| p159 | policy-state | `rejected` | `DCL_SEM_POLICY_CAUSATION_STATE_INVALID` | False | DCL_SEM_POLICY_CAUSATION_STATE_INVALID | — | PASS |
| p160 | policy-state | `throttled` | `DCL_SEM_POLICY_CAUSATION_STATE_INVALID` | False | DCL_SEM_POLICY_CAUSATION_STATE_INVALID | — | PASS |
| p161 | policy-state-concern-coupling | `times_out-without-timeout-concern` | `DCL_SEM_POLICY_CAUSATION_CONCERN_MISSING` | False | DCL_SEM_POLICY_CAUSATION_CONCERN_MISSING | — | PASS |
| p162 | attachment-constraint | `retry-without-idempotency` | `DCL_SEM_RETRY_REQUIRES_IDEMPOTENCY` | False | DCL_SEM_RETRY_REQUIRES_IDEMPOTENCY | — | PASS |
| p163 | attachment-constraint | `circuit_breaker-governs-capability` | `DCL_SEM_POLICY_CONCERN_ATTACHMENT_INVALID` | False | DCL_SEM_POLICY_CONCERN_ATTACHMENT_INVALID | — | PASS |
| p164 | attachment-constraint | `circuit_breaker-governs-effect` | accept | True | — | — | PASS |
| p165 | field-type | `Text` | accept | True | — | — | PASS |
| p166 | field-type | `Boolean` | accept | True | — | — | PASS |
| p167 | field-type | `Number` | accept | True | — | — | PASS |
| p168 | field-type | `Date` | accept | True | — | — | PASS |
| p169 | field-type | `DateTime` | accept | True | — | — | PASS |
| p170 | field-type | `Uuid` | accept | True | — | — | PASS |
| p171 | field-type | `Email` | accept | True | — | — | PASS |
| p172 | field-type | `Money` | accept | True | — | — | PASS |
| p173 | field-type | `List<Text>` | accept | True | — | — | PASS |
| p174 | field-type | `List<Number>` | accept | True | — | — | PASS |
| p175 | field-type | `shape-ref(Other)` | accept | True | — | — | PASS |
| p176 | field-type | `String(default-ctx)` | accept | True | — | — | PASS |
| p177 | field-type | `Int(default-ctx)` | accept | True | — | — | PASS |
| p178 | field-type | `String(named-ctx)` | `DCL_SEM_UNDEFINED_SYMBOL` | False | DCL_SEM_UNDEFINED_SYMBOL | — | PASS |
| p179 | field-type | `Int(named-ctx)` | `DCL_SEM_UNDEFINED_SYMBOL` | False | DCL_SEM_UNDEFINED_SYMBOL | — | PASS |
| p180 | field-type | `shape-shadow(Text)` | `DCL_SEM_TYPE_BUILTIN_SHADOWED` | False | DCL_SEM_TYPE_BUILTIN_SHADOWED | — | PASS |
| p181 | duration-unit | `ms` | accept | True | — | — | PASS |
| p182 | duration-unit | `millisecond` | accept | True | — | — | PASS |
| p183 | duration-unit | `milliseconds` | accept | True | — | — | PASS |
| p184 | duration-unit | `s` | accept | True | — | — | PASS |
| p185 | duration-unit | `second` | accept | True | — | — | PASS |
| p186 | duration-unit | `seconds` | accept | True | — | — | PASS |
| p187 | duration-unit | `m` | accept | True | — | — | PASS |
| p188 | duration-unit | `minute` | accept | True | — | — | PASS |
| p189 | duration-unit | `minutes` | accept | True | — | — | PASS |
| p190 | duration-unit | `h` | accept | True | — | — | PASS |
| p191 | duration-unit | `hour` | accept | True | — | — | PASS |
| p192 | duration-unit | `hours` | accept | True | — | — | PASS |
| p193 | duration-unit | `d` | accept | True | — | — | PASS |
| p194 | duration-unit | `day` | accept | True | — | — | PASS |
| p195 | duration-unit | `days` | accept | True | — | — | PASS |
| p196 | duration-unit | `500ms(single-token)` | accept | True | — | — | PASS |
| p197 | duration-unit | `week` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p198 | duration-unit | `weeks` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p199 | duration-unit | `fortnight` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p200 | period-unit | `day` | accept | True | — | — | PASS |
| p201 | period-unit | `days` | accept | True | — | — | PASS |
| p202 | period-unit | `month` | accept | True | — | — | PASS |
| p203 | period-unit | `months` | accept | True | — | — | PASS |
| p204 | period-unit | `year` | accept | True | — | — | PASS |
| p205 | period-unit | `years` | accept | True | — | — | PASS |
| p206 | period-unit | `weeks` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p207 | period-unit | `hours` | `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` | False | DCL_SEM_POLICY_CONCERN_VALUE_INVALID | — | PASS |
| p208 | language-version | `1.0` | accept | True | — | — | PASS |
| p209 | language-version | `9.9` | accept | True | — | — | PASS |
| p210 | language-name | `foo` | `DCL_PARSE_LANGUAGE_UNSUPPORTED` | False | DCL_PARSE_LANGUAGE_UNSUPPORTED | — | PASS |
| p211 | capability-section | `unknown(gadgets)` | `DCL_PARSE_UNKNOWN_CAPABILITY_SECTION` | False | DCL_SEM_OUTCOME_CAUSE_REQUIRED, DCL_PARSE_UNKNOWN_CAPABILITY_SECTION, DCL_PARSE_UNKNOWN_CAPABILITY_SECTION, DCL_PARSE_EXPECTED_DECLARATION, DCL_PARSE_EXPECTED_DECLARATION, DCL_PARSE_UNEXPECTED_TOKEN, DCL_PARSE_UNEXPECTED_TOKEN | — | PASS |
| p212 | top-level-decl | `unknown(widget)` | `DCL_PARSE_EXPECTED_DECLARATION` | False | DCL_PARSE_EXPECTED_DECLARATION | — | PASS |
| p213 | capability-local-effect-decl | `effect-is-kind-inside-capability` | `DCL_PARSE_LOCAL_EFFECT_DECL_UNSUPPORTED` | False | DCL_PARSE_LOCAL_EFFECT_DECL_UNSUPPORTED | — | PASS |
| p214 | structure | `private-modifiers` | accept | True | — | — | PASS |
| p215 | structure | `context-and-depends-on` | accept | True | — | DCL_SEM_UNUSED_DEPENDENCY | PASS |
| p216 | structure | `intents-block` | accept | True | — | — | PASS |
| p217 | structure | `actors-block+requires-decision` | accept | True | — | — | PASS |
| p218 | structure | `rule-single-line` | accept | True | — | — | PASS |
| p219 | structure | `outcome-with-payload` | accept | True | — | — | PASS |
| p220 | structure | `event-named-type-payload` | accept | True | — | — | PASS |
| p221 | structure | `effect-after-ordering` | accept | True | — | — | PASS |
| p222 | structure | `supervises-lifecycle` | accept | True | — | — | PASS |
| p223 | structure | `step-recovery` | accept | True | — | — | PASS |
| p224 | policy-family | `(none-declared)` | `DCL_SEM_POLICY_FAMILY_REQUIRED` | False | DCL_SEM_POLICY_FAMILY_REQUIRED | — | PASS |
| p225 | language-version | `(header-omitted)` | accept | True | — | DCL_VERSION_DECL_MISSING | PASS |
| p226 | structure | `published-skeleton-verbatim` | accept | True | — | — | PASS |

## Slot coverage

- **actor-kind**: 7 probes (4 accept / 3 reject)
- **attachment-constraint**: 3 probes (1 accept / 2 reject)
- **capability-local-effect-decl**: 1 probes (0 accept / 1 reject)
- **capability-section**: 1 probes (0 accept / 1 reject)
- **concern-param**: 2 probes (0 accept / 2 reject)
- **deadline-consequence**: 2 probes (1 accept / 1 reject)
- **duration-unit**: 19 probes (16 accept / 3 reject)
- **effect-kind**: 10 probes (7 accept / 3 reject)
- **effect-kind-block-form**: 1 probes (1 accept / 0 reject)
- **field-type**: 16 probes (13 accept / 3 reject)
- **language-name**: 1 probes (0 accept / 1 reject)
- **language-version**: 3 probes (3 accept / 0 reject)
- **lifecycle-step-kind**: 7 probes (5 accept / 2 reject)
- **lifecycle-trigger-kind**: 4 probes (2 accept / 2 reject)
- **observe-target**: 8 probes (5 accept / 3 reject)
- **observe-type(capability target)**: 5 probes (5 accept / 0 reject)
- **observe-type(effect target)**: 8 probes (5 accept / 3 reject)
- **period-unit**: 8 probes (6 accept / 2 reject)
- **policy-concern**: 34 probes (31 accept / 3 reject)
- **policy-concern-family-binding**: 2 probes (0 accept / 2 reject)
- **policy-family**: 13 probes (9 accept / 4 reject)
- **policy-kind**: 4 probes (1 accept / 3 reject)
- **policy-state**: 10 probes (8 accept / 2 reject)
- **policy-state-concern-coupling**: 1 probes (0 accept / 1 reject)
- **policy-target**: 9 probes (6 accept / 3 reject)
- **structure**: 11 probes (11 accept / 0 reject)
- **top-level-decl**: 1 probes (0 accept / 1 reject)
- **value:classification**: 6 probes (4 accept / 2 reject)
- **value:degradation(allow/forbid)**: 4 probes (2 accept / 2 reject)
- **value:dependency_tolerance**: 5 probes (3 accept / 2 reject)
- **value:idempotency(req/allow/forbid)**: 5 probes (3 accept / 2 reject)
- **value:sensitivity**: 6 probes (4 accept / 2 reject)
- **wait-signal-kind**: 5 probes (2 accept / 3 reject)
- **when-decision**: 5 probes (3 accept / 2 reject)

## Sanity anchors (required reproductions)

- `machine` (actor-kind): REJECTED with DCL_SEM_ACTOR_KIND_UNKNOWN — reproduces the prior-run rejection. (PASS)
- `in_memory` (effect-kind): REJECTED with DCL_SEM_EFFECT_KIND_UNKNOWN — reproduces the prior-run rejection. (PASS)

## Findings (drift / quirks / rules discovered by probing)

1. **No extracted literal was rejected and no invented literal was accepted for any closed enum slot** — the Go source enum sets at the pin match the vendored WASM checker exactly (actor kinds, effect kinds, policy families, policy kind, all 29 concerns, concern enum values, observation types, observe targets, policy attachment targets, lifecycle step kinds, trigger kinds, wait signal kinds, deadline consequence, when decisions, policy causation states, duration units, period units, builtin field types).
2. **WASM version gate is inert**: `language dcl 9.9` compiles ok in the vendored WASM checker (p209). Root cause: `validateLanguageVersions` skips when the version manifest is unresolvable, and the WASM build cannot read version.json (the harness's documented ENOSYS file-walk). The native CLI at the pin (version.json supports=1.0) would emit `DCL_VERSION_UNSUPPORTED`. Consequence: always author `language dcl 1.0`; do not rely on the checker to catch version typos.
3. **Unknown field types pass silently in the default context**: `x: String` / `x: Int` compile ok when no `context` is declared (p176–p177; `compiler.go validateType` returns without error when the shape is unresolvable in the default context). Inside a named context they correctly fail `DCL_SEM_UNDEFINED_SYMBOL` (p178–p179). Consequence: type-name typos are NOT compiler-caught in single-context files — the vocab file's builtin list is the only guard.
4. **Attachment constraints discovered mid-probe** (initial expectations corrected from source): a `retry` policy attached to a target requires `idempotency allowed|required` on the same target (`DCL_SEM_RETRY_REQUIRES_IDEMPOTENCY`, policy_effective.go:191); `circuit_breaker` may only govern effects (`DCL_SEM_POLICY_CONCERN_ATTACHMENT_INVALID`, compiler.go:1385). Both now covered by dedicated probes (attachment-constraint slot).
5. **Wait-signal kind is enforced even without `from`** — contrary to a first source reading of the early-return in `waitTriggerIR`, `waits for signal X` (no `from`) is rejected `DCL_SEM_LIFECYCLE_WAIT_SIGNAL_KIND` (p143). The closed set {event, outcome} holds unconditionally.
6. **Legacy effect kinds** `notify`/`persist`/`invoke` are accept-with-warning (`DCL_SEM_EFFECT_KIND_LEGACY`) and normalize to notification/persistence/invocation (p011–p013).
7. **`recovery` targets are capabilities/effects, not lifecycle states**: `recovery <State>` fails (`DCL_SEM_LIFECYCLE_RECOVERY_TARGET_UNKNOWN` + `DCL_SEM_LIFECYCLE_RECOVERY_RESULT_TRANSITION_MISSING`); the verified working shape is a contributor capability with a `move … from <target>` transition (p223).
8. **`undefinedSymbolCode()` (compiler.go:1853)** composes `DCL_SEM_UNKNOWN_<KIND>` codes at runtime for the default context and `DCL_SEM_UNDEFINED_SYMBOL` for named contexts — these are reference-resolution codes, not enum-membership codes; the closed-enum codes probed here are the static ones listed per slot.

License note: upstream is Apache-2.0; the clone retains its LICENSE and NOTICE. The vendored checker directory ships its own LICENSE/NOTICE/PROVENANCE.md.

# Accepted Decisions

This file records durable accepted product/architecture decisions and concise
supersession boundaries. Detailed experiment transcripts, benchmark tables,
CI logs, device checklists, and release execution evidence remain in the
referenced evidence documents or Git history. Historical decisions are retained
when their rationale or supersession remains useful; a superseded clause is
not current authority.

## D001–D021 — project and initial architecture

### D001 — Android first
Android is the first target platform; other platforms are separate tracks.

### D002 — Pinyin/Shuangpin primary input; MoQi auxiliary
Pinyin and Shuangpin remain primary input. MoQi is an Auxiliary Filter, not a
decoder or replacement input engine.

### D003 — MoQi interaction
MoQi uses the bounded on-demand per-character/word interaction: filter,
partial-select, preserve composition, continue typing, and permit another
filter pass. It must not force whole-string commit.

### D004 — shared Auxiliary Filter infrastructure
Reuse and minimally generalize the upstream Stroke Filter infrastructure.

### D005 — trigger/implementation separation
The Auxiliary Filter trigger enters the configured implementation. It is not
hard-bound to Stroke or MoQi and no general plugin framework is introduced.

### D006 — MoQi target semantics
MoQi filters the target character after the current selection frontier. It does
not inherit Stroke’s arbitrary-character-in-phrase predicate.

### D007 — LibIME boundary
Reuse LibIME partial-selection and composition APIs. LibIME remains unmodified
unless a new, concrete source/API conflict is accepted.

### D008 — fixed MoQi table
The product table is `gaboolic/moqima-tables@6d8ba8f1c57466f358e682baefe11bbd0fe389ab`,
file `moqima_gb18030.txt`, MIT. The pin, digest, and configure-time packaging
are the single source for the product table.

### D009 — Rime reference
Rime is a reference/alternative, not a hard dependency.

### D010 — Android generic configuration
Reuse the existing generic Fcitx configuration UI and descriptor path.

### D011 — data/update separation
Dictionary updates and user-input upload are independent. Enabling an update
does not authorize uploading user input.

### D012 — default Voice trigger
The microphone button is the default Voice trigger.

### D013 — optional Space trigger
Long-press Space may trigger the same Voice Input flow; it does not create a
second pipeline.

### D014–D015 — System ASR boundary
Reuse Android SpeechRecognizer/upstream-compatible work. System
SpeechRecognizer/RecognitionService is one optional ASR backend, not the whole
Voice architecture and not the internal Provider abstraction.

### D016 — Provider independence
Voice flow, ASR backend, and concrete Provider remain separate. Provider changes
must not change the trigger/session contract.

### D017 — ASR and post-processing separation
ASR ends at Raw Transcript. Optional TextPostProcessor is independently
configurable and fully disableable. The provider-neutral seam is implemented
and retained by Android PR #15; configured processor/provider is NONE/null/
disabled, so the current product path is ASR → Raw Transcript → IME.
The tested 0.6B–1B Local-LLM route is STOPPED after the quality gate failed;
llama.cpp/JNI/GGUF runtime was removed. Cloud LLM is not implemented/planned.
A concrete processor requires a separate decision/task.

### D018 — auditable Voice data flow
Voice routing, lifecycle, receiving party, fallback, and termination must be
auditable without default transcript/audio/credential/endpoint-content logging.
Content-level transcript logging requires a separate explicit privacy decision.

### D019–D021 — repository and scope boundaries
Fusion is the controller repository; upstream forks remain separate. Do not
choose a repository-wide license prematurely. Prefer minimal, reviewable
changes and existing upstream infrastructure over parallel abstractions.

## D022–D040 — productization decisions

### D022 — batched validation
Validation is staged after source/diff review and uses the applicable local,
CI, device, and service route; a lower gate never substitutes for a higher one.

### D023 — configuration persistence
Auxiliary Filter persistence follows the upstream path; unit tests need not
claim filesystem persistence they cannot exercise.

### D024 — MoQi Android packaging
The addon retrieves the fixed table at configure time and installs it through
the config component; Android requires no MoQi-specific product source change.

### D025 — historical MoQi release identity
The old `.moqi` package/signing line is historical and separate from Fusion
Enhanced. It is not the current signer or migration path.

### D026 — no single OEM System ASR dependency
System RecognitionService cannot be the only usable Voice path.

### D027 — Architecture A VoiceBackend
Voice uses an internal VoiceBackend boundary:
SystemAsrBackend → SpeechRecognizer/RecognitionService, and DirectAsrBackend →
Fcitx-owned AudioRecord → configured Local/Managed/Self-hosted Provider.
This is not a public plugin framework.

### D028 — Provider categories and scope
The logical categories are System, Local, Managed Cloud, and Self-hosted.
Provider-specific implementations are acceptable; no generic protocol/plugin
framework is required. Current Managed Cloud scope is Doubao, Alibaba/Qwen, and
Tencent.

### D029 — Provider-specific settings
Provider credentials/configuration are independent, securely stored, and never
cross-reused. Local models are separately managed from the Local runtime.
Maintainer credentials never enter source, CI, APK, or release artifacts.

### D030 — Voice visibility
Voice trigger visibility follows configured-backend semantics and availability,
not a hardcoded System-ASR assumption.

### D031 — shared Voice panel
Mic and Space sessions use shared lifecycle/panel semantics; Direct capture may
provide a real level visualization, while System uses a non-PCM indicator.

### D032 — historical Local A/B study
The first A/B Local comparison was a bounded research/device study with external
models. Its evidence remains historical and does not select the current model
set.

### D033 — four Provider categories
All Providers use the same Voice flow. Self-hosted does not create a separate
pipeline. Historical checkpoint claims that Qwen/Tencent real-device work was
pending are superseded by later owner acceptance; Self-hosted device testing is
DEFERRED/non-blocking.

### D034 — selection and first recommendation
Users configure/enable concrete services; “current service” selects one. First
recommendation is one-time and Local-first, then disclosed/authorized System,
then configuration guidance. It never silently selects a cloud/self-hosted
service or rewrites the user’s selection.

### D035 — bounded runtime fallback
Only a selected external/network ASR may fall back on early technical/service
failure before usable session establishment. The target is one eligible,
installed, enabled, runtime-ready production Local ASR. System is never an
automatic target; there is no external-to-external chaining, quality-triggered
fallback, post-establishment migration, or PCM replay. `onStarted` is not
session establishment. The core early-failure path is DEVICE VERIFIED /
COMPLETE; edge/race permutations are not a reopened core gate.

### D036–D038 — Local model selection
The old A/B checkpoint remains historical. Current product models and order are
fixed by D050. Each Local model is an independently enabled/selectable service;
installed, enabled, current, production, recommendation eligibility, and
runtime readiness remain separate dimensions.

### D039–D040 — dictionary distribution
Dictionary distribution uses fixed, reproducible, license-reviewed candidates
and preserves the required license/provenance boundaries. D080 closes the
productized Dictionary Manager update path.

## D045–D055 — retained boundaries and Voice architecture

### D045 — current Local recommendation
The current Local model set and recommendation semantics are governed by D050;
the old Zipformer research collection is not restored.

### D046–D049 — UI boundaries
Toolbar configuration is canonical state projected by the UI; runtime width does
not rewrite it. Voice Settings is presentation/navigation and does not change
Provider, dictionary, or lifecycle semantics. Toolbar/Voice Settings device
regression and defect closure are COMPLETE.

### D050 — current Local ASR release line
Current production/recommendation-eligible Local order is:
X-ASR offline INT8 → X-ASR 960 ms streaming INT8 → FunASR Nano.
Models are downloaded from fixed upstream sources on demand; weights are not
bundled, mirrored, or project-hosted. Core release-device lifecycle and
abnormal/error Model Manager paths are COMPLETE / DEVICE VERIFIED. Provenance,
license, and NOTICE closure is COMPLETE; do not create another audit task.

### D051 — paired punctuation
The experimental paired-punctuation extension is PAUSED and excluded from the
first-release product scope by D066. Do not treat its historical experiment as
a current product task.

### D052–D053 — MoQi downstream boundary
MoQi remains downstream-only. Upstream contribution work is closed/non-blocking;
the product table and Auxiliary Filter semantics remain.

### D054 — Fusion Enhanced identity
The current Fusion Enhanced application identity is distinct from historical
MoQi identity and does not perform old-install migration.

### D055 — top-level Voice providers
External Android Voice Input, System ASR, Local, Managed Cloud, and Self-hosted
are top-level provider choices with the existing ownership/selection semantics.

## D056–D068 — release and authority closure

### D056 — Local release JNI closure
The sherpa-onnx R8/JNI runtime issue was fixed with the accepted package keep
boundary and closed by release/minified three-engine device verification.

### D057 — System ASR diagnostics
System ASR runtime failure must be visible/diagnosable within the accepted
SpeechRecognizer boundary. Do not add ROM-specific service selection or rewrite
system settings.

### D058 — release signing identity
Fusion Enhanced has its own permanent release signing identity, separate from
historical MoQi and debug identities.

### D059 — Local distribution four-rights closure
Bundle, mirror/re-host, fixed-upstream in-app download, and manual import are
separate rights. The fixed-upstream download path is approved; project
mirroring/bundling is not. `licenseAuditComplete` is disclosure state, not a
download gate. Reopen only under D059’s explicit conditions.

### D060 — stable baseline and authority
`docs/first-release-baseline.md` is the single first-release current-state
matrix. Other documents point to it rather than duplicating a competing matrix.

### D061 / D066 — punctuation and RC supersession
D061’s acceptance of the expanded punctuation pin was superseded by D066:
D051 is outside first-release scope, the release pin is `47401b04`, and RC.1
was rejected. These are historical release-boundary decisions, not current
punctuation work.

### D063–D064 — signed RC and debug identity
Signed RC production promotes the exact tested artifact; debug identity is
separate and reproducibly verified. Do not mix identities or rebuild a tested
release artifact.

### D068 — first release
RC.2 was exactly promoted and the first Fusion Enhanced release was published.
Release evidence is historical; post-release development state is tracked by
the current baseline/ROADMAP.

## D069–D080 — Mixed Input, governance, lexicon, and latest release

### D069–D071 — Mixed Input foundations
Preserve the accepted bounded mixed-input architecture, separate sourcing/
lexicon/learning ownership, raw/output alignment, selection frontier, partial
selection, and canonical/literal semantics. These decisions are not licenses
to revive superseded Architecture A' or old ranking experiments.

### D072 — Windows boundary
Windows Fusion is a separate product/research track with authority in
`docs/windows-architecture.md`.

### D073–D075 — M2+/r4 closure
D073’s M3-B proposal was not accepted. D074 preserves the mixed-input contract
and explicitly supersedes A' as product architecture. D075 accepts M2+/r4 as
the current Mixed Input architecture baseline; A' is historical/reference,
architecture competition is CLOSED, and no r5/r6 or new held-out competition is
planned. Phase 11 productization and merged Android integration are
VERIFIED / COMPLETE.

### D076 — branch governance
Canonical branches, PR/review flow, gitlink reachability, and deletion
preconditions are governed by `docs/branch-policy.md`.

### D077 — versioning
Fusion versions use the canonical upstream-version + `-fusion.N` policy.

### D078–D079 — English lexicon
The current English Core uses the accepted single bundled lexicon policy and
the D079 Ice/Frost/curated replacement. Android Spell remains a separate
responsibility. Do not reopen the retired SCOWL comparison or invent ranking/
metadata work.

### D080 — v0.1.3-fusion.7 and Dictionary Manager closure
The v0.1.3-fusion.7 exact-artifact release, addons pin advancement, and
productized Dictionary Manager Phase 5D are recorded as COMPLETE / historical
release facts. Do not treat the old Phase 5D forward pointer or release
execution transcript as current NEXT.

## Current authority rule

For current product state, use `docs/first-release-baseline.md` and the
compact current-next section in `docs/ROADMAP.md`. For requirements use
`docs/REQUIREMENTS.md`. For evidence use the referenced checkpoint/report
documents; their historical PENDING/NOT RUN rows do not reopen later CLOSED,
VERIFIED, STOPPED, or DEFERRED facts.

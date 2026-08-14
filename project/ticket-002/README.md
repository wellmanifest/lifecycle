# Ticket 002: Validate lifecycle ecosystem conformance

- **ID**: ticket-002
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-14

## Goal and scope

Validate the general Lifecycle DSL against every current Wellmanifest
`*-lifecycle` domain, publish one deterministic multi-domain projection bundle,
and make the reference validator usable as one byte-pinned standalone file for
offline adoption. Record only ecosystem-derived extensions that preserve the
core boundary: the DSL describes lifecycle decisions but never executes them.

## Acceptance criteria

- [ ] AC-01: One Lifecycle DSL bundle represents Git, ticket, legal, product,
  SaaS and Twin lifecycle graphs without importing their domain payloads.
- [ ] AC-02: The reference validator accepts the ecosystem bundle and tests
  bind every expected lifecycle, initial/terminal state and representative
  feedback transition.
- [ ] AC-03: A byte-identical copy of `src/lifecycle.py` works without the
  repository error catalog while explicit catalog validation remains supported.
- [ ] AC-04: The specification records reusable findings from the domain
  standards and current public workflow/state-machine specifications while
  keeping execution, retries, timeouts and authority outside Lifecycle DSL v1.
- [ ] AC-05: Unit, static, container and adopted governance checks pass with no
  runtime dependency or network access.

## Risks

- A projection could invent a domain transition that its owning standard does
  not define. Profiles therefore distinguish commands from externally observed
  events and remain compatibility projections, not replacements for domain
  conformance.
- Embedding diagnostics could drift from `errors/catalog.json`. Tests require
  exact equality between both representations.
- Workflow-engine features could blur the non-executing trust boundary. They
  are recorded as explicitly deferred profile/runtime concerns.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

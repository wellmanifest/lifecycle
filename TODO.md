# Roadmap

## Active

- [ ] [`ticket-001`](project/ticket-001/README.md): define Lifecycle DSL v1,
  implement its deterministic validator and stable error catalog, and prove
  the Git branch and governed-ticket profiles.
  - [x] Specify and implement the five-file Lifecycle DSL v1 slice.
  - [x] Pass host, static, governance, and networkless-container validation.
  - [x] Attempt todo2code semantic review in required-LLM mode and record the
    provider-limit failure without silent fallback.
  - [ ] Obtain trusted current-head review, merge, and verify ticket-branch
    deletion.

## Later

- [ ] Add deployment, service, release, and infrastructure lifecycle profiles
  only through separately bounded tickets.
- [ ] Add advisory LLM-assisted profile authoring after deterministic fixtures
  and provenance recording are defined.
- [ ] Publish language bindings only after the core text and JSON contracts are
  stable.

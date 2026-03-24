# map-capabilities Contract

Shared source of truth for the `map-capabilities` workflow across Claude and Codex adapters.

## Goal

Generate one capability document per catalog entry through a Researcher -> Writer -> Judge workflow with resumability.

## Phase 1: Prepare

- Load the catalog and initialize or resume `wave-progress.json`.
- Show current status to the user.
- Do not process a new wave without explicit approval.

## Phase 2: Wave Execution

For each wave:

- Determine the next batch of slugs.
- For each slug:
  - save `entry.json`
  - fetch `readme-raw.md`
  - optionally fetch `compose-raw.md`
- Spawn one `researcher` per slug.
- Save each `factsheet.json`.
- Spawn one `writer` per slug.
- Save each `capability.md`.
- Spawn one `judge` for the wave.
- Mark slugs done or failed based on judge feedback.

## Phase 3: Report

- Show completed, failed, in-progress, and remaining work.
- Resume from `wave-progress.json` on the next run.

## Hard Invariants

- Researchers operate only on prefetched entry, README, and compose artifacts.
- Researchers must be spawned with `allowed-tools: []`.
- Writers require a valid factsheet.
- Judges review generated capability docs, not prompts alone.
- Output validation can reject malformed `capability.md`.
- The workflow is resumable from `wave-progress.json`.

# Home Assistant Integration Gate — 16 November 2026

## Decision

**Not certified.** The repository does not contain an authorized Home Assistant entity inventory, a reviewed backend/integration design, or verified circuit mapping for A3/A4. The V2 Demo remains browser-local simulation only.

This is a deliberate safety boundary: no entity IDs, tokens, passwords, authorization headers, or live-control endpoints were guessed or added.

## Evidence checked

- `config/device-mapping.example.json` remains `schemaVersion: "0.1-draft"` and `status: "placeholder-unverified"`.
- All `entityId` and `circuit` fields in the draft mapping are `null`.
- `docs/PLATFORM_SOURCE_HANDOFF_2026-11-13.md` still records Home Assistant administrator responses as pending.
- Breaker panels are explicitly `select` / `visual-only`; no hardware control authorization is recorded.
- `app/room_3d_preview_v2.html` uses local browser state and does not call Home Assistant.

## What must be supplied before certification

### Authorized inventory

A Home Assistant administrator or project owner must provide a reviewed, non-secret inventory containing at least:

| Field | Required value |
|---|---|
| `objectId` / stable GLB node name | Exact canonical model node |
| `roomId` | `A3`, `A4`, or `A3_A4_TRANSITION` |
| `entity_id` | Exact HA entity ID, supplied by the administrator |
| Domain | `light`, `switch`, `climate`, `media_player`, `camera`, or approved domain |
| Read-only or control | Explicit capability approval |
| Expected state/attributes | State schema and unavailable behavior |
| Circuit | Verified electrical schedule/panel mapping, or `unverified` |
| Owner/approval reference | Person/team and date approving the row |

Do not place tokens or secrets in the inventory or Git.

### Backend/security boundary

The platform owner and Home Assistant administrator must approve:

1. Browser code never receives a long-lived HA token.
2. Browser calls an authenticated project backend or integration layer only.
3. Backend stores secrets in its secret manager/environment, not in HTML, GLB, Git, or client URLs.
4. Backend allowlists entity IDs and service/domain actions; arbitrary entity/service passthrough is prohibited.
5. Read-only state endpoints are separated from write/control endpoints.
6. Authentication, authorization, audit logging, rate limiting, CORS/origin policy, and failure behavior are documented.
7. Breaker hardware remains visual-only unless written professional and platform authorization is supplied.
8. Development testing uses a sandbox or explicitly approved non-production entities.

### Circuit mapping

Circuit assignments must come from the approved electrical schedule or responsible owner. The current visual grouping in V2 is not evidence of the real electrical circuit:

- A3: SE/NE/transition-south outlets, AC A3, A3 light switch
- A4: transition-north/SW/NW outlets, AC A4, A4 and transition light switches

These are demo simulation groups only until the electrical mapping is verified.

## Certification checklist

- [ ] Authorized A3/A4 entity inventory received
- [ ] Entity IDs and domains verified against Home Assistant
- [ ] Read-only state display approved
- [ ] Backend/security boundary reviewed and named
- [ ] Circuit mapping verified by responsible owner
- [ ] Control actions explicitly approved per entity
- [ ] Breaker hardware authorization recorded, or kept visual-only
- [ ] Sandbox test completed without affecting live users/devices
- [ ] No secrets committed or exposed
- [ ] `config/device-mapping.example.json` updated from draft only after approval

## Current status

```text
Entity inventory          BLOCKED — not supplied/authorized
Backend boundary          BLOCKED — not supplied/reviewed
Circuit mapping           BLOCKED — not verified
Live Home Assistant I/O   DISABLED
Breaker hardware control  NOT AUTHORIZED — visual-only
V2 browser simulation     AVAILABLE
```

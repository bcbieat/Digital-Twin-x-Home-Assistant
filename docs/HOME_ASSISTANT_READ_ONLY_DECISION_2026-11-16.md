# Home Assistant Read-Only Integration Decision — 16 November 2026

## Decision

The intended integration mode is **read-only Home Assistant state display**. The V2 Demo may display approved device state from Home Assistant in the future, but it must not send control commands. Breaker panels and breaker levers remain **visual-only browser simulation**.

## Current implementation status

**Not enabled yet.** The repository does not contain the minimum authorized inputs required to safely implement a live read-only connection:

- approved A3/A4 Home Assistant entity inventory;
- entity domains, state schema, and unavailable-state behavior;
- named backend/integration endpoint owned by the platform team;
- approved authentication/session model that keeps HA credentials out of browser code;
- owner and date approving the inventory and read-only scope;
- verified circuit mapping.

No Home Assistant URL, token, entity ID, secret, or live endpoint was guessed or added.

## Required implementation boundary

```text
Browser V2 Demo
      ↓ authenticated read-only request
Approved project backend / integration layer
      ↓ server-side credentials only
Home Assistant
```

The browser must not connect directly to Home Assistant with a long-lived token. The backend must expose an allowlisted read-only state projection rather than arbitrary entity/service passthrough.

## Explicitly disabled

- Home Assistant write/service calls
- breaker hardware control
- arbitrary entity lookup from browser input
- credentials or authorization headers in HTML, GLB, Git, or URLs
- circuit control inferred from the current visual simulation grouping

## Enablement checklist

- [ ] Home Assistant administrator supplies a reviewed, non-secret entity inventory
- [ ] Platform owner names the backend endpoint and environment
- [ ] Security review approves authentication, authorization, CORS, logging, rate limits, and failure behavior
- [ ] Read-only domains/entities are allowlisted
- [ ] Entity state/attributes and `unavailable` behavior are documented
- [ ] Circuit mapping is verified separately by the responsible owner
- [ ] Sandbox/test entities are approved
- [ ] Browser integration test passes without write calls
- [ ] Breaker visual-only regression test passes

Until these items are complete, V2 remains on browser-local simulation and this decision is a target mode, not a live integration claim.

## Related records

- `docs/HOME_ASSISTANT_INTEGRATION_GATE_2026-11-16.md`
- `docs/PLATFORM_SOURCE_HANDOFF_2026-11-13.md`
- `config/device-mapping.example.json`
- `app/room_3d_preview_v2.html`

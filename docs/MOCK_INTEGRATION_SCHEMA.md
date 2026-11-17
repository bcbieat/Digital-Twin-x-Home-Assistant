# A3/A4 Mock Integration Schema

**Status:** mock-only, browser/repository fixture; no Home Assistant connection
**Version:** 0.2 mapping / 0.1 state
**Purpose:** prepare the data contract for the future approved read-only integration without guessing B1/B2/B3 entity IDs or credentials.

## Scope

The mock contract covers the measured room assets:

- `A3`
- `A3_A4_TRANSITION`
- `A4`

Canonical `objectId`, `nodeName`, room tokens, and GLB paths follow `docs/ASSET_IDENTITY_COORDINATE_CONTRACT.md` and `docs/INTERIOR_ASSET_PLAN.md`. Manual/protected model positions are not changed by this schema work.

## Files

- `config/device-mapping.schema.json` — JSON Schema for room/device/entity mapping.
- `config/device-mapping.mock.json` — synthetic fixture for A3, transition, and A4.
- `config/device-state.schema.json` — JSON Schema for one UI-facing normalized state projection.
- `config/device-state.mock.json` — one sample `available`/`on` state fixture.
- `config/device-states.schema.json` — JSON Schema for a collection of mock state fixtures.
- `config/device-states.mock.json` — mock state collection for A3, transition, and A4.
- `config/device-activity.schema.json` / `config/device-activity.mock.json` — mock state-transition events, including a missing cause when no cause is recorded.
- `config/device-history.schema.json` / `config/device-history.mock.json` — mock state and measurement samples for the historical viewer.
- `config/device-mapping.example.json` — existing pre-approval draft; entity and circuit values remain null.

The mock mapping uses only synthetic IDs matching `mock.*`. It contains no B1 entity IDs, Home Assistant URL, token, cookie, MQTT credential, camera URL, or secret.

## Mapping model

```text
room
  └── device (canonical 3D object)
        └── entities[] (zero, one, or many HA-shaped mock entities)
```

### Room

- `roomId` is a machine token: `A3`, `A3_A4_TRANSITION`, or `A4`.
- `assetFile` identifies the measured GLB used by the current Web Demo.
- Devices are room-scoped; a device must not appear under another room without an explicit mapping decision.

### Device

- `objectId` and `nodeName` use the canonical measured asset identity.
- `displayName` is localized UI text and must not replace the machine ID.
- `deviceType` describes the Digital Twin object, not necessarily the Home Assistant domain.
- `entities[]` is an array because one physical device may expose multiple entities (for example climate + temperature + power).
- `circuit` remains null until the responsible owner verifies it.

### Entity mapping

Each entity mapping contains:

- synthetic `entityId` such as `mock.a3_ac_01`;
- `domain` such as `light`, `switch`, `climate`, `sensor`, or `media_player`;
- a semantic `role` such as `primary_state`, `temperature`, or `power`;
- `readOnly: true`.

The eventual approved inventory may replace the synthetic ID and update the domain/role only after administrator and platform-owner review. Do not copy B1 IDs into this fixture.

## Normalized state model

`config/device-state.schema.json` defines a UI-facing state projection independent of Home Assistant transport:

| Field | Meaning |
|---|---|
| `state` | Current value, or null when unavailable/unknown |
| `availability` | `available`, `unavailable`, or `unknown` |
| `freshness` | `fresh` or `stale` according to backend policy |
| `updatedAt` | Last time the projection was received/generated |
| `lastChanged` | Last known state transition, nullable |
| `attributes` | Safe, allowlisted display attributes only |
| `source` | `mock` in this phase |

State semantics:

- `off` means the state was read successfully and the device reports off.
- `unavailable` means the source cannot currently provide a state; it must not be rendered as off.
- `unknown` means a state has not been established.
- `stale` means a value exists but exceeds the approved freshness threshold.
- `loading` and `error` are UI/request states and should be represented by the adapter/UI layer, not confused with a device's HA state.

## Access policy for mock phase

Every mock device is:

```json
{
  "visible": true,
  "webControl": false,
  "userControl": false,
  "automationControl": false,
  "adminConfig": false
}
```

Breaker panels have no entities and `integration.mode: "visual-only"`. This does not authorize electrical control. The mock UI must label all state as simulated and must not call Home Assistant services.

## UI prototype adapter

`app/room_3d_preview_v2.html` loads the mapping, state, activity, and history mock fixtures with browser `fetch()` and renders a read-only **Mock HA state** panel in the Control Desk. The room buttons filter every mock view by `roomId`; devices with multiple state rows are summarized as one device with an entity count. `unavailable`, `unknown`, `stale`, and `visual-only` remain visibly distinct.

The Activity tab shows event type, before/after state, timestamp, mock source, and an explicit “Cause not recorded” fallback. The History tab shows chronological state/measurement samples and preserves unavailable/stale semantics rather than converting them to off.

The existing breaker/device controls remain local presentation simulation and are not connected to the fixture state or Home Assistant. The fixture panel is labelled mock/read-only and does not provide a service-call path.

Selecting Room A3 now uses a preview camera pose based on the observed A3 camera anchor. Selecting Room A4 uses a planned NW-corner camera pose at the same height reference. This is a browser camera-view preview only: no A4 Blender camera/device transform was created or moved, and the A4 camera mapping/state remains explicitly planned/unknown until installation and survey confirmation.

## Future integration boundary

```text
Home Assistant
      ↓ approved server-side adapter
Project backend
      ↓ allowlisted normalized state
Digital Twin browser
```

The browser must not query `/api/states`, `/api/services`, `/api/events`, WebSocket, File editor, Studio Code Server, or configuration files directly. A future adapter may be added only after the meeting supplies an approved entity inventory, access policy, backend endpoint, authentication/security boundary, and verified circuit mapping.

## Meeting decisions still required

1. Exact A3/A4 entity inventory and domain for each device.
2. Which entities are read-only state, history, activity, camera, power, or other roles.
3. Availability/unknown semantics and stale threshold.
4. Allowed attributes and units for each entity.
5. Room and device access roles.
6. Backend endpoint, authentication, CORS/origin, rate limits, logging, and failure behavior.
7. Circuit mapping and breaker policy.
8. History/activity retention and permitted query range.
9. Physical mobile and platform acceptance are separate from this schema.

## Validation intent

Before replacing synthetic IDs, validate the fixture against both schemas, check duplicate `objectId`/`nodeName` values, check room ownership, and scan for credentials or real network endpoints. Do not promote `mock-only` to `approved` by editing a version string alone.

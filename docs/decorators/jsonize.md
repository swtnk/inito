# @Jsonize

Generate `to_dict()` and `to_json()` that serialize a class's declared fields to
**JSON-native** forms — coercing the types `json.dumps` can't handle on its own.

## The problem it solves

`json.dumps(obj)` raises on a plain object, and even `vars(obj)` fails once a
field holds a `datetime`, `UUID`, `Decimal`, `Enum`, or `bytes`. Hand-writing a
`to_dict` that walks every field and coerces those types is exactly the
boilerplate inito exists to remove. `@Jsonize` derives it from the class's
annotations, once.

## Usage

```python
import datetime
import uuid

from inito import Data, Jsonize


@Jsonize
@Data
class Event:
    id: uuid.UUID
    when: datetime.datetime
    name: str = ""


event = Event(uuid.uuid4(), datetime.datetime.now(datetime.timezone.utc), "launch")

event.to_dict()   # {"id": "…", "when": "2026-07-13T05:30:00+00:00", "name": "launch"}
event.to_json()   # '{"id": "…", "when": "…", "name": "launch"}'
event.to_json(indent=2, sort_keys=True)   # kwargs are forwarded to json.dumps
```

## What it generates

- **`to_dict(self) -> dict[str, Any]`** — every declared field, each value coerced
  to a JSON-native form (see the table). The field → key mapping is fixed at
  decoration time; only the per-value coercion runs at call time (a field's
  runtime value type isn't knowable earlier).
- **`to_json(self, **kwargs) -> str`** — `json.dumps(self.to_dict(), **kwargs)`;
  any keyword arguments (`indent`, `sort_keys`, …) pass straight through.

## Type coercions

| Value type | Serialized as |
|---|---|
| `str` / `int` / `float` / `bool` / `None` | unchanged |
| `datetime` / `date` / `time` | ISO 8601 string (`.isoformat()`) |
| `uuid.UUID` | string |
| `decimal.Decimal` | string (no precision loss) |
| `enum.Enum` | its `.value` (recursively) |
| `bytes` / `bytearray` | base64 string |
| `os.PathLike` (e.g. `pathlib.Path`) | string |
| mapping | `{str(key): serialized(value)}` |
| sequence / set | list of serialized items |
| object with `to_dict()` (e.g. nested `@Jsonize`) | that object's dict |
| anything else | `str(value)` |

Nest `@Jsonize` on your nested types so they serialize structurally; an
undecorated object falls back to `str(...)`.

## Type checking

The bundled [mypy plugin](../installation.md#type-checking-mypy) and
[`inito-stubgen`](../installation.md) both expose `to_dict`/`to_json`, so
`mypy --strict` and pyright see them with the right signatures.

## Use with FastAPI

A plain inito object isn't a Pydantic model, so return the serialized form from a
handler:

```python
@app.get("/events/{event_id}")
async def read_event(event_id: int) -> dict:
    return store.get(event_id).to_dict()
```

## Options

| Option | Default | Effect |
|---|---|---|
| _(none yet)_ | | `@Jsonize` and `@Jsonize()` are equivalent |

## See also

- [@Data](data.md) · [@Value](value.md)
- [API reference](../reference/index.md)

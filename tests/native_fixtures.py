import hashlib
import json
from pathlib import Path


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
        ).encode()
    ).hexdigest()


def synthetic_source(tmp_path, counts=(0, 1), responses=None):
    categories = (
        "input_tokens",
        "cached_input_tokens",
        "cache_write_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
        "total_tokens",
    )
    rows = [
        {
            "type": "session_meta",
            "payload": {
                "id": "PRIVATE-thread",
                "session_id": "PRIVATE-session",
                "parent_thread_id": "PRIVATE-parent",
                "prompt": "PRIVATE-PROMPT",
            },
        }
    ]
    facts = []
    for index, quantity in enumerate(counts):
        payload = dict(
            thread_id="PRIVATE-thread",
            turn_id="PRIVATE-turn",
            session_id="PRIVATE-session",
            root_turn_id="PRIVATE-root",
            response_id=responses[index] if responses else f"PRIVATE-response-{index}",
            usage=dict.fromkeys(categories, quantity),
            turn_token_usage={},
            thread_token_usage={},
        )
        rows.append({"type": "token_usage_record", "payload": payload})
        event = digest(
            [
                "codex-request-event-v1",
                "Codex",
                "desktop-coding",
                payload["thread_id"],
                payload["response_id"],
            ]
        )
        lineage = {
            name: digest(["codex-source-id-v1", kind, raw])
            for name, kind, raw in (
                ("thread", "thread", payload["thread_id"]),
                ("turn", "turn", payload["turn_id"]),
                ("session", "session", payload["session_id"]),
                ("root_turn", "turn", payload["root_turn_id"]),
                ("header_parent_thread", "thread", "PRIVATE-parent"),
            )
        }
        for category in categories:
            facts.append(
                dict(
                    fact_key=digest(["codex-request-fact-v1", event, "request", category]),
                    event_key=event,
                    mapping_revision="codex-request-observation-r1",
                    category=category,
                    scope="request",
                    quantity=quantity,
                    quantity_basis="serialized_source",
                    backend_presence="unknown",
                    producer={
                        "engine_version": "0.163.0-alpha.10.2",
                        "client_surface": "desktop-coding",
                        "client_build": None,
                    },
                    source_lineage=lineage,
                    request_interval="unknown",
                    model=None,
                    model_version=None,
                    coverage="partial_observed_subset",
                    completeness="unknown",
                    finality="unknown",
                )
            )
    raw = b"".join(json.dumps(row).encode() + b"\n" for row in rows)
    path = tmp_path / "PRIVATE-source.jsonl"
    path.write_bytes(raw)
    canonical = json.loads(
        (Path(__file__).parents[1] / "docs/providers/source-profiles.json").read_text()
    )["profiles"][-1]
    admission = canonical["admission"]
    admission.update(
        source_sha256=hashlib.sha256(raw).hexdigest(),
        accepted_records=[1, 2],
        expected_request_count=2,
        expected_fact_count=12,
        whole_record_count=3,
        projection_sha256=digest(sorted(facts, key=lambda fact: fact["fact_key"])),
    )
    admission["classification"].update(
        records=3,
        accepted_records=[1, 2],
        outer_record_counts={"session_meta": 1, "token_usage_record": 2},
        event_payload_type_counts={},
    )
    envelope = dict(
        profile_id="synthetic-only",
        profile_digest="b" * 64,
        approval_digest="c" * 64,
        admission=admission,
    )
    return path, raw, envelope

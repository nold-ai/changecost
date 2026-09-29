"""Pre-call plain payload expectations; finite fixture IDs, no production imports."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

STORE_ID = "scenario-store"
CHANGE_ID = "5d4bcc633187488018c41572c3f853956b4ca0c2a534bb25f5e1f8e9220129d5"
# Literal fixture identities for synthetic/c and cursor/ide/r0..r2. These are
# reviewed finite fixtures, not calls to the implementation's stable_id helper.
RUN_IDS = {
    "r0": "cc841021f70ba241ce6df6587ca0c5cc27fdcb9b4f006da2dc6e8ac2a8316d80",
    "r1": "43fef61f3186cdba95dc0ed842a98118ecdc7a23456701025a3ebcc8fb911a1a",
    "r2": "139761fcbb220d8bdd259e8ba21249b5d18bf5eb43a1fff83bfed403055beb6c",
}
BINDING_IDS = {
    "r0": "229a5dc11dd46c9c65d6a74d736518e66eb44f9f71fce51670873d706e735fb3",
    "r1": "7a57a8d2d9896ded36c71bdab7e703b9a2b3e758d98e5dc2c2ae177bf6118e9a",
    "r2": "5708421b205954c11b3e066dbd3302e29910ce95175051d98b6ea1f8c0297dbf",
}


def allocation(step, ordinal):
    return f"step-{step}-allocation-{ordinal}"


def run_identity(name):
    return dict(repository_id="synthetic", provider="cursor", surface="ide", run_id=name)


def reference(kind, ident):
    return dict(kind=kind, record_id=ident)


@dataclass
class ExpectedPayloads:
    clock: datetime
    records: list = field(default_factory=list)
    previous: dict = field(default_factory=dict)
    step: int = 0
    ordinal: int = 0

    def timestamp(self, minutes=0):
        return (
            None
            if minutes is None
            else (self.clock + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")
        )

    def add(self, kind, ident=None, **fields):
        if ident is None:
            ident = allocation(self.step, self.ordinal)
            self.ordinal += 1
        self.records.append(
            dict(
                schema="changecost/v1",
                kind=kind,
                record_id=ident,
                origin_store_id=STORE_ID,
                recorded_at=self.timestamp(),
                effective_at=self.timestamp(),
                **fields,
            )
        )
        return reference(kind, ident)

    def advance(self, before, after, action, step):
        self.step, self.ordinal = step, 0
        if before.feature is None and after.feature is not None:
            self.add(
                "change",
                CHANGE_ID,
                repository_id="synthetic",
                change_id="c",
                features=dict(
                    version="features/v1",
                    captured_at=self.timestamp(),
                    recorded_at=self.timestamp(),
                    change_shape=after.feature,
                    trajectory=None,
                    execution_profile=None,
                ),
                commit_ref=None,
                pr_ref=None,
            )
        for name in after.runs.keys() - before.runs.keys():
            self.add(
                "run",
                RUN_IDS[name],
                ref=run_identity(name),
                observed_start=self.timestamp(after.runs[name]),
                provider_session_id=None,
                trace_id=None,
            )
            self.add(
                "run_binding",
                BINDING_IDS[name],
                run=run_identity(name),
                change=reference("change", CHANGE_ID),
                method="manual",
                source_refs=[],
            )
        self.outcomes(before, after, action)
        self.intervals(before, after, action)

    def outcomes(self, before, after, action):
        for name, history in after.outcomes.items():
            prior = before.outcomes.get(name, [])
            if len(history) == len(prior):
                continue
            subject = (
                reference("change", CHANGE_ID) if name == "c" else reference("run", RUN_IDS[name])
            )
            key = "outcome", name
            self.previous[key] = self.add(
                "outcome",
                subject=subject,
                outcome=history[-1],
                previous=self.previous.get(key),
                reason=action.reason if prior else None,
            )

    def intervals(self, before, after, action):
        for name, history in after.intervals.items():
            prior = before.intervals.get(name, [])
            if len(history) == len(prior):
                continue
            start, end = history[-1]
            changed = bool(prior) and any(
                old is not None and old != new
                for old, new in zip(prior[-1], history[-1], strict=True)
            )
            key = "interval", name
            self.previous[key] = self.add(
                "interval",
                run=run_identity(name),
                start=self.timestamp(start),
                end=self.timestamp(end),
                previous=self.previous.get(key),
                reason=action.reason if changed else None,
                method="manual",
                source_refs=[],
            )

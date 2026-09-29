"""Small scenario oracle: no imports from production code or its decision helpers."""

from copy import deepcopy
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Action:
    kind: str
    target: str = "r0"
    value: str | None = None
    start: int | None = None
    end: int | None = None
    correction: bool = False
    reason: str = ""
    naive: bool = False


@dataclass
class Model:
    feature: str | None = None
    runs: dict[str, int | None] = field(default_factory=dict)
    outcomes: dict[str, list[str]] = field(default_factory=dict)
    intervals: dict[str, list[tuple[int | None, int | None]]] = field(default_factory=dict)

    def attempt(self, action: Action) -> bool:
        candidate = deepcopy(self)
        try:
            candidate.apply(action)
        except ValueError:
            return False
        self.__dict__.update(candidate.__dict__)
        return True

    def apply(self, action: Action) -> None:
        if action.naive:
            raise ValueError("aware timestamps required")
        if action.kind == "change":
            feature = action.value or "bugfix"
            if self.feature is not None and self.feature != feature:
                raise ValueError("immutable features")
            self.feature = feature
        elif action.kind == "run":
            self.register_run(action)
        else:
            self.declare(action)

    def register_run(self, action: Action) -> None:
        if self.feature is None:
            raise ValueError("unknown Change")
        if action.target in self.runs:
            if self.runs[action.target] != action.start:
                raise ValueError("immutable start")
            return
        if self.outcomes.get("c"):
            raise ValueError("terminal Change")
        self.runs[action.target] = action.start
        if action.start is not None:
            self.intervals[action.target] = [(action.start, None)]

    def declare(self, action: Action) -> None:
        if (action.target == "c" and self.feature is None) or (
            action.target != "c" and action.target not in self.runs
        ):
            raise ValueError("unknown target")
        if action.value is None and action.start is None and action.end is None:
            raise ValueError("no declaration")
        if action.value is not None:
            allowed = (
                {"accepted", "abandoned"}
                if action.target == "c"
                else {"succeeded", "failed", "cancelled"}
            )
            if action.value not in allowed:
                raise ValueError("outcome domain")
            history = self.outcomes.setdefault(action.target, [])
            if not history or history[-1] != action.value:
                self.require_correction(bool(history), action)
                history.append(action.value)
        if action.start is not None or action.end is not None:
            self.interval(action)

    def interval(self, action: Action) -> None:
        if action.target == "c":
            raise ValueError("interval requires Run")
        history = self.intervals.setdefault(action.target, [])
        before = history[-1] if history else (None, None)
        after = (
            action.start if action.start is not None else before[0],
            action.end if action.end is not None else before[1],
        )
        if after[0] is not None and after[1] is not None and after[1] < after[0]:
            raise ValueError("negative interval")
        changed = any(
            old is not None and old != new for old, new in zip(before, after, strict=True)
        )
        self.require_correction(changed, action)
        if not history or after != before:
            history.append(after)

    @staticmethod
    def require_correction(needed: bool, action: Action) -> None:
        if needed and not (action.correction and action.reason.strip()):
            raise ValueError("reasoned correction required")

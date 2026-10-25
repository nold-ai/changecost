"""Run a deterministic manual-session journey through the actual CLI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def walkthrough(directory: Path) -> dict:
    """Reserve a fresh directory and retain every real CLI input and result."""
    directory.mkdir(parents=True, exist_ok=False)
    database = directory / "sessions.sqlite3"
    core = directory / "unused-core.sqlite3"
    steps = []

    def invoke(*arguments: str) -> dict:
        command = [
            sys.executable,
            "-m",
            "changecost",
            "--db",
            str(core),
            "session",
            "--session-db",
            str(database),
            *arguments,
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=True)
        result = json.loads(completed.stdout)
        steps.append(dict(arguments=list(arguments), result=result))
        return result

    observed = []
    for name, actual in (("one", 200), ("two", 200), ("three", 1000)):
        arguments = ["start", name, "--task-kind", "feature", "--context", "demo/python-cli"]
        if name == "one":
            arguments.extend(["--guess", "100"])
        invoke(*arguments)
        result = invoke("finish", name, "--tokens", str(actual), "--outcome", "completed")
        observed.append(
            dict(
                session_id=name,
                forecast=result["forecast"]["amount"],
                actual=actual,
                signed_error=result["error"]["signed_tokens"],
                absolute_error=result["error"]["absolute_tokens"],
            )
        )
    fourth = invoke("start", "four", "--task-kind", "feature", "--context", "demo/python-cli")
    history = invoke("history", "--task-kind", "feature", "--context", "demo/python-cli")
    transcript = dict(
        observed=observed,
        fourth_forecast=fourth["forecast"],
        evaluation=history["evaluation"],
        steps=steps,
    )
    with (directory / "transcript.json").open("x") as destination:
        json.dump(transcript, destination, indent=2)
        destination.write("\n")
    return transcript


def main() -> None:
    parser = argparse.ArgumentParser(description="Manual session demo in a NEW isolated directory.")
    parser.add_argument(
        "directory", type=Path, help="Must not already exist; never uses real history."
    )
    arguments = parser.parse_args()
    try:
        result = walkthrough(arguments.directory)
    except FileExistsError:
        parser.exit(2, "Choose a new demo directory. Existing contents were preserved.\n")
    except (OSError, subprocess.CalledProcessError):
        parser.exit(
            2, "Demo could not complete. Retain its directory and inspect the CLI separately.\n"
        )
    print("Manual, provisional, uncalibrated. Unit: total_tokens.")
    print("session  forecast  actual  signed_error  absolute_error")
    for row in result["observed"]:
        print(
            f"{row['session_id']:7}  {row['forecast']:>8}  {row['actual']:>6}  "
            f"{row['signed_error']:>12}  {row['absolute_error']:>14}"
        )
    fourth = result["fourth_forecast"]
    print(f"Next forecast: {fourth['amount']} tokens from {fourth['sample_count']} samples.")
    mae = result["evaluation"]["mean_absolute_error"]
    print(
        f"Cumulative MAE: {mae['numerator']}/{mae['denominator']} = "
        f"{mae['rounded_decimal']} tokens. One pending session is excluded."
    )
    print("Errors improved, then worsened. This example makes no accuracy promise.")
    print("The separate database and transcript.json are in the new demo directory.")


if __name__ == "__main__":
    main()

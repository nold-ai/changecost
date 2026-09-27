# Non-negotiable checklist

- Respect the explicit phase: pilot planning is authorized; product implementation
  and live collection need a subsequent request. Research is not additional scope.
- Inspect existing changes and preserve work belonging to others.
- Use focused branches for normal changes. A branch in the existing checkout
  is enough when there is no concurrent work to isolate.
- Keep the repository private until the maintainer explicitly authorizes otherwise.
- Never commit secrets, actual billing exports, prompts, or identifiable bindings.
  Keep local runtime/review output in `.changecost/` and `.specfact/` respectively.
- For product behavior, derive tests from specs, observe the expected failure,
  implement, then record the passing result. No fabricated test evidence.
- Run applicable quality checks; resolve review findings or document an explicit,
  justified exception. An unavailable analyzer is incomplete evidence.
- Do not introduce SpecFact as a runtime dependency or copy its release machinery.
- Explain material limitations, relevant risks, and rollback in the final handoff.

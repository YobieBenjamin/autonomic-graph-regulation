# Instructions for AI coding agents

*Read this before changing anything. It applies to every AI agent (Claude, Codex, or any other) working in this
repository, on any machine.*

1. **The goal.** Read `GOAL.md` (https://github.com/YobieBenjamin/hardware-and-silicon/blob/main/goals/GOAL.md).
   Every change is judged by whether it brings a chip that stops bad actions from AI, provably, closer to existing.
2. **Branches.** `main` is protected. Never push, force-push or merge to `main`, never delete it, and never change
   repository settings, rulesets or required checks. Work on your own branch (`fix/`, `exp/`, `docs/`, `audit/`); you
   may create, change, rebase, force-push and delete working branches as needed. A person merges into `main` through a
   pull request. Full rule: `BRANCHES.md`.
3. **Never merge, even if you can.** GitHub cannot tell a person from an AI agent using that person's login, so
   nothing technical stops you from merging a pull request with credentials that allow it. You still must not: do not
   merge or approve pull requests into `main`, do not use the owner's personal token or login for anything a person is
   meant to decide, and use only the narrowly scoped credentials you were given for your task. If the only credentials
   available would let you merge, stop and say so instead of using them. Report what you did; a person merges.
4. **Open audit findings stay private.** Never push an open audit's report, catalog or failing attack tests to a
   public repository, branch, pull request, issue or comment. A round is published only when its fixes are merged
   (`DISCLOSURE.md`).
5. **Source of truth.** GitHub, account `YobieBenjamin`. Clones on the Mac mini, the MacBook Pro or in a cloud session
   follow it. Branch from a freshly fetched `origin/main`.
6. **Evidence.** Never rewrite dated, hash-pinned records under `archive/` or `audit/`.
7. **Fix pipeline.** Every problem gets a failing test first, then the fix, then the full suites
   (`PROBLEM-TO-SILICON-PIPELINE.md`). Never weaken a test or a formal property to make it pass.
8. **Writing.** Plain English; descriptive comments in code saying what and why; no em dashes or en dashes; names that
   a future developer can read (`LABELS.md` where it exists). Do not invent new naming schemes or prefixes.
9. **No AI is the final judge.** Your results are evidence for a person to check, not a verdict.

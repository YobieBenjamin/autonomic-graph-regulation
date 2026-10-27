# Branches: who may change what

*Applies to all six repositories at https://github.com/YobieBenjamin (safety-governor, hardware-and-silicon, Watermark,
chip-that-says-no-discussion, safety, autonomic-graph-regulation), to every person and every AI coding agent that
works on them, on every machine (the Mac mini, the MacBook Pro, and any cloud session). Decided by Yobie Benjamin,
26 October 2026.*

## The rule

**`main` is protected. Everything else is a working branch.**

- `main` is the source of truth (GOAL.md). It changes only through a pull request that a person approves and merges.
  No AI agent merges into `main`, pushes to `main`, force-pushes `main`, or deletes it. This is GOAL.md's rule "no AI
  is the final judge" applied to the code itself: the AI that builds the work does not decide what becomes the truth.
- **AI agents may create, change, rebase, force-push and delete working branches as needed.** That is how they work:
  a fix round, an experiment or an audit response lives on its own branch until a person merges it.
- An AI agent never weakens the protection: it does not change repository settings, rulesets, required checks or
  permissions, and does not ask for a bypass.

## Settings on GitHub (each repository, branch `main`)

Applied by the owner with one command on the Mac mini, `work/launch/protect/protect_main.sh` (launcher
`protect_main.terminal`), signed in to GitHub as `YobieBenjamin`. It creates or updates a repository ruleset named
"Protect main" on the default branch of all six repositories and reads it back:

1. **No deletion** of `main`.
2. **No force push** to `main`.
3. **Pull request required.** Every change reaches `main` through a pull request. Required approvals: 0 for now,
   because GitHub does not let an owner approve their own pull request, so with one person a required approval would
   lock everyone out. The person who merges is the approval. Raise it to 1 when a second person joins.
4. **CI must pass** where the repository has CI (safety-governor, safety, autonomic-graph-regulation), with the branch
   up to date with `main`. The script requires exactly the checks that have run on `main`.
5. **No bypass list.** Nobody, administrators included, skips the ruleset.

Working branches are not protected: people and the AI agents they allow may create, push, force-push and delete them.

## Development rule: only a person merges, whatever the credentials allow

GitHub cannot tell a person from an AI agent using that person's credentials. An agent holding a token that can write to
a repository could technically merge a pull request into `main`. So this is a standing rule for every developer, agent
and model, on every machine:

1. **No AI agent or model merges or approves a pull request into `main`,** even when its credentials would let it. It
   pushes its branch, opens the pull request, reports the evidence, and stops. A person merges.
2. **Agents get their own narrowly scoped credentials** (for example a fine-grained token limited to the repositories
   and permissions the task needs), never the owner's personal login or token for anything a person is meant to decide.
3. **An agent that finds it holds credentials able to merge, change settings or bypass protection does not use them for
   that,** and says so in its report.
4. **People check.** Every merge into `main` is reviewed by the person merging; a merge made by an agent is reverted
   and reported.
5. **Developers who run agents** give each agent this file and `AGENTS.md` (Claude Code reads them through
   `CLAUDE.md`; other agents are pointed at `AGENTS.md` in their instructions).

## Branch names

Plain names that say what the branch is for, so a developer can read them:

| Prefix | Used for | Example |
|---|---|---|
| `fix/` | a fix round or one fix | `fix/adversarial-audit-3` |
| `exp/` | an experiment | `exp/observer-evaluation-set` |
| `docs/` | documents only | `docs/goal-claim` |
| `audit/` | an audit's own records (read-only work) | `audit/openai-2026-10` |

Existing branches keep their names.

## How work reaches `main`

1. Work on a branch, on any machine. Push the branch to GitHub. Commit as the person or agent that did the work, with
   the agent named in a `Co-Authored-By` line.
2. Before opening a pull request, the branch passes the same checks the merge requires, run locally (each repository's
   tests; in safety-governor also `python -m govsim.redteam`, `python -m rtl.conformance` and `python -m rtl.formal`).
3. Open a pull request into `main` with a description of what changed and the evidence (test counts, verdicts, the
   response document for an audit round).
4. A person reviews, approves and merges. Merge, do not squash, when the branch history is evidence an audit relies on.
5. After the merge, every clone pulls `main` (`git switch main && git pull --ff-only`). The Mac mini clones under
   `/Volumes/External_4TB/Safety Experiments/work/<repository>` and the MacBook Pro clones follow GitHub; they never
   become a second source of truth.

## Several machines, several agents

- One branch, one writer at a time. If two machines or agents must work on the same change, each takes its own branch
  and one merges into the other by pull request or rebase on the branch, never on `main`.
- Before starting, fetch (`git fetch origin`) and branch from the current `origin/main`.
- A clone whose `origin` is not its repository at `https://github.com/YobieBenjamin/<repository>.git` is misconfigured
  and is fixed before any work (the Mac install scripts check this).
- Evidence that is dated and hash-pinned (under `archive/` and `audit/`) is never rewritten, on any branch.

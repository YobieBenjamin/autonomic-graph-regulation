# Disclosure: when audit findings become public

*Applies to all six repositories at https://github.com/YobieBenjamin and to every person, AI agent and model working
on them. Decided by Yobie Benjamin, 26 October 2026.*

The governor is a safeguard against attackers, so a list of its open weaknesses is an attack plan. This project follows
standard responsible disclosure:

1. **Open findings stay private.** An audit's report, its problem catalog, its failing attack tests and its scripts are
   kept off the public repositories while the round is open: on the project owner's drive
   (`/Volumes/External_4TB/Safety Experiments/work/audits/`) and in the owner's private claude.ai Project. They are never
   pushed to a public repository, a public branch, a pull request description, an issue or a public comment.
2. **A round closes when its fixes are merged into `main`.** That is: every finding is fixed (with its failing test
   now passing), or written down as open with the reason, in the round's response document
   (for example `safety-governor/docs/28-adversarial-audit-3-response.md`).
3. **Then the round is published.** The auditor's report and catalog are added, unedited, beside the response document
   in the same pull request or the next one, so the public record shows what was found, how it was fixed, and what is
   still open.
4. **Findings that are still open when a round closes** are described in the response document at the level a reader
   needs to judge the claim (what is not yet covered, and why), without the step-by-step attack.
5. **Outside auditors** (OpenAI's included) receive the public repositories plus, if they need it, read access to the
   private audit material, and agree to the same rule: nothing about an open finding is published until the round
   closes.

AI agents: before you push a branch or open a pull request, check that it carries no open audit material (reports,
catalogs, failing attack tests from an audit that is not yet closed). If it does, stop and say so.

The work carries distinctive markers that identify copies of it. They are documentation and naming only: none of them
changes what the governor, its proofs or its tests do.

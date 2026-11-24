# grill-my-paper: help

A panel of reviewer agents with different jobs reads your paper independently, argues over the
disputed points, and an editor writes a verdict and a revision plan for your target journal.

## Commands

| Type this | What happens |
|---|---|
| `/grill-my-paper <paper.pdf or .tex>` | Review at the default depth. Asks the target journal and confirms the panel before starting. |
| `/grill-my-paper <paper> depth=quick` | Pick a depth: `quick`, `standard`, `full`, or `desk` (table below). |
| `/grill-my-paper <paper> target=RFS` | Set the target journal. |
| `/grill-my-paper <paper> reviewers: skeptic, champion, lit: corporate bond liquidity, auditor` | Choose the seats yourself. |
| `/grill-my-paper <paper> add: a behavioral finance referee who thinks it is all sentiment` | Add any reviewer you can describe. A new persona is written for it, and you can save it afterwards. |
| `/grill-my-paper <revised paper> rerun` | After revising: same panel, checks which earlier issues are resolved. |
| `/grill-my-paper tune the skeptic was too generic on identification` | Improve a reviewer from what you liked or disliked in a past run. |
| `/grill-my-paper personas` | List the reviewer types and how often each has been seated. |
| `/grill-my-paper save <name>` | Save a reviewer invented during a run to the library. |
| `/grill-my-paper help` | This page. |

Arguments are free text; the forms above are examples, not strict syntax. They can be combined.

## Depths

| Depth | Who sits | Debate round | Use it when |
|---|---|---|---|
| `quick` | editor-desk, skeptic, champion | No | First look, or a cheap check after small changes |
| `standard` | quick + one literature specialist + identification or mechanism | Yes | The normal pre-submission review |
| `full` | standard + second literature specialist, outsider, auditor, institutional if relevant | Yes | Final check before submitting |
| `desk` | editor-desk (one per target journal), outsider | No | Testing the title, abstract and introduction, or choosing between journals |

Cost grows with seats and rounds: every reviewer reads the whole paper, and reads it again in the
debate round.

## What you get

A folder next to the paper, `grill_<paper-name>_<date>/`:

- `PANEL_REPORT.md`: bottom line, votes, the surviving rejection and acceptance cases, rulings on each
  disputed issue, and a revision plan ordered by payoff (including what to ignore).
- `round1/`, `round2/`: each reviewer's own report and debate answers.
- `ledger.md`: every issue raised and who raised it.

## Good to know

- Start a session in the paper's folder so the run folder can be written there.
- Citations to other papers are tagged verified or unverified. Check the unverified ones by hand.
- The panel is a stress test, not a forecast of what real referees will say.
- Defaults (field, target journals, depth, seats to always include) live in `profile.md`. Say
  "default to RFS" or "always seat the auditor" to change them.

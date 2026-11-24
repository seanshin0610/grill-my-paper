# grill-my-paper: help

A panel of reviewer agents with different jobs reads your paper independently, argues over the
disputed points, and an editor writes a verdict and a revision plan for your target journal.

## Commands

| Type this | What happens |
|---|---|
| `/grill-my-paper <paper.pdf or .tex>` | Review at the default depth. Asks the target journal and confirms the panel before starting. |
| `/grill-my-paper <paper> depth=quick` | Pick a depth: `quick`, `standard`, `full`, or `desk` (table below). |
| `/grill-my-paper <paper> target=RFS` | Set the target journal. |
| `/grill-my-paper <paper> model=opus` | Run the reviewers on a model other than the session's. The editor's part (casting, rulings, the report) stays on the session's model. |
| `/grill-my-paper <paper> also=online_appendix.pdf` | Give reviewers another file, such as an appendix. For a TeX paper the appendix, figures, and bibliography it points to are found automatically. |
| `/grill-my-paper <paper> reviewers: skeptic, champion, lit: corporate bond liquidity, auditor` | Choose the seats yourself. |
| `/grill-my-paper <paper> add: a behavioral finance referee who thinks it is all sentiment` | Add any reviewer you can describe. A new persona is written for it, and you can save it afterwards. |
| `/grill-my-paper <revised paper> rerun` | After revising: same panel, checks which earlier issues are resolved. |
| `/grill-my-paper tune the skeptic was too generic on identification` | Improve a reviewer from what you liked or disliked in a past run. |
| `/grill-my-paper personas` | List the reviewer types. |
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

- `PANEL_REPORT.pdf`: bottom line, votes, the surviving rejection and acceptance cases, rulings on each
  disputed issue, and a revision plan ordered by payoff (including what to ignore). The same report
  is there as `PANEL_REPORT.md`, which is the source the PDF is made from.
- `round1/`, `round2/`: each reviewer's own report and debate answers.
- `ledger.md`: every issue raised and who raised it.
- `citation_check.md`: whether the papers reviewers cited exist and say what was claimed. Covers the
  ones cited from memory and the ones the report's rulings rely on.

## Good to know

- Your paper is never changed. The skill reads your files and writes only into the run folder. It
  edits the paper only if you ask for an edit after the review.
- Start a session in the paper's folder so the run folder can be written there.
- If the paper is in a git repository, such as an Overleaf project shared with coauthors, the run
  folder is added to that repository's local exclude list (`.git/info/exclude`). It cannot be
  committed or pushed by accident, and coauthors see no change.
- PDF papers are cited by page. TeX papers have no pages, so the report cites sections, labels, and
  line numbers, and those are the line numbers of your own .tex file.
- Reviewers tag each citation to another paper as verified or from memory. A separate Sonnet agent
  then looks up the ones from memory, and the ones the report's rulings rely on, and reports which
  exist and say what the reviewer claimed. It never sees your paper. Whatever it could not confirm is listed as such in the report.
- The panel is a stress test, not a forecast of what real referees will say.
- The skill keeps no record of your runs and never edits itself during a review. Reviewers and
  defaults change only when you ask: `tune ...`, `save ...`, or "default to RFS".

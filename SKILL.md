---
name: grill-my-paper
description: >
  Convene a simulated review panel for an academic paper draft (PDF or TeX). Independent reviewer
  agents with different mandates (rejecting referee, champion, literature specialists, identification
  referee, editor's first read, and others) each review the paper, cross-examine one another's
  points, and a handling editor rules on the disputes and writes a verdict plus a prioritized
  revision plan for the target journal. Tunes or saves reviewer personas only when the user asks.
  Trigger on "grill-my-paper", "grill my paper", "review panel", "have agents debate my paper",
  "stress-test my paper before submission", or "tune the skeptic / a reviewer".
argument-hint: "<paper.pdf|.tex> [target=RFS] [depth=quick|standard|full] [also=appendix.pdf] [reviewers: ...]  |  tune <feedback>  |  personas  |  help"
disable-model-invocation: true
---

# Grill My Paper

Run a paper through a panel of reviewers who disagree on purpose, then act as the handling editor who
decides what the author should do about it. The goal is not a pile of referee reports. It is a short
list of the changes most likely to move this draft toward publication in the target journal.

A panel beats a single reviewer for four reasons, and each step below exists to protect one of them:

1. **Independence.** Reviewers who have not seen each other's views make different mistakes. Two
   independent reviewers raising the same issue is strong evidence; one reviewer echoing another is none.
2. **Different mandates, not different moods.** A reviewer told to find the fastest route to rejection
   reads differently from one told to find the best version of the paper. "Be harsh" and "be nice"
   change tone; a mandate changes what gets found.
3. **A real fight on contested points.** When the skeptic calls something fatal and the champion calls
   it the paper's strength, making them answer each other with evidence from the paper is where the
   author learns the most.
4. **An editor who rules.** Averaging six reports gives a laundry list. The synthesis decides which
   points matter, which to ignore, and in what order to act.

## Modes

Route on the user's arguments (free text; no strict syntax):

| The user gives | Do |
|---|---|
| A paper path (optionally target, depth, reviewer list) | **Review**: the workflow below |
| A paper path plus an earlier run folder, or "re-run" | **Re-run after revision**: see the section near the end |
| `tune ...`, or an explicit request to change how a reviewer or the skill works | Read `references/tuning.md` and follow it |
| `personas`, `save <name>`, "add a reviewer type" | Read `references/tuning.md`, section "Managing the library" |
| `help`, `?`, no arguments, or a question about how to use the skill | **Help**: see below |

### The skill does not change itself

A review reads this folder and writes only to the run folder. Do not log runs, count usage, or edit
any file in this folder as a side effect of doing a review. Files here change only when the user
explicitly asks: `tune`, `save`, or a request to change a default. This is the user's tool, and they
decide what it becomes; a tool that keeps records of their papers or quietly rewrites its own
instructions is doing something they did not ask for.

A reaction to a reviewer's output ("the skeptic was generic") is conversation, not a request to edit
a persona. Respond to it as part of discussing the paper. You may mention once that `tune` would make
the change permanent, and then leave it to them.

### Help

Show `references/help.md` to the user as written. Then add two things that the static page cannot
know, because the user may have changed them:

- **Reviewer types available now**: a table built from the frontmatter of every file in `personas/`
  (skip `_TEMPLATE.md`) with columns id, lens, when to use, and parameters.
- **Current defaults** from `profile.md` if it exists, otherwise `profile.default.md`: target
  journals, default depth, standing preferences.

Help reads only those small files. Do not read a paper or launch any reviewer for it, and do not ask
the user for a paper path; end by pointing at the first command they are most likely to want.

## What is in this skill

All paths are relative to this skill's base directory (shown when the skill loads).

| Path | What it is |
|---|---|
| `profile.default.md` | The defaults shipped with the skill: field, target journals, default depth |
| `profile.md` | The user's own defaults. Exists only once the user has asked to change one; it then replaces `profile.default.md`. Git ignores it. |
| `personas/*.md` | The reviewer library. One file per reviewer type. This is what tuning edits. |
| `personas/_TEMPLATE.md` | How to write a new reviewer type |
| `references/reviewer-brief.md` | Ground rules and report format shared by every reviewer |
| `references/cross-exam.md` | Round 2 protocol |
| `references/synthesis-template.md` | Structure of the final panel report |
| `references/tuning.md` | Changing a persona when the user asks; saving and listing personas |
| `references/help.md` | The help page shown for `help` or no arguments. Keep it in step when commands or depths change. |
| `scripts/extract_paper.py` | Creates the run folder; extracts the paper to text; gathers the appendix, figures, and bibliography; keeps the run folder out of a surrounding git repository |
## Review workflow

### Step 1. Set up the run and read the paper

Run the extractor. It creates a run folder next to the paper and gathers the paper's materials there:

```bash
python "<skill-dir>/scripts/extract_paper.py" "<path-to-paper>" [--also "<file>" ...]
```

Use `python3` where `python` is not available. The script needs one PDF library (`pip install
pymupdf`). It prints a JSON summary. Read it, because the assignments in Step 3 are built from it:

- **`anchor`** says how reviewers cite locations. A PDF gives `pages`: `paper.txt` has
  `===== Page N =====` markers that match the PDF. A TeX source gives `lines`: there are no pages, so
  reviewers cite sections, labels, and line numbers of `paper.txt`.
- **`companions`**, **`figures`**, **`bibliography`**: for a TeX source the script follows
  `\externaldocument` (the online appendix, flattened to its own text file, with the label prefix the
  paper uses for it), `\includegraphics` (figure files copied to `figures/`, each with its labels), and
  `\bibliography` (the .bib file). Reviewers need these: a short paper keeps most of its support in
  the appendix, and a reviewer who cannot see it will report things as missing that are there.
- **`--also`** adds anything the script cannot detect: pass every file the user names (`also=...`),
  and for a PDF source ask yourself whether an appendix exists as a separate file. If the user
  mentioned one or the paper refers to an "Online Appendix" that is not in the PDF, ask for it.
- **`missing`** and **`warnings`**: files the source points to that were not found, or a PDF that
  looks scanned (reviewers must then read the PDF pages directly; say so in their assignments).
- **`git_exclude`**: if the paper sits in a git repository, such as an Overleaf project shared with
  coauthors, the script adds `grill_*/` to that repository's `.git/info/exclude`. That file exists
  only on this machine, so the run folder cannot be committed or pushed by accident and coauthors see
  no change. When `added` is true, tell the user in one line that this was done. If the summary says
  the run folder is inside a repository and not excluded, warn the user.

If the paper's folder is not writable from this session, or the user wants the output elsewhere, pass
`--run-dir <folder>`.

Read the defaults from `profile.md` if it exists, otherwise from `profile.default.md`. Then read the
whole paper yourself, and the parts of the appendix that carry the evidence (the
measurement procedure, the robustness tables). You are the handling editor: you cannot cast the right
panel, or later rule on a dispute between two reviewers, for a paper you have only skimmed.

### Step 2. Cast the panel

From your reading, write down (this goes into `00_panel.md` in the run folder):

- **Paper type**: empirical, theory, structural, or mixed.
- **Claimed contribution** in one sentence, in the paper's own terms.
- **Literatures it speaks to**, named the way an insider would name them ("corporate bond mutual fund
  fragility", not "asset management"). Usually two or three. These determine who would referee it.
- **Design**: the source of identifying variation, or the model's key mechanism.
- **Setting**: any market or institution whose details matter.

List the available reviewer types by searching `personas/` for the frontmatter lines
(`^(id|lens|use_when|parameters|reads):`), skipping `_TEMPLATE.md`. The library changes as the user
tunes and adds personas, so look rather than rely on the table below.

**Presets** (use the user's choice, else the profile's default depth):

| Depth | Roster | Rounds |
|---|---|---|
| `quick` | editor-desk, skeptic, champion | Round 1 only |
| `standard` | editor-desk, skeptic, champion, literature-specialist (primary literature), identification *or* mechanism | Round 1 + cross-examination |
| `full` | standard + a second literature-specialist, outsider, auditor, and institutional if the setting warrants | Round 1 + cross-examination |
| `desk` | editor-desk (once per target journal), outsider | Round 1 only |

**Casting principles:**

- Always seat both the skeptic and the champion. The fight needs two sides; either one alone gives a
  biased read.
- Seat one literature specialist per literature whose insiders would plausibly referee the paper. A
  paper that bridges two literatures is most often killed by the side that feels misdescribed, so cast
  both sides even at `standard` if the bridge is the contribution.
- Use `identification` for empirical papers and `mechanism` for theory. Seat both when an empirical
  paper's contribution is a claim about a channel.
- Stay at eight or fewer. Past that, reports repeat each other and the synthesis gets worse, not better.
- If the user asks for a reviewer type that is not in the library ("someone from behavioral finance
  who thinks it is all sentiment", "a regulator"), write a new persona for it following
  `personas/_TEMPLATE.md` and put the full persona text in that reviewer's assignment file. Offer to
  save it to the library at the end of the run.
- Honor explicit requests exactly: if the user names the reviewers or the number, that is the roster.

**Confirm once before launching**, unless the user already specified the roster or depth. A run is
expensive (every reviewer reads the full paper, and again in Round 2), and casting is the biggest
lever on quality. Show the roster as a table (reviewer, lens, why this paper needs them), state the
target journal you will use, and give the scale ("6 reviewers, 2 rounds"). Offer the adjacent
alternatives (quicker, fuller, custom). If the target journal is unknown and the profile lists
several, ask which one, since the bar and the audience differ.

### Step 3. Write each reviewer's assignment

A reviewer's prompt has three parts: the **persona** (saved, reusable), the **shared brief** (saved,
same for everyone), and the **assignment** (written by you, for this paper). Reviewers read the
persona and brief straight from the skill folder, so the tuned text is exactly what runs. You write
only the assignment, to `prompts/<reviewer-id>.md` in the run folder:

```markdown
# Assignment: <reviewer-id>

- **Persona:** <absolute path to personas/x.md>   (or "ad hoc, see below")
- **Parameters:** <e.g. literature = "corporate bond liquidity and dealer intermediation">
- **Target journal:** <journal, plus any format limits that are facts: word cap, exhibit cap, review process>
- **Paper text:** <run>/paper.txt
- **Appendix and other companions:** <each text file from the summary, with its label prefix if any>
- **Figures:** <run>/figures/   <list the main-text figures as file (label)>
- **Original PDF:** <path, when the source is a PDF>
- **Bibliography:** <run>/<file>.bib, for looking up citation keys
- **Write your report to:** <run>/round1/<reviewer-id>.md

## How to cite locations
<From the summary's `anchor`. For `pages`: "Cite page numbers; the page markers in paper.txt match
the PDF." For `lines`: "The source is LaTeX, so there are no page numbers. Cite a section, a figure
or table label, or a line number in paper.txt. Tables are inlined in the text; figures are separate
files, so open the file when a point depends on what a figure shows.">

## Where to point your lens
<3 to 6 sentences specific to this paper.>

## Persona (ad hoc reviewers only)
<full persona text written from _TEMPLATE.md>
```

Give each reviewer only the materials their persona may read. For `editor-desk`, state the exact
pages or line ranges of the title, abstract, introduction, and conclusion, name the one results
exhibit they may open, and leave the appendix out of the list; a reading restriction that is not
spelled out in pages or lines does not hold.

The tailoring paragraph is the part that needs judgment. Its job is to aim the reviewer, not to hand
them a conclusion. A reviewer handed a hypothesis tends to return it confirmed, which destroys the
independence the panel depends on.

- Good: "The paper claims to be the first to link fund flows to dealer inventory. Your literature is
  where that claim will be judged. The closest work the paper itself discusses is in Section 1.2."
- Bad: "The contribution looks incremental relative to prior flow-fragility papers. Check this."

Keep out of every assignment: your own opinion of the paper, the author's hopes or worries, and what
other reviewers are being asked. Facts are fine (target journal, that it is a job market paper, that
a previous version was rejected at journal X).

Give each seat a distinct id when a persona is used twice (`lit-bond-liquidity`, `lit-fund-flows`).

### Step 4. Round 1: independent reviews

Launch all reviewers in parallel, in a single message, each as a fresh general-purpose subagent on the
session's model (review quality is the product, so do not downgrade the model unless the user asks for
a cheap run). Use this launch prompt:

```
You are reviewer "<reviewer-id>" on a simulated review panel for a paper under consideration at <journal>.

Read these files in order and follow them:
1. Your persona: <path>
2. The shared reviewer brief: <skill-dir>/references/reviewer-brief.md
3. Your assignment for this paper: <run>/prompts/<reviewer-id>.md

Then read the paper as your persona instructs and write your Round 1 report to the path in your
assignment. Reply with only: your recommendation, the title of your top issue, and the report path.
```

When all are back, read every report in full. Check each against the brief before moving on: are
the issues anchored to specific places in the paper, and did the reviewer deliver the lens-specific
section their persona requires? If a report is generic or missed its deliverable, send it back once
with a specific request. A weak report that goes forward weakens everything downstream.

### Step 5. Build the issue ledger

Write `ledger.md` in the run folder: one row per distinct issue across all reports.

| # | Issue | Where in paper | Raised by (severity each) | Status |
|---|---|---|---|---|

- Merge two reviewers' points only when they are the same concern about the same thing. Two reviewers
  attacking the same table for different reasons are two issues.
- **Status** is one of: `consensus` (two or more reviewers raised it independently), `contested`
  (reviewers conflict: one's strength is another's flaw, or severities are far apart), `solo` (one
  reviewer only).
- Before recording any issue as FATAL or MAJOR, check it against the paper yourself. Reviewers
  sometimes miss that the paper already addresses a point in a later section or the appendix. Mark such
  issues `addressed in paper (where)` rather than deleting them: if a reviewer missed it, a real
  referee may too, and that is an exposition problem worth reporting.
- Record literature claims separately with their verification tags. An unverified "this has been done
  by X" must never reach the author stated as fact.

At `quick` and `desk` depth, skip to Step 7.

### Step 6. Round 2: cross-examination

Read `references/cross-exam.md` and follow it. In short: select a docket of the contested issues, the
serious solo issues, and the top consensus issues; send each reviewer the docket with the other
reviewers' arguments and a role-specific task (the champion must answer the rejection case, the
skeptic must attack the champion's best version, specialists adjudicate disputes in their area);
collect positions and final votes.

One round is the default. Further rounds mostly produce politeness and convergence. Run a second
exchange only on a specific FATAL question that Round 2 left genuinely unresolved, and only between
the reviewers involved.

### Step 7. Synthesize as handling editor

Write `PANEL_REPORT.md` in the run folder using `references/synthesis-template.md`. How to rule:

- **Rule; do not average.** For each contested issue, decide who is right and say why, citing the
  paper. Where you cannot decide, say what evidence would decide it.
- **Weigh evidence, not votes.** One well-evidenced fatal point outweighs five mild approvals.
  Independent agreement in Round 1 is the strongest signal the panel produces. Agreement that appears
  only in Round 2, after reviewers have read each other, is much weaker.
- **Discount what deserves it**: points with no anchor in the paper, generic requests ("more
  robustness") with no named threat, novelty objections resting on unverified citations, and
  anything the paper already addresses.
- **Protect the author's time.** A revision plan that lists everything is as useless as one that lists
  nothing. Sort actions by leverage: how much each moves the decision relative to what it costs
  (rewrite, new analysis on existing data, new data). Include a "Set aside" section naming the
  comments you recommend ignoring and why; knowing what not to do is half the value.
- **Separate ceiling problems from fixable problems.** If the binding constraint is the importance of
  the question, say so in the first paragraph. More robustness tables do not raise a ceiling; a
  reframing or a different target journal might.
- **Stay honest about what this is.** The panel is a stress test by simulated reviewers, not a forecast
  of a real editorial decision. Say that once, briefly, and do not let it soften the content.

### Step 8. Close the loop

1. Tell the user where the report is and give the bottom line in a few sentences: where the paper
   stands, the biggest risk, the highest-leverage change. Do not paste the whole report.
2. Offer the next move: work through the revision plan together, or re-run the panel after revising.
3. If any reviewer was ad hoc, say that it can be kept for future runs with `save <name>`.

Everything about the run lives in the run folder. Nothing is written to the skill folder.

## Run folder layout

```
<paper-folder>/grill_<paper-name>_<YYYY-MM-DD>/
├── PANEL_REPORT.md      the deliverable
├── 00_panel.md          paper facts, roster, why each reviewer was cast
├── ledger.md            issue ledger
├── paper.txt            extracted text (page markers for a PDF; cite by line for TeX)
├── <appendix>.txt       online appendix and any other companion, when there is one
├── figures/, *.bib      figure files and bibliography gathered from a TeX source
├── prompts/<id>.md      each reviewer's assignment
├── round1/<id>.md       independent reports
└── round2/<id>.md       cross-examination positions (plus docket.md)
```

## Re-run after revision

When the user has revised the paper and wants to know whether it worked, find the earlier run folder
(given, or the most recent `grill_*` folder next to the paper) and:

1. Reuse the earlier roster unless the user changes it, so the comparison is like for like.
2. In each assignment, add a section "Issues from the previous round" listing the earlier ledger's
   open issues that fall under that reviewer's lens. Instruct the reviewer to form and write down
   their fresh view of the new draft first, and only then mark each earlier issue as resolved, partly
   resolved, unresolved, or made worse, with the location in the new draft. Fresh view first, because a
   reviewer who starts from the old list stops looking for new problems.
3. Add a "Since the last panel" section at the top of the new report: what was resolved, what
   remains, what the revision newly introduced, and whether the votes moved.

## Failure modes this design guards against

Knowing these helps you make sensible calls in situations the steps do not cover.

- **Correlated reviewers.** All reviewers are the same underlying model. Their diversity comes only
  from what they are asked and what they read, so keep mandates distinct and Round 1 independent.
- **Invented literature.** A confident, wrong "X (2019) already shows this" can send the author
  chasing a paper that does not exist or abandoning a real contribution. Citations carry verification
  tags from the reviewer through to the final report.
- **Laundry lists.** Six reviewers can produce sixty comments. The ledger, the docket, and the
  editor's rulings exist to cut that to the handful that matter.
- **Leading the witness.** Tailoring that tells a reviewer what to find produces confirmation, not
  review.
- **Polite convergence.** In Round 2 reviewers tend to agree with each other. The role-specific tasks
  force the champion and skeptic to keep their mandates; treat late agreement with suspicion.

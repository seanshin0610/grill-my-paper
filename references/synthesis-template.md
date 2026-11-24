# Panel report template

The handling editor writes this after reading every report and the cross-examination. It is written
to the author. The author should be able to read sections 1 to 3 in five minutes and know where the
paper stands, and use section 6 as a work plan.

Write in plain declarative prose. Refer to reviewers by role. Every issue carries its location in the
paper. Do not repeat the same point across sections; later sections refer to issue ids.

```markdown
# Panel report: <paper title>

**Draft:** <file> · **Target:** <journal> · **Date:** <date> · **Depth:** <quick | standard | full>
**Panel:** <reviewer ids>

*This is a stress test by simulated reviewers. It shows where the draft is vulnerable; it does not
forecast an editorial decision.*

## 1. Bottom line

<Five sentences at most. Where the draft stands against the target journal's bar. The single biggest
risk. Whether that risk is a ceiling problem (importance of the question, size of the contribution) or
a fixable problem (execution, framing, exposition). The single highest-leverage change.>

## 2. Scoreboard

| Reviewer | Lens | Round 1 | Final | Deciding reason |
|---|---|---|---|---|

<One or two sentences on the pattern: where the votes split and why, and which votes moved.>

## 3. The two cases

**The rejection case.** <The strongest case against the paper that survived cross-examination, written
as the paragraph a real referee would send to the editor. If the champion defeated parts of the
original case, leave those parts out.>

**The acceptance case.** <The best version of the contribution that survived the skeptic's attack: what
the paper shows, whose beliefs it changes, and why that matters. If this differs from how the draft
currently pitches itself, say so; that gap is usually the most valuable finding of the panel.>

## 4. Issues and rulings

### Consensus issues
<Raised independently by two or more reviewers in Round 1. These are the most reliable findings.>

#### I1. [FATAL | MAJOR] <title>
- **Where:** <location>
- **Issue:** <one or two sentences>
- **Raised by:** <roles>
- **In cross-examination:** <what was argued; who moved>
- **Ruling:** <the editor's judgment and the reason>
- **What to do:** <the fix, or "no fix; see section 7 on positioning">

### Contested issues
<Same fields. The ruling must say who was right and cite the paper. If it cannot be decided from the
paper, say what evidence would decide it.>

### Solo issues worth acting on
<Raised by one reviewer, checked by the editor against the paper, and judged real.>

### Already addressed in the paper, but missed by a reviewer
<List with the location of the existing answer. If a careful reviewer missed it, a referee may too:
recommend moving or signposting it.>

## 5. Literature and positioning

- **Closest papers and what remains new:** <from the literature specialists; each citation tagged
  [verified] or [unverified]>
- **Missing or mishandled citations:** <...>
- **Unverified claims to check by hand:** <any claim about prior work that the panel could not verify.
  State these as leads, never as facts.>

## 6. Revision plan

Ordered by leverage: effect on the decision relative to cost.

### Do before submitting
| # | Action | Addresses | Type | Effort | Why this first |
|---|---|---|---|---|---|

### Do if time allows
| # | Action | Addresses | Type | Effort | Payoff |
|---|---|---|---|---|---|

<Type is one of: reframe, rewrite, new analysis on existing data, new data, cut.
Effort is S (days), M (weeks), or L (months).
Actions must be specific enough to start on: name the table, the specification, the paragraph.>

### Set aside
<Comments from the panel that the editor recommends not acting on, each with a one-line reason:
uninformative test, outside the paper's scope, rests on an unverified citation, already handled,
matter of taste. This section is required.>

## 7. Positioning and fit

- **Pitch:** <title, abstract, and first-paragraph changes suggested by the panel, especially the
  editor's first read and the champion's best version>
- **Journal fit:** <how the paper fits the target; if the panel thinks another journal on the author's
  list fits better, say so and why>
- **Likely referees:** <the types of referee an editor would pick, from the editor's first read, and
  what that implies about which literature's concerns to pre-empt>

## 8. Files

- Individual reports: `round1/`  · Cross-examination: `round2/` · Issue ledger: `ledger.md`
```

## Adjustments by depth

- `quick` and `desk`: there is no cross-examination. Drop the "In cross-examination" fields and the
  "Final" column. Say in section 1 that contested points were ruled on by the editor without the
  reviewers answering each other, which is weaker.
- Re-runs: add "## 0. Since the last panel" before section 1 (resolved, remaining, newly introduced,
  how the votes moved).

## Length

Aim for 1,500 to 2,500 words at `standard`. The report earns its keep by being shorter than the sum
of its inputs. If it is growing past that, the editor is forwarding comments instead of ruling on them.

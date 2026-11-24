# Round 2: cross-examination

Round 1 produces independent opinions. Round 2 makes the reviewers answer each other on the points
where the answer matters. It is run by the handling editor (you) and is deliberately narrow: a fixed
docket, one exchange, positions backed by locations in the paper. Sections 1 to 3 are Round 2.
Section 4 covers Rounds 3 and 4, which run only when the user asked for them with `rounds=`.

## 1. Build the docket

From `ledger.md`, pick at most eight issues, in this priority:

1. Every **contested** issue (a strength to one reviewer and a flaw to another, or severities far apart).
2. Every **solo** issue rated FATAL or MAJOR. One reviewer may have seen something real that the
   others missed, or may be wrong; the others can tell you which.
3. The top **consensus** issues, not to re-argue whether they exist but to argue about the fix: is
   there one, what is the cheapest convincing version, and would it be enough?
4. The champion's proposed best version of the paper, as an item of its own.

Write the docket to `round2/docket.md`. For each item give: an id (D1, D2, ...), a neutral one-line
statement of the issue, where it sits in the paper, and each reviewer's Round 1 position on it in two
or three sentences, attributed by role ("skeptic", "lit-fund-flows"). State positions fairly and at
full strength. Do not signal which side you favor; a docket that leans tells reviewers what to say.

Leave off the docket anything you already confirmed the paper addresses, and all minor points.

## 2. Send each reviewer their Round 2 task

Continue each Round 1 reviewer if you can message an existing subagent (they keep their reading of
the paper, which makes Round 2 cheaper and better). If you cannot, launch a fresh subagent with: the
persona path, the brief path, their assignment, their own Round 1 report, and the paper paths, and
tell them to re-read the parts of the paper the docket touches.

Send all reviewers in parallel. Message:

```
Round 2 (cross-examination). The docket is at <run>/round2/docket.md. It contains the issues the
editor wants argued and what each reviewer said in Round 1.

Follow the "Round 2: cross-examination" section at the end of the reviewer brief
(<skill-dir>/references/reviewer-brief.md): take a position on each docket item within your
competence, backed by a location in the paper, in the Round 2 format given there.

Your specific task this round: <role task from the table below>

Write your response to <run>/round2/<reviewer-id>.md, then reply with only your final
recommendation and whether it changed.
```

The rules and the reply format live in the reviewer brief so that every reviewer, continued or
fresh, reads the same text and tuning has one place to edit.

### Role tasks

| Reviewer | Round 2 task |
|---|---|
| skeptic | Attack the champion's best version of the paper: would that version survive at the target journal, and what would its referee say? Then go through your own FATAL and MAJOR points and state which survive every fix proposed by anyone on the panel. Finish with the rejection paragraph you would still write. |
| champion | Answer the rejection case point by point. Classify each FATAL and MAJOR issue on the docket as (a) wrong: show where the paper already handles it; (b) fixable: give the cheapest fix that a skeptical referee would accept; or (c) real and not fixable: concede it and propose the framing or scope that keeps the paper alive without it. A champion who concedes nothing is not credible, and one who concedes everything is not a champion. |
| senior-scholar | The panel has now established what survives. Restate the contribution that is left and say whether it is enough for the target journal. Rule on disputes about importance and ceiling, as opposed to validity. Sort the proposed fixes into those that would raise the paper's level and those that would only polish it. |
| literature-specialist | Adjudicate every novelty or positioning dispute that touches your literature. Run targeted searches on any disputed claim about prior work and report what you found, with verification tags. |
| identification | For each analysis anyone requested, say whether it is informative (what it would rule out, and what result would be damning) or busywork. Rank the informative ones. Adjudicate disputes about what the design can support. |
| mechanism | Adjudicate disputes about the channel: for each alternative explanation raised, say what it predicts differently and whether evidence already in the paper discriminates. |
| editor-desk | You have now seen what full reads turned up. Which docket items would actually weigh on an editor's decision, and which would an editor wave through? Has your first-read decision changed? |
| outsider | Which docket items change whether a non-specialist should care about the paper, and which are inside baseball? |
| auditor | Check any factual dispute about what the tables show. Report what the numbers actually are. |
| institutional | Rule on disputes that turn on how the setting actually works. |
| ad hoc reviewers | Write a task in the same spirit: what can this lens settle that the others cannot? |

## 3. Read the exchange as an editor

- Update `ledger.md`: for each docket item, record who took which side and what evidence was cited.
- Changes of position with a stated reason are informative. Blanket agreement is not; where a reviewer
  endorses everything, weigh their Round 1 report and largely ignore their Round 2.
- If a factual dispute about the paper remains (one reviewer says Table 4 shows X, another says it does
  not), open the paper and settle it yourself. Do not pass an unresolved factual dispute to the author.
- If the user gave no `rounds=` and one specific FATAL question remains genuinely open and turns on
  argument rather than fact, you may run one more exchange between only the two or three reviewers
  involved, each seeing the other's Round 2 answer. Otherwise stop here. When the user set the number
  of rounds, run what they asked for and do not add this exchange on top.

## 4. Later rounds (Round 3 and Round 4)

Run these only when the user asked for three or four rounds. Each is narrower than the one before,
and each has to earn its cost: by Round 3 every reviewer has read every other, so agreement comes
easily and means little. What a later round can still add is a better argument on a point that is
truly open.

### Rewrite the docket

Before each later round, write a new docket to `round<N>/docket.md` with only the issues still in
dispute after the round before. An issue is still in dispute when reviewers hold opposed positions on
it, or when a QUALIFY leaves the deciding point open. Drop:

- every item on which the panel now agrees;
- every item you settled yourself by opening the paper;
- every item that came down to wording, which you can rule on without them.

Add an item only if the previous round raised a new FATAL or MAJOR issue. For each item that stays,
give what the last round settled, the question still open in one sentence, and each reviewer's
position from the last round at full strength. As before, do not signal which side you favor.

### Stop early when nothing is left

If no issue is still in dispute, do not run the round, even though the user asked for more. Reviewers
with nothing to argue about will only agree with each other, at the price of reading everything
again. Record in the report how many rounds ran, how many were asked for, and that the panel had no
dispute left.

### Send the round

Send it to every reviewer, in parallel, continuing the same subagents:

```
Round <N> (cross-examination, continued). The docket is at <run>/round<N>/docket.md. It holds only
the issues still in dispute after Round <N-1>. The other reviewers' Round <N-1> responses are in
<run>/round<N-1>/. Read the docket and those responses, go back to the paper where they point to it,
and answer again.

Follow "Later rounds" at the end of the reviewer brief
(<skill-dir>/references/reviewer-brief.md). If you change a position you held in Round <N-1>, say
what changed your mind: which argument, or which passage of the paper. A changed position with no
reason will be disregarded.

There is no new role task. Your role still decides what you argue from.

Write your response to <run>/round<N>/<reviewer-id>.md, then reply with only your final
recommendation and whether it changed.
```

A reviewer with nothing to say on the remaining items may answer in one line. That is a fair result.

### Read it as an editor

- Update `ledger.md` with who moved in this round and the reason each gave.
- A change of position with no stated reason counts for nothing. Rule on the argument that reviewer
  made earlier.
- Agreement that first appears here is the weakest the panel produces. Weigh the argument that
  produced it, not the fact of it.
- An issue still in dispute after the last round is yours to rule on. Say who you side with and why,
  or say what evidence would decide it.

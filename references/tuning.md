# Tuning reviewers and managing the persona library

This file is for the occasions when the user asks to change the skill: `tune <feedback>`, `personas`,
`save <name>`, or a request in so many words to change a reviewer or a default.

It is not triggered by a reaction to a reviewer's output during a conversation. "The skeptic was
generic" is a comment on a report; answer it as part of discussing the paper. Nothing in the skill
folder changes unless the user asks for it to change.

## Tuning from feedback

### 1. Get the evidence

Find the run the feedback is about: the one in this conversation, or the run folder the user names
(it sits next to the paper as `grill_<paper-name>_<date>`). If you cannot tell which run is meant,
ask. Read three things for the reviewer in question:

- their assignment (`prompts/<id>.md`),
- what they produced (`round1/<id>.md`, and `round2/<id>.md` if it exists),
- the persona file as it stands now.

Do not tune from the user's sentence alone. "Generic" can mean the mandate was vague, the tailoring
named the wrong literature, the reviewer had no search tool, or the paper gave them little to work
with. Each has a different remedy, and only the files tell you which it was.

If the feedback is vague ("the lit specialist was bad"), ask what specifically they wanted and did
not get, or point to the passage you think they mean and confirm.

### 2. Locate the fault

| Where the fault lies | Signs | What to change |
|---|---|---|
| The persona | The reviewer followed their persona and the result was still not what a real reviewer of that type would produce: wrong emphasis, missing deliverable, a trap not named | `personas/<id>.md` |
| The assignment | The persona is fine but the editor aimed it badly: wrong or too-broad literature, tailoring that was vague or leading | Casting and tailoring guidance in `SKILL.md` Steps 2 and 3; nothing if it was a one-off |
| The shared brief | The same complaint applies to several reviewers: too long, inflated severity, unanchored points, format | `references/reviewer-brief.md` |
| Cross-examination | Reviewers caved, talked past each other, or the docket missed the real dispute | `references/cross-exam.md` |
| The synthesis | The reports were fine but the editor's rulings or revision plan were weak | `SKILL.md` Step 7 or `references/synthesis-template.md` |
| The user's standing preference | Not a quality problem; the user wants something different by default | `profile.md` (see "Change defaults") |
| Nothing fixable by a prompt | The reviewer could not have known (a working paper not online, a private institutional fact), or the paper really is ambiguous there | Change nothing. Say so. |

Be willing to land on the last row. Changing a prompt in response to every miss makes it worse.

### 3. Generalize before editing

Restate the feedback as a property of reviews in general, not of this paper. From "it did not notice
that my Table 5 already rules out the liquidity story" to "the reviewer raises alternative explanations
without checking whether later tables address them". The second version is what goes into the prompt.
An instruction that mentions this paper's topic, variables, or tables is overfitted; rewrite it.

Then ask whether the general version is already in the persona. If it is and the reviewer ignored it,
the instruction is probably buried or unexplained: move it up, or add the reason it matters. Adding a
second copy in capital letters is not the fix.

### 4. Make the smallest edit that would have prevented it

Prefer, in this order:

1. Rewriting the sentence in the persona body that should have covered this.
2. Adding a sentence to the relevant section of the body ("How to work" or "Traps"), with its reason.
3. Adding a line under "Calibration notes" at the end of the persona. Use this only for a specific
   exception that does not fit the body.

The user asked for the change, so make it and show it as a short before-and-after. Ask first only if
the change would alter a persona's mandate or affect every reviewer (the shared brief), since those
shift the whole panel. Change only what the feedback calls for; do not tidy other parts of the file
while you are there.

### 5. Keep what worked

When the user asks to keep a comment as an example of what they want, add it to the persona under a
section "What good looks like" (create the section above "Calibration notes" if it is not there):

- State the pattern in one line (what made it good), then give the comment with the paper's specifics
  replaced by placeholders such as [main outcome] and [Table N], in at most 80 words. Nothing that
  identifies the user's paper goes into a persona.
- Keep at most three exemplars per persona. When adding a fourth, drop the weakest. Examples steer a
  reviewer strongly, and too many, or ones that are too specific, produce imitations.

### 6. Offer the only real test

A prompt change is a guess until it is tried. Offer to re-run just that reviewer on the same paper with
the revised persona (one subagent, same assignment, output to `round1/<id>.v2.md` in the run folder)
and show the old and new reports side by side. Do it if the user says yes.

### 7. Prune

When a persona's "Calibration notes" grow past about six lines, fold them into the body and clear the
section. When a persona passes about 90 lines, look for instructions that are no longer earning their
place and remove them. Personas that only ever grow become a list of patches that reviewers follow
unevenly.

## Managing the library

### List the personas

Search `personas/` for the frontmatter lines (`^(id|lens|use_when|parameters):`), skipping
`_TEMPLATE.md`, and show them as a table.

### Save an ad hoc reviewer

When the user says `save <name>` after a run that used an ad hoc reviewer:

1. Take the persona text from that reviewer's assignment file (`prompts/<id>.md`).
2. Replace anything specific to that paper with a `{parameter}` and list the parameters in the
   frontmatter. A saved persona must make sense for the next paper.
3. Check it against the five criteria at the top of `personas/_TEMPLATE.md`. If it has no deliverable
   of its own or no named traps, add them now; that is usually why an ad hoc reviewer felt thin.
4. Save as `personas/<id>.md` and tell the user how to seat it (`reviewers: ..., <id>`).

### Add a reviewer type from a description

When the user describes a reviewer they want in the library ("a reviewer who is a behavioral finance
person", "the kind of referee I got at RFS last time"), write it from `personas/_TEMPLATE.md`. If the
user has a real referee report that exemplifies the type, ask for it: a real report is the best
possible source for the persona's mandate, habits, and traps. Extract the reviewer's way of working
from it, not its paper-specific content.

### Fork or retire

Fork a persona (copy to a new id) when the user wants a variant that should coexist with the original,
such as a journal-specific skeptic. Retire a persona only when the user asks; move it to
`personas/retired/` so its text is kept.

### Change defaults

When the user asks to change a default (target journal, depth, seats to always or never include,
report length), put it in `profile.md`. If `profile.md` does not exist yet, create it as a copy of
`profile.default.md` and then make the change. Confirm the new default to the user in one line.

## After any change

These files live in the user's own skills folder, so edits persist across sessions. If the folder is a
git repository, say that the change is uncommitted; do not commit or push unasked.

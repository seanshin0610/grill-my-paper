# grill-my-paper

A Claude Code skill that puts your paper draft in front of a panel of reviewer agents before real
referees see it.

Each reviewer has a different job: a referee who looks for the fastest route to rejection, a champion
who looks for the best version of the paper, specialists in the literatures you cite, a referee for
the empirical design, an editor who reads only the first few pages, and others. They review the paper
independently, then argue over the points they disagree on. An editor rules on the disputes and writes
a verdict and a revision plan for your target journal, ordered by payoff and including what to ignore.

## Requirements

- [Claude Code](https://claude.com/claude-code). The skill launches subagents, so it does not work in
  plain chat.
- Python 3 with two packages: `pip install pymupdf markdown`. PyMuPDF reads a PDF paper (pypdf or
  pdfplumber also work for that) and, with `markdown`, renders the final report as a PDF. Without them
  the review still runs on a TeX paper and gives you the report as Markdown.

## Install

macOS or Linux:

```bash
git clone https://github.com/seanshin0610/grill-my-paper.git ~/.claude/skills/grill-my-paper
```

Windows (PowerShell):

```powershell
git clone https://github.com/seanshin0610/grill-my-paper.git "$env:USERPROFILE\.claude\skills\grill-my-paper"
```

Start a new Claude Code session and type `/grill-my-paper help`.

## Use

Open a session in the folder that holds your paper, then:

```
/grill-my-paper my-paper.pdf depth=quick
```

| Command | What it does |
|---|---|
| `/grill-my-paper <paper.pdf or .tex>` | Review at the default depth |
| `... depth=quick` / `standard` / `full` / `desk` | Choose how many reviewers and whether they debate |
| `... target=RFS` | Set the target journal |
| `... model=opus` | Run the reviewers on a model other than the session's |
| `... also=online_appendix.pdf` | Give reviewers another file; for a TeX paper the appendix, figures, and bibliography are found automatically |
| `... reviewers: skeptic, champion, lit: <a literature>` | Choose the reviewers yourself |
| `... add: <describe a reviewer>` | Add any reviewer type you can describe |
| `<revised paper> rerun` | After revising, check which earlier issues are resolved |
| `tune <what you liked or disliked>` | Improve a reviewer from a past run |
| `personas` | List the reviewer types |
| `help` | Full help |

Results go in a folder next to the paper, `grill_<paper-name>_<date>/`. Read `PANEL_REPORT.pdf` first
(the same report is there as Markdown).
Your paper's own files are read and never changed.

If the paper lives in a git repository, such as an Overleaf project shared with coauthors, the skill
adds `grill_*/` to that repository's `.git/info/exclude`. That file is local to your machine, so the
reviews cannot be committed or pushed by accident and your coauthors see no change.

## Cost

Every reviewer reads the whole paper, and reads it again in the debate round. A `standard` run is five
reviewers over two rounds. Start with `depth=quick` (three reviewers, no debate) to see what you get.

## Make it yours

- **Your field and journals.** The shipped defaults in `profile.default.md` are for finance (JF, RFS,
  JFE). Tell the skill to change one ("default to AER", "always seat the auditor") and it writes
  your own `profile.md`, which git ignores.
- **Your reviewers.** Reviewer types are plain Markdown files in `personas/`. To change one, run
  `/grill-my-paper tune <what you liked or disliked>` after a review. You can also describe a new
  reviewer type and save it.

The skill keeps no record of your runs or your papers, and it does not edit itself during a review.
Everything a run produces stays in the run folder next to your paper. Skill files change only when
you ask with `tune`, `save`, or a request to change a default.

## Updating

```bash
git pull
```

Run it inside the skill folder. If you have tuned personas in your copy, commit your changes first;
otherwise a pull that touches the same persona will stop with a conflict.

## Keep in mind

- This is a stress test by simulated reviewers. It shows where a draft is vulnerable; it does not
  forecast what real referees will decide.
- Reviewers tag every outside citation as verified or from memory. A separate agent, which never sees
  your paper, looks up the ones from memory and the ones the report relies on. Still read a cited
  paper yourself before you rely on it.

## License

MIT. See [LICENSE](LICENSE).

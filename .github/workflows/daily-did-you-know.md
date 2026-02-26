---
description: "Daily 'Did You Know?' fact mined from research papers, posted to the website"
on:
  schedule: daily
  skip-if-match: 'is:pr is:open in:title "daily did-you-know"'
permissions:
  contents: read
safe-outputs:
  create-pull-request:
    max: 1
  noop:
---

# Daily Did You Know

You maintain a "Did You Know?" section on a personal academic website. Every day you surface one interesting, non-trivial fact from the author's research papers and open a PR with the change.

## Context

- The website is `index.html` in the repo root.
- Research papers (as markdown) live in `files/markdown/*.md` (there are 32 papers).
- A historic log of past facts lives at `files/did-you-know-log.md`. It may not exist yet on the first run.
- The current "Did You Know?" text is inside a `<p id="did-you-know">` element in `index.html`, located between the `<!-- AGENT-UPDATED: did-you-know -->` comment and the next `<h3>` tag.

## Instructions

1. **Read the historic log** at `files/did-you-know-log.md` (if it exists) to learn which facts and papers have already been used.

2. **Pick a paper** from `files/markdown/`. Prefer papers that have NOT been featured recently (check the log). If all papers have been used, it is okay to revisit a paper — but choose a different fact.

3. **Read the chosen paper** and extract one interesting, non-trivial, and concise fact (1–3 sentences). The fact should be surprising or illuminating to a general computer-science audience. Avoid generic statements; pick something specific and memorable.

4. **Format the new fact** as a short HTML snippet:
   ```
   <strong>Did you know?</strong> [Your fact here] <em>(from: <a href="files/markdown/FILENAME.md">Paper Title</a>)</em>
   ```

5. **Archive the previous fact**:
   - Read the current content of the `<p id="did-you-know">` element in `index.html`.
   - If the current content is NOT the placeholder text ("Placeholder: check back soon"), prepend it as a new entry at the TOP of `files/did-you-know-log.md` with today's date as a header (`## YYYY-MM-DD`).
   - If the log file does not exist, create it with a `# Did You Know — Historic Log` title before adding the entry.

6. **Update `index.html`**: Replace the content of the `<p id="did-you-know">` element with the new fact HTML snippet. Do NOT change anything else in the file.

7. If for any reason you cannot find a suitable fact or there is an error, call the `noop` safe output explaining why.

## Quality Guidelines

- Facts should be **specific**: mention concrete numbers, system names, vulnerability names, algorithm names, or surprising results.
- Facts should be **accessible**: a CS undergraduate should be able to appreciate them without deep domain knowledge.
- Facts should be **varied**: alternate between security, concurrency, GPU, testing, and architecture topics across runs.

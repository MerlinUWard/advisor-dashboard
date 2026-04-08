# Gong Extraction Rules

Rules for identifying projects, tasks, due dates, documents, and sentiment from Gong transcripts.

---

## Project Detection

A project mention is a named, multi-step initiative being tracked over time. Detect project mentions using these signals:

**Strong signals (high confidence — create/match project):**
- Explicit "project" label: "the rebrand project", "the Q2 campaign project"
- Initiative names: "the website redesign", "the pricing rollout", "the email sequence build"
- Campaign names: "the spring campaign", "the Black Friday push"
- Proper noun + action noun: "the Sales Deck", "the Newsletter", "the Onboarding Flow"

**Weak signals (require supporting context — flag if no existing match):**
- Generic references without names: "the project", "that thing we're working on"
- Single-word mentions without context: "the relaunch" (of what?)

**Not a project:**
- One-time tasks: "send them the proposal", "follow up on email"
- Recurring processes: "our weekly call", "the monthly report"
- Past events: "the conference we went to"

**Matching to existing projects:**
1. Exact name match (after learn.md corrections) → update existing
2. Alias match from learn.md → update existing
3. >85% fuzzy similarity → update existing (note the match)
4. 60–85% fuzzy similarity → flag for review, do not auto-merge
5. No match → create new project

---

## Task Detection

A task is a specific, assigned action with an implied or explicit owner and (optionally) a deadline.

**High-confidence task patterns:**
- "[Name] is going to [verb]..." → task for named advisor
- "[Name] will [verb]..." → task
- "We need to [verb]..." → task (assign to advisor who is the call participant)
- "Can you [verb]...?" + acknowledgment → task
- "I'll [verb]..." → task for the speaking advisor
- "Action item: ..." → task (explicit)
- "Follow up on...", "Send...", "Schedule...", "Draft...", "Review..." → tasks

**Do not create tasks for:**
- Completed past actions ("we sent that last week")
- Hypothetical discussions ("we could potentially...")
- Client commitments that are not advisor actions

**Task owner assignment:**
- If a name is mentioned: match to advisor from setup.json (by Gong identity or alias)
- If "I" or first-person: attribute to the advisor who is the call participant
- If unclear: assign to the OA and flag

---

## Due Date Extraction

Convert all relative date references to absolute ISO dates based on the call date.

| Transcript phrase         | Resolution                                  |
|---------------------------|---------------------------------------------|
| "by end of week"          | Friday of the call's week                   |
| "by end of next week"     | Friday of the following week                |
| "by [weekday]"            | Next occurrence of that weekday after call  |
| "end of month"            | Last day of call's month                    |
| "by Q[N]"                 | Last day of that quarter in call's year     |
| "next [month name]"       | First day of that month                     |
| "[Month] [day]"           | That date in the current or next year       |
| "ASAP" / "soon"           | null due date + flag in task description    |
| "no rush" / "eventually"  | null due date                               |

Always confirm ambiguous dates (e.g., "the 15th" without a month) by checking call date context.

---

## Document Reference Detection

Listen for mentions of documents that should be linked in Google Drive.

**Trigger phrases:**
- "the budget", "our budget doc", "the budget spreadsheet"
- "our dashboard", "our sheet", "the tracking doc"
- "the proposal", "the deck", "the slide deck", "the presentation"
- "the report", "the weekly report", "the monthly report"
- "the contract", "the agreement", "the SOW"
- Any phrase mentioning a specific file name with an extension

**After detection:**
1. Apply learn.md Document Name Aliases to normalize the reference
2. Search the client's Google Drive folder for a matching file (see document-linking.md)
3. If found: link to the relevant project or client record
4. If not found: add to flagged items as "missing_doc" with the reference phrase

---

## Sentiment Detection

Analyze the overall call tone and the client's expressed sentiment. Read both sides of the conversation — the advisor AND the client speaker(s).

Look for:
- Positive: enthusiasm, praise, agreement, expressions of progress or satisfaction
- Cautious: uncertainty, requests to revisit, expressions of concern or delay
- Negative: frustration, disappointment, questioning value, mentions of cancellation

Weight client speaker statements more heavily than advisor statements for sentiment scoring.

Default to "neutral" when no strong signals are present. Never default to "positive" without evidence.

---

## Call Summary Generation

Generate a 2–4 sentence narrative summary for `advisor_call_summaries`. Include:
1. The main topic or focus of the call
2. Any significant decisions or commitments made
3. The overall tone/outcome
4. Any urgent items or risks surfaced

Keep it factual and crisp. Do not editorialize. Write from the perspective of someone briefing a team lead who wasn't on the call.

Example:
> "Discussed the Q2 email campaign timeline; client expressed concern about the April 1 launch date due to internal bandwidth constraints. Advisor committed to sending a revised timeline by end of week. Client is cautiously optimistic about the content quality but wants to see a draft before approving. No blockers on the advisor side."

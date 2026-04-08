# Sentiment & MOI Score Reference

## MOI Score Interpretation

The MOI (Measure of Impact) score is a numeric value from 0–5 pulled from the Client Performance Google Sheet. It represents the client's overall engagement and satisfaction level for the week.

| Score    | Label    | Meaning                                                           |
|----------|----------|-------------------------------------------------------------------|
| 4.0–5.0  | Positive | Client is highly engaged, goals on track, relationship strong     |
| 3.0–3.9  | Neutral  | Client is engaged, normal progress, no major concerns             |
| 2.0–2.9  | Cautious | Some friction, slower progress, or client expressing uncertainty  |
| 0–1.9    | Negative | Significant concerns, possible churn risk, requires immediate attention |

Display rules:
- Always show the score number alongside the label (e.g., "Positive 4.2")
- If `synced_at` is more than 14 days old, add a muted "(stale)" note
- If `moi_access_error` is set, add "⚠" prefix and show last synced date

## Call-Level Sentiment (from Gong)

Call sentiment is detected during Gong transcript processing and stored on each call summary object. It reflects the tone of that specific call, not the overall client relationship.

| Sentiment | Keyword Signals |
|-----------|----------------|
| Positive  | "great", "love it", "excited", "on track", "ahead of schedule", "happy with", "good progress" |
| Neutral   | factual discussion, no strong emotional signals, "sounds good", status updates only |
| Cautious  | "concerned about", "not sure", "need to revisit", "a bit worried", "behind", "delayed", "waiting on" |
| Negative  | "frustrated", "disappointed", "not working", "unhappy", "want to cancel", "reconsidering", "not seeing results" |

Use these as signals, not rules. Apply judgment. A call discussing a challenge calmly may still be "neutral" rather than "cautious."

## Note Tags

When tagging notes, use these consistently:

| Tag         | When to apply                                                      |
|-------------|-------------------------------------------------------------------|
| `sentiment` | Note reflects how the client feels about the engagement overall    |
| `challenge` | Note describes a specific obstacle, blocker, or problem           |
| `risk`      | Note suggests possible churn, budget cuts, or relationship damage |
| `milestone` | Note captures a win, completion, or positive progress marker      |
| `general`   | Informational — doesn't fit other categories                      |

A note can have multiple tags.

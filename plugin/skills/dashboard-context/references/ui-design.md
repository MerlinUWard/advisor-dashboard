# UI Design Specification
# This file is the authoritative visual spec for all dashboard views.
# Edit this file to change colors, layout, or component patterns.
# Changes here are reflected on the next dashboard render automatically.
# Last updated: 2026-03-16 — Updated to match Cardone Ventures platform aesthetic

---

## Overall Aesthetic

Clean, modern, consumer-app feel. Pure white surfaces, generous white space, bold typography hierarchy, vibrant but small category badges. The vibe is polished and professional — not a spreadsheet, not a CRM form. Looks like a product people actually want to use.

---

## Color Palette

```
Page background:   #FFFFFF  (pure white — NOT gray)
Surface:           #FFFFFF  (cards are also white)
Surface subtle:    #F8FAFC  (used sparingly for inset sections)
Border:            #E2E8F0  (very light, almost invisible borders)
Text Primary:      #0F172A  (near-black — deep navy, not pure black)
Text Secondary:    #64748B  (medium slate gray)
Text Muted:        #94A3B8  (light slate — timestamps, metadata)

Accent Blue:       #3B82F6  (primary action buttons, links)
Accent Blue Dark:  #1D4ED8  (hover state for blue elements)
```

---

## Advisor Role Colors

Vibrant, uppercase badge style. Text is bold and uppercase inside the badge.

```
Operations:   text #1D4ED8   bg #DBEAFE   (blue)
Finance:      text #065F46   bg #D1FAE5   (green)
Marketing:    text #5B21B6   bg #EDE9FE   (purple)
```

---

## Sentiment / MOI Colors

| Sentiment | Score Range | Text Color | Badge BG   |
|-----------|-------------|------------|------------|
| Positive  | 4.0 – 5.0  | #065F46    | #D1FAE5    |
| Neutral   | 3.0 – 3.9  | #1D4ED8    | #DBEAFE    |
| Cautious  | 2.0 – 2.9  | #92400E    | #FEF3C7    |
| Negative  | 0 – 1.9    | #991B1B    | #FEE2E2    |
| No Data   | null       | #64748B    | #F1F5F9    |

---

## Status Badge Colors

| Status    | Text Color | Badge BG |
|-----------|------------|----------|
| Active    | #065F46    | #D1FAE5  |
| On Hold   | #92400E    | #FEF3C7  |
| Completed | #374151    | #F1F5F9  |
| Archived  | #9CA3AF    | #F8FAFC  |
| Overdue   | #991B1B    | #FEE2E2  |

---

## Typography

```
Font stack:  -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif

Page greeting:      32px, font-weight: 800, color: #0F172A   (e.g. "Good afternoon, Merlin")
Page subheading:    15px, font-weight: 400, color: #94A3B8   (e.g. "Monday, March 16, 2026")
Section label:      11px, font-weight: 600, color: #94A3B8   UPPERCASE, letter-spacing: 0.08em
                    (e.g. "CLIENTS", "TODAY'S TASKS", "UPCOMING")
Card title:         16px, font-weight: 700, color: #0F172A
Card subtitle:      13px, font-weight: 400, color: #64748B
Body text:          14px, font-weight: 400, color: #0F172A
Meta / timestamps:  12px, font-weight: 400, color: #94A3B8
Badge text:         11px, font-weight: 600, UPPERCASE, letter-spacing: 0.05em
```

---

## Layout Grid

```
Page max-width:     1280px, centered
Page padding:       32px horizontal, 28px vertical
Section gap:        40px between major sections
Card gap:           16px between cards in a grid
Card border-radius: 16px
Card padding:       20px
Card border:        1px solid #E2E8F0
Card shadow:        0 2px 8px rgba(15, 23, 42, 0.06)
Card shadow hover:  0 8px 24px rgba(15, 23, 42, 0.10)
```

---

## Gradient Top Bar

Every page includes a thin rainbow gradient bar at the very top (4px tall):

```html
<div style="
  height: 4px;
  width: 100%;
  background: linear-gradient(90deg,
    #6366F1 0%,
    #8B5CF6 15%,
    #EC4899 30%,
    #F59E0B 50%,
    #10B981 70%,
    #3B82F6 85%,
    #6366F1 100%);
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;">
</div>
```

---

## Page Header Pattern

All dashboard views use a greeting-style header, not a utility bar:

```html
<!-- Top of every page, below the gradient bar -->
<div style="padding: 28px 32px 0;">
  <div style="display:flex; justify-content:space-between; align-items:flex-start;">
    <div>
      <h1 style="font-size:32px; font-weight:800; color:#0F172A; margin:0;">
        [Page Title or "Good [time], [Name]"]
      </h1>
      <p style="font-size:15px; color:#94A3B8; margin:6px 0 0;">
        [Subtitle — e.g. date, last sync time, breadcrumb]
      </p>
    </div>
    <div style="display:flex; gap:8px; padding-top:4px;">
      <!-- Action buttons here -->
    </div>
  </div>
</div>
```

Team dashboard greeting: "Good [morning/afternoon/evening], [first name]"
Client dashboard: "[Client Name]" as title, breadcrumb as subtitle
Project dashboard: "[Project Name]" as title, "Client Name → Project" breadcrumb

---

## Component Patterns

### Badge / Pill

```html
<span style="
  display: inline-flex; align-items: center;
  padding: 3px 10px; border-radius: 9999px;
  font-size: 11px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.05em;
  background: [bg color]; color: [text color];">
  LABEL
</span>
```

### Section Label

```html
<p style="
  font-size: 11px; font-weight: 600; color: #94A3B8;
  text-transform: uppercase; letter-spacing: 0.08em;
  margin: 0 0 14px;">
  SECTION NAME
</p>
```

### Primary Action Button

```html
<button style="
  background: #0F172A; color: #FFFFFF;
  border: none; border-radius: 10px;
  padding: 8px 16px; font-size: 13px;
  font-weight: 600; cursor: pointer;
  font-family: inherit;">
  Action
</button>
```

### Secondary Action Button

```html
<button style="
  background: #FFFFFF; color: #0F172A;
  border: 1px solid #E2E8F0; border-radius: 10px;
  padding: 8px 16px; font-size: 13px;
  font-weight: 500; cursor: pointer;
  font-family: inherit;">
  Action
</button>
```

---

## Client Card (Team Dashboard)

Wide cards in a responsive grid (min 300px, 3 columns at full width).

```html
<div style="
  background: #FFFFFF; border: 1px solid #E2E8F0;
  border-radius: 16px; padding: 20px;
  box-shadow: 0 2px 8px rgba(15,23,42,0.06);">

  <!-- Top row: name + MOI badge -->
  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
    <span style="font-size:16px; font-weight:700; color:#0F172A;">[Client Name]</span>
    <span>[MOI sentiment badge]</span>
  </div>

  <!-- Stats row -->
  <div style="font-size:13px; color:#64748B; margin-bottom:6px;">
    [N] active projects
  </div>
  <div style="font-size:13px; color:#64748B; margin-bottom:16px;">
    Next due: [date] — [task title]
  </div>

  <!-- Divider -->
  <div style="height:1px; background:#F1F5F9; margin-bottom:14px;"></div>

  <!-- Footer row -->
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <div style="display:flex; gap:6px;">
      [Ops badge] [Finance badge] [Marketing badge]  <!-- role badges for active advisors -->
    </div>
    <a style="font-size:13px; font-weight:600; color:#3B82F6; text-decoration:none;">
      Open →
    </a>
  </div>
</div>
```

---

## Project Block (Client Dashboard)

```html
<div style="
  background: #FFFFFF; border: 1px solid #E2E8F0;
  border-radius: 16px; padding: 20px;
  box-shadow: 0 2px 8px rgba(15,23,42,0.06); margin-bottom: 12px;">

  <!-- Header row -->
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
    <div style="display:flex; align-items:center; gap:10px;">
      <span>[Status badge]</span>
      <span style="font-size:16px; font-weight:700; color:#0F172A;">[Project Name]</span>
    </div>
    <span>[Advisor role badge]</span>
  </div>

  <!-- Meta row -->
  <div style="font-size:13px; color:#64748B; margin-bottom:12px;">
    Next due: [date] &nbsp;·&nbsp; [N] / [total] tasks pending
  </div>

  <!-- Task preview list (top 3) -->
  <div style="border-top:1px solid #F1F5F9; padding-top:12px;">
    [task rows — see task row pattern below]
  </div>

  <!-- Footer -->
  <div style="text-align:right; margin-top:14px;">
    <a style="font-size:13px; font-weight:600; color:#3B82F6; text-decoration:none;">
      Open Project →
    </a>
  </div>
</div>
```

---

## MOI Score Chart Section (Client Dashboard)

Placed at the **top of the client page**, above the Advisor Call Summaries section. Three equal-width cards in a row — one per advisor role (Operations, Finance, Marketing).

### Chart Card Structure

```html
<div style="
  background: #FFFFFF; border: 1px solid #E2E8F0;
  border-radius: 16px; padding: 20px;
  box-shadow: 0 2px 8px rgba(15,23,42,0.06);">

  <!-- Card header: advisor role badge + label -->
  <div style="display:flex; align-items:center; gap:8px; margin-bottom:16px;">
    <span style="[role badge style]">[ROLE]</span>
    <span style="font-size:13px; font-weight:600; color:#0F172A;">MOI Score — 12 Weeks</span>
  </div>

  <!-- Chart area: SVG inline -->
  [SVG chart or empty state — see below]

  <!-- Embedded call data for modal (hidden) -->
  <script id="callData-[role]" type="application/json">[JSON array]</script>
</div>
```

### SVG Chart Rendering

Chart dimensions: width=100% (use viewBox), height=185px. Use `viewBox="0 0 400 185"` and `width="100%" height="185"`.

Chart margins: top=10, right=10, bottom=20, left=36 (for y-axis labels).
Plot area: x from 36 to 390, y from 10 to 155.

**Y-axis:** Score range 0.0–6.0. Map score to y-pixel:
```
y = 155 - (score / 6.0) * 145
```
Draw gridlines (stroke: #F1F5F9, stroke-width: 1) and y-labels (10px, #94A3B8) at all integer scores 0, 1, 2, 3, 4, 5, 6.
X-axis date labels at y=175.

**X-axis:** Up to 12 weeks of call dates, spread evenly across plot width (36 to 390).
If N data points: x_i = 36 + (i / (N-1)) * 354 (for N≥2). If N=1, center at x=213.
Draw date labels below x-axis in MM/DD format (11px, #94A3B8), rotated -35deg if crowded (>6 points).

**Line:** `<polyline>` connecting all (x,y) points. stroke = role color (see Advisor Role Colors), stroke-width=2, fill=none.

**Data points:**
```html
<circle cx="[x]" cy="[y]" r="6"
  fill="[role color]" stroke="#FFFFFF" stroke-width="2"
  style="cursor:pointer;"
  onclick="showCallSummary('[role]', '[call_date]')"
  onmouseover="showTooltip(evt, '[MM/DD/YY]: [score]')"
  onmouseout="hideTooltip()">
  <title>[MM/DD/YY] — MOI [score]</title>
</circle>
```

**SVG Tooltip (inline, no CDN):** Include these elements at the top of the SVG and the JS functions at the bottom of the page (once, shared across all charts):

```html
<!-- Tooltip element inside SVG -->
<g id="svg-tooltip" style="display:none; pointer-events:none;">
  <rect rx="6" ry="6" fill="#0F172A" opacity="0.9" height="28"></rect>
  <text fill="#FFFFFF" font-size="12" font-family="-apple-system, sans-serif" dy="18" dx="8"></text>
</g>
```

```js
// Inline JS at bottom of page (once)
function showTooltip(evt, label) {
  const svg = evt.target.closest('svg');
  const tip = svg.querySelector('#svg-tooltip');
  const rect = tip.querySelector('rect');
  const text = tip.querySelector('text');
  text.textContent = label;
  const w = label.length * 7 + 16;
  rect.setAttribute('width', w);
  const pt = svg.createSVGPoint();
  pt.x = evt.clientX; pt.y = evt.clientY;
  const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());
  tip.setAttribute('transform', `translate(${svgP.x - w/2},${svgP.y - 40})`);
  tip.style.display = 'block';
}
function hideTooltip() {
  document.querySelectorAll('#svg-tooltip').forEach(t => t.style.display = 'none');
}
```

### Last Call Summary Block

Rendered inside each chart card, below the SVG (or empty state). Shows the most recent call's summary text, date, and sentiment. Use the last entry in the sorted call data array.

```html
<!-- Last call summary — appended inside chart card, below the SVG -->
<div style="border-top:1px solid #F1F5F9;margin-top:12px;padding-top:10px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
    <span style="font-size:11px;color:#94A3B8;">Last call: [date in Mon D, YYYY format]</span>
    <span style="[sentiment badge style for that call]">[SENTIMENT]</span>
  </div>
  <p style="font-size:12px;color:#64748B;line-height:1.5;margin:0;">[call.summary of most recent entry]</p>
</div>
```

If no call data for this role, omit the last call summary block (empty state already communicates the absence).

### Empty State (no MOI data for that advisor role)

```html
<div style="
  height: 140px; display: flex; align-items: center; justify-content: center;
  background: #F8FAFC; border-radius: 12px;
  color: #94A3B8; font-size: 13px; text-align: center; line-height: 1.6;">
  📞 No call data yet<br>
  <span style="font-size:12px;">Sync Gong to populate</span>
</div>
```

### Call Summary Modal

Triggered by `showCallSummary(role, callDate)`. Include this JS once at the bottom of the client page:

```js
function showCallSummary(role, callDate) {
  const dataEl = document.getElementById('callData-' + role);
  if (!dataEl) return;
  const calls = JSON.parse(dataEl.textContent);
  const call = calls.find(c => c.call_date === callDate);
  if (!call || !call.call_summary_detail) return;
  const d = call.call_summary_detail;

  // Build scorecard rows
  const scorecardRows = (d.moi_scorecard || []).map(r =>
    `<tr>
      <td style="padding:8px 12px;font-size:13px;color:#0F172A;border-bottom:1px solid #F1F5F9;">${r.category}</td>
      <td style="padding:8px 12px;font-size:13px;font-weight:700;color:#3B82F6;border-bottom:1px solid #F1F5F9;text-align:center;">${r.score}</td>
      <td style="padding:8px 12px;font-size:12px;color:#64748B;border-bottom:1px solid #F1F5F9;">${r.rationale}</td>
     </tr>`).join('');

  // Build reflection Q&A
  const reflections = (d.reflection_questions || []).map((q, i) =>
    `<div style="margin-bottom:10px;">
       <div style="font-size:12px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:3px;">Q${i+1}</div>
       <div style="font-size:13px;font-weight:600;color:#0F172A;margin-bottom:3px;">${q.question}</div>
       <div style="font-size:13px;color:#64748B;line-height:1.5;">${q.answer}</div>
     </div>`).join('');

  // Build core value badges
  const coreValues = (d.core_values || []).map(v =>
    `<span style="display:inline-flex;align-items:center;padding:3px 10px;border-radius:9999px;
      font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;
      background:#DBEAFE;color:#1D4ED8;">${v}</span>`).join(' ');

  const overallScore = call.moi_score || '—';
  const dateLabel = new Date(callDate + 'T00:00:00').toLocaleDateString('en-US', {month:'short', day:'numeric', year:'numeric'});

  const modal = document.createElement('div');
  modal.id = 'callSummaryModal';
  modal.style.cssText = 'position:fixed;inset:0;background:rgba(15,23,42,0.6);z-index:1000;display:flex;align-items:center;justify-content:center;padding:24px;';
  modal.innerHTML = `
    <div style="background:#FFFFFF;border-radius:16px;max-width:700px;width:100%;max-height:85vh;overflow-y:auto;box-shadow:0 24px 64px rgba(15,23,42,0.2);">
      <div style="padding:24px 28px;border-bottom:1px solid #E2E8F0;display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
          <div style="font-size:18px;font-weight:700;color:#0F172A;margin-bottom:4px;">Call Summary</div>
          <div style="font-size:13px;color:#94A3B8;">${dateLabel} &nbsp;·&nbsp; Overall MOI: <strong style="color:#3B82F6;">${overallScore}</strong></div>
        </div>
        <button onclick="closeCallSummary()" style="background:none;border:none;font-size:20px;cursor:pointer;color:#94A3B8;padding:0 4px;line-height:1;">×</button>
      </div>
      <div style="padding:24px 28px;">
        <p style="font-size:11px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 8px;">Strategic Summary</p>
        <p style="font-size:13px;color:#64748B;line-height:1.6;margin:0 0 24px;">${d.strategic_summary || ''}</p>
        <p style="font-size:11px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 12px;">MOI Scorecard</p>
        <table style="width:100%;border-collapse:collapse;margin-bottom:24px;">
          <thead>
            <tr>
              <th style="text-align:left;font-size:11px;font-weight:600;color:#94A3B8;padding:6px 12px;text-transform:uppercase;letter-spacing:0.05em;">Category</th>
              <th style="text-align:center;font-size:11px;font-weight:600;color:#94A3B8;padding:6px 12px;text-transform:uppercase;letter-spacing:0.05em;">Score</th>
              <th style="text-align:left;font-size:11px;font-weight:600;color:#94A3B8;padding:6px 12px;text-transform:uppercase;letter-spacing:0.05em;">Rationale</th>
            </tr>
          </thead>
          <tbody>${scorecardRows}</tbody>
        </table>
        <p style="font-size:11px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 12px;">Reflection Questions</p>
        <div style="margin-bottom:24px;">${reflections}</div>
        <p style="font-size:11px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 10px;">Core Values Demonstrated</p>
        <div>${coreValues}</div>
      </div>
    </div>`;
  modal.addEventListener('click', e => { if (e.target === modal) closeCallSummary(); });
  document.body.appendChild(modal);
}

function closeCallSummary() {
  const m = document.getElementById('callSummaryModal');
  if (m) m.remove();
}
```

---

## Advisor Call Summary Panel

Three equal-width panels in a row. Each panel is a white card.

```html
<div style="
  background: #FFFFFF; border: 1px solid #E2E8F0;
  border-radius: 16px; padding: 20px;
  box-shadow: 0 2px 8px rgba(15,23,42,0.06);">

  <!-- Advisor header -->
  <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
    <!-- Colored avatar circle with initials -->
    <div style="
      width:36px; height:36px; border-radius:50%;
      background:[role bg color]; color:[role text color];
      display:flex; align-items:center; justify-content:center;
      font-size:13px; font-weight:700;">
      [Initials]
    </div>
    <div>
      <div style="font-size:14px; font-weight:700; color:#0F172A;">[Advisor Name]</div>
      <div style="font-size:11px; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em;">[Role]</div>
    </div>
  </div>

  <!-- Call date + sentiment -->
  <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
    <span style="font-size:12px; color:#94A3B8;">Last call: [date]</span>
    <span>[Sentiment badge]</span>
  </div>

  <!-- Divider -->
  <div style="height:1px; background:#F1F5F9; margin-bottom:12px;"></div>

  <!-- Summary -->
  <p style="font-size:13px; color:#64748B; line-height:1.6; margin:0 0 12px;">
    [Summary text]
  </p>

  <!-- Topics -->
  <div style="display:flex; gap:6px; flex-wrap:wrap;">
    [topic chips — small gray pills]
  </div>
</div>
```

---

## Task Row (Project Dashboard table)

```html
<div style="
  display:flex; align-items:center; gap:12px;
  padding:10px 0; border-bottom:1px solid #F1F5F9;">

  <!-- Status checkbox area -->
  <div style="width:18px; height:18px; border-radius:5px;
    border:2px solid #E2E8F0; flex-shrink:0;"></div>

  <!-- Task title (flex-grow) -->
  <span style="flex:1; font-size:14px; color:#0F172A;">[Task title]</span>

  <!-- Due date -->
  <span style="font-size:12px; color:#94A3B8; white-space:nowrap;">[Due date]</span>

  <!-- Advisor badge -->
  <span>[role badge]</span>

  <!-- Source -->
  <span style="font-size:11px; color:#94A3B8;">Gong</span>

  <!-- Move action -->
  <a style="font-size:12px; color:#3B82F6; cursor:pointer;">Move</a>
</div>
```

Overdue rows: wrap in `background: #FFF5F5; border-radius: 8px; padding: 10px 8px; margin: 0 -8px;`
Completed rows: `opacity: 0.45; text-decoration: line-through;`

---

## Agent Feed / Notification Panel (right sidebar, team dashboard)

```html
<div style="
  background: #FFFFFF; border: 1px solid #E2E8F0;
  border-radius: 16px; padding: 0; overflow:hidden;
  box-shadow: 0 2px 8px rgba(15,23,42,0.06);">

  <!-- Panel header -->
  <div style="padding:16px 20px; border-bottom:1px solid #F1F5F9;
    display:flex; justify-content:space-between; align-items:center;">
    <span style="font-size:11px; font-weight:600; color:#94A3B8;
      text-transform:uppercase; letter-spacing:0.08em;">FLAGGED ITEMS</span>
  </div>

  <!-- Each item -->
  <div style="padding:14px 20px; border-bottom:1px solid #F1F5F9;">
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
      <!-- Colored dot -->
      <div style="width:8px; height:8px; border-radius:50%; background:#3B82F6;"></div>
      <span style="font-size:12px; color:#94A3B8;">[advisor] · [time ago]</span>
      <!-- Optional IMPORTANT badge -->
      <span style="font-size:10px; font-weight:700; color:#1D4ED8;
        background:#DBEAFE; padding:2px 7px; border-radius:9999px;
        text-transform:uppercase; letter-spacing:0.05em;">IMPORTANT</span>
    </div>
    <div style="font-size:14px; font-weight:600; color:#0F172A; margin-bottom:4px;">
      [Item title]
    </div>
    <div style="font-size:13px; color:#64748B; line-height:1.5;">
      [Description]
    </div>
  </div>
</div>
```

---

## Warning Banner (MOI Error)

```html
<div style="
  background: #FFF5F5; border: 1px solid #FECACA;
  border-radius: 12px; padding: 14px 18px;
  display:flex; align-items:flex-start; gap:10px; margin-bottom: 24px;">
  <span style="font-size:16px;">⚠️</span>
  <div>
    <div style="font-size:13px; font-weight:600; color:#991B1B; margin-bottom:2px;">
      MOI sheet access error
    </div>
    <div style="font-size:13px; color:#B91C1C;">
      Showing last known values as of [date]. Check your email for details.
    </div>
  </div>
</div>
```

---

## Empty States

```html
<div style="
  text-align:center; padding: 40px 20px;
  color:#94A3B8; font-size:14px;">
  <div style="font-size:28px; margin-bottom:12px;">[emoji]</div>
  <div style="font-weight:600; color:#64748B; margin-bottom:6px;">[Primary message]</div>
  <div style="font-size:13px;">[Secondary instruction]</div>
</div>
```

Examples:
- No tasks today: 🎉 "All clear" / "No tasks due today"
- No projects: 📋 "No projects yet" / "Run /sync-gong to pull from Gong calls"
- No calls: 📞 "No calls recorded" / "Sync Gong to populate advisor call summaries"

---

## Spacing Constants

```
Gradient bar height:  4px (fixed, top of page)
Page top padding:     24px (below gradient bar)
Section gap:          40px between major sections
Card gap:             16px between cards in a grid
Inner padding:        20px inside cards
List item gap:        0px (use border-bottom dividers instead)
Divider color:        #F1F5F9 (very subtle)
```

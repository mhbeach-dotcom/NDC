# Nuclear Deterrence and Coercion in a Multipolar Age — Winter 2026/27 course page

Personal study aid for the Naval War College Nuclear Deterrence course, modeled on the Strategy & Policy course page.
`index.html` is a single self-contained file (open it in a browser; no server needed). It is generated and password-protected (StatiCrypt, AES-256) — edit the data, then rebuild.

- **10 lesson cards**: guiding question, required reading (with read-checkboxes saved in your browser) and further reading.
- Course summary, objectives, both assignments (scenario exercise; Nuclear Posture Review), integrity and GAI policy.
- Search, dark mode, "next unread reading" jump, reading-progress counter.

- **Class schedule**: the 10 lessons map to the S&P calendar's Electives/LDPA Days 1–10 (Mondays 1330–1630; Lesson 8 is Wed Jan 20 because of MLK Day), with a next-class countdown.

## Rebuilding
```
NDC_PASSWORD='...' tools/publish.sh
```
This runs `tools/build.py` and encrypts `index.html` in place. The committed `index.html` is the encrypted one; `python3 tools/build.py` alone writes plaintext — don't commit that.

| File | Purpose |
| --- | --- |
| `data/readings.txt` | Lessons and reading lists (`## ` lesson, `Q:` question, `R:` required, `F:` further, `N:` note) |
| `data/course.json` | Title, instructors, class dates (`schedule`), summary, objectives, assignments, policies, optional `links` (`"4.r2": "<Drive URL>"` = lesson 4, required reading 2; `f` for further) |
| `tools/shell.html`, `tools/app.js`, `tools/jmo_base.css`, `tools/extra.css` | Page shell, behavior, styling |

Source: *Nuclear Deterrence Theory Course_26-27.docx*. The official syllabus and Blackboard are authoritative.

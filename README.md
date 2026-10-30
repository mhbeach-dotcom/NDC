# Nuclear Deterrence and Coercion in a Multipolar Age — Winter 2026/27 course page

Personal study aid for the Naval War College Nuclear Deterrence course, modeled on the Strategy & Policy course page.
`index.html` is a single self-contained file (open it in a browser; no server needed). It is generated — edit the data, then rebuild.

- **10 lesson cards**: guiding question, required reading (with read-checkboxes saved in your browser) and further reading.
- Course summary, objectives, both assignments (scenario exercise; Nuclear Posture Review), integrity and GAI policy.
- Search, dark mode, "next unread reading" jump, reading-progress counter.

## Rebuilding
```
python3 tools/build.py
```

| File | Purpose |
| --- | --- |
| `data/readings.txt` | Lessons and reading lists (`## ` lesson, `Q:` question, `R:` required, `F:` further, `N:` note) |
| `data/course.json` | Title, instructors, summary, objectives, assignments, policies, optional `links` (`"4.r2": "<Drive URL>"` = lesson 4, required reading 2; `f` for further) |
| `tools/shell.html`, `tools/app.js`, `tools/jmo_base.css`, `tools/extra.css` | Page shell, behavior, styling |

Source: *Nuclear Deterrence Theory Course_26-27.docx*. The official syllabus and Blackboard are authoritative.

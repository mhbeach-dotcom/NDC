#!/usr/bin/env python3
"""Build index.html (single self-contained file) from data/course.json + data/readings.txt.

Usage:  python3 tools/build.py
"""
import json, hashlib, html, re, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / 'data'
T = ROOT / 'tools'
course = json.load(open(D / 'course.json', encoding='utf-8'))
links = course.get('links', {})   # "lesson.reading" -> URL, e.g. "1.2": "https://drive.google.com/..."

esc = lambda s: html.escape(s, quote=True)
URL = re.compile(r'(https?://[^\s,]+?)(?=[.,;]?(?:\s|$))')
PAGES = re.compile(r'\s*\((\d+) pages?\)\.?\s*(?=$|E-book)')

def parse_readings():
    lessons = []
    for raw in (D / 'readings.txt').read_text(encoding='utf-8').splitlines():
        line = raw.rstrip()
        if not line or (line.startswith('#') and not line.startswith('## ')): continue
        if line.startswith('## '):
            short, full = [x.strip() for x in line[3:].split('|', 1)]
            lessons.append({'short': short, 'full': full, 'q': [], 'lead': [], 'req': [], 'fur': []})
        elif line[:2] in ('Q:', 'L:'):
            lessons[-1]['q' if line[0] == 'Q' else 'lead'].append(line[2:].strip())
        elif line[:2] in ('R:', 'F:'):
            text = line[2:].strip()
            m = PAGES.search(text)
            pages = m.group(1) if m else ''
            if m: text = (text[:m.start()] + text[m.end():]).strip()
            lessons[-1]['req' if line[0] == 'R' else 'fur'].append({'cite': text, 'pages': pages, 'note': ''})
        elif line[:2] == 'N:':
            grp = 'fur' if lessons[-1]['fur'] and lessons[-1]['fur'][-1] is not None and last_kind == 'F' else 'req'
            lessons[-1][grp][-1]['note'] = line[2:].strip()
        if line[:2] in ('R:', 'F:'): last_kind = line[0]
    return lessons

LESSONS = parse_readings()
SCHED = course['schedule']
DAYS = SCHED['days']
assert len(DAYS) == len(LESSONS), 'one class date per lesson'
def fmt(s, wd=True):
    d = datetime.date.fromisoformat(s)
    return (d.strftime('%a ') if wd else '') + d.strftime('%b ') + str(d.day)
def span(): return SCHED['start'].replace(':', '') + '–' + SCHED['end'].replace(':', '')

SVG = {
 'eye': '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
 'cal': '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
 'book': '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/>',
}
def sub(title, icon, body, cls=''):
    return (f'<div class="subsection {cls}"><h4><span class="sec-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{SVG[icon]}</svg></span>{title}</h4>{body}</div>')

def rid(*a): return hashlib.sha1('|'.join(a).encode()).hexdigest()[:8]

def linkify(text):
    out, last = '', 0
    for m in URL.finditer(text):
        out += esc(text[last:m.start()]) + f'<a href="{esc(m.group(1))}" target="_blank" rel="noopener">{esc(m.group(1))}</a>'
        last = m.end()
    return out + esc(text[last:])

def reading_li(n, i, r, required):
    cite = linkify(r['cite'])
    link = links.get(f'{n}.{"r" if required else "f"}{i+1}')
    if link: cite = f'<a href="{esc(link)}" target="_blank" rel="noopener">{cite}</a>'
    pages = f'<span class="cite-pages">{r["pages"]} pp.</span>' if r['pages'] else ''
    note = f'<span class="cite-note">{esc(r["note"])}</span>' if r['note'] else ''
    cls = 'cite-req' if required else 'cite-fur'
    box = (f'<label class="read-toggle"><input type="checkbox" class="read-checkbox" data-read-id="{rid(str(n), cls, r["cite"])}" '
           f'aria-label="Mark as read"></label>')
    return f'<li class="cite {cls}">{box}<span class="cite-text"><span class="plain">{i+1}. {cite}</span>{pages}{note}</span></li>'

def lesson_card(n, L):
    body = f'<div class="card-block-label">{esc(L["full"])}</div>'
    body += sub('Class', 'cal', f'<p>{fmt(DAYS[n-1]["date"])}, {span()}</p><p class="lead-note">{esc(DAYS[n-1]["note"])}</p>')
    if L['q'] or L['lead']:
        txt = ''.join(f'<p>{esc(p)}</p>' for p in L['q'])
        txt += ''.join(f'<p class="lead-note">{esc(p)}</p>' for p in L['lead'])
        body += sub('Guiding question', 'eye', txt, 'span-all')
    req = ''.join(reading_li(n, i, r, True) for i, r in enumerate(L['req']))
    body += sub(f'Required Reading ({len(L["req"])})', 'book', f'<ul class="cite-list">{req}</ul>', 'span-all')
    if L['fur']:
        fur = ''.join(reading_li(n, i, r, False) for i, r in enumerate(L['fur']))
        body += sub(f'Further Reading ({len(L["fur"])})', 'book',
                    f'<details class="more"><summary>Show further readings</summary><ul class="cite-list further">{fur}</ul></details>', 'span-all')
    pages = sum(int(r['pages']) for r in L['req'] if r['pages'])
    when = f'{fmt(DAYS[n-1]["date"])} &middot; {span()}'
    meta = f'{when} &middot; {len(L["req"])} required &middot; {len(L["fur"])} further' + (f' &middot; ~{pages} pp. counted' if pages else '')
    return (f'<details class="session-card" id="card-{n}" data-code="{n}">'
            f'<summary><span class="code">Lesson {n}</span><span class="title-wrap"><span class="title">{esc(L["short"])}</span>'
            f'<span class="card-meta-line">{meta}</span></span>'
            f'<span class="badges"><span class="badge badge-type">Lesson</span></span></summary>'
            f'<div class="card-body">{body}</div></details>')

def lessons_html(): return ''.join(lesson_card(i + 1, L) for i, L in enumerate(LESSONS))

def lesson_index_html():
    rows = ''.join(f'<li><button type="button" data-jump-session="{i+1}"><span class="ci-num">{i+1}</span><span>{esc(L["short"])}</span><span class="ci-dates">{fmt(DAYS[i]["date"], False)}</span></button></li>'
                   for i, L in enumerate(LESSONS))
    return f'<ul class="case-index">{rows}</ul>'

def hero_html():
    profs = ''.join(f'<div>{esc(p["name"])}<span>{esc(p["role"])} &middot; {esc(p["office"])}</span></div>' for p in course['instructors'])
    return (f'<section class="course-hero"><p class="term">{esc(course["term"])} &middot; Pass/Fail</p>'
            f'<h2>{esc(course["title"])}</h2>'
            f'<blockquote>{esc(course["quote"])}<cite>&mdash; {esc(course["quote_by"])}</cite></blockquote>'
            f'<div class="profs">{profs}</div>'
            f'<button type="button" class="next-class" id="nextClass" data-jump-session="1" hidden></button></section>')

def panel(title, body, pid='', open_=False):
    i = f' id="{pid}"' if pid else ''
    return f'<details class="ref-panel"{i}{" open" if open_ else ""}><summary>{title}</summary><div class="ref-body">{body}</div></details>'

def ul(items, tag='ul'): return f'<{tag}>' + ''.join(f'<li>{esc(x)}</li>' for x in items) + f'</{tag}>'

def assignment_html(a):
    b = f'<div class="assign-box"><h5>Assignment {a["n"]}: {esc(a["title"])} ({a["words"]:,} words)</h5><p class="window">{esc(a["window"])}</p>'
    b += ''.join(f'<p>{esc(p)}</p>' for p in a['paras'])
    if a['asks']: b += ul(a['asks'])
    if a['then']: b += f'<p>{esc(a["then"])}</p>' + ul(a['must'], 'ol')
    return b + '</div>'

def schedule_html():
    rows = ''.join(f'<li><span class="lec-when">{fmt(d["date"])}</span> <button type="button" class="lec-jump" data-jump-session="{i+1}">'
                   f'Lesson {i+1}: {esc(LESSONS[i]["short"])}</button> <span class="lec-who">&mdash; {esc(d["note"])}</span></li>'
                   for i, d in enumerate(DAYS))
    return (f'<p>Classes meet {span()}. Week 1 starts {fmt(SCHED["weeks_start"])}. Thanksgiving recess Nov 25&ndash;27; holiday recess Dec 22&ndash;Jan 1.</p>'
            f'<ul class="lec-list">{rows}</ul><p class="cite-note">Dates from the {esc(SCHED["source"])}.</p>')

def reference_html():
    out = '<section class="ref-section" id="reference"><h2>Course Reference</h2>'
    out += panel('Class schedule', schedule_html(), 'schedule', True)
    out += panel('Course summary', ''.join(f'<p>{esc(p)}</p>' for p in course['summary']), open_=True)
    out += panel('Course objectives', '<p>After this course, you should:</p>' + ul(course['objectives']))
    out += panel('Main assignments (2 &times; 2,500 words)', ''.join(assignment_html(a) for a in course['assignments']), 'assignments', True)
    out += panel('Expectations of behavior and effort', f'<p>{esc(course["expectations"])}</p>')
    out += panel('Academic integrity', ''.join(f'<p>{esc(p)}</p>' for p in course['integrity']))
    out += panel('Generative AI (GAI) policy',
                 f'<p>{esc(course["gai_intro"])}</p>' + ul(course['gai_rules'], 'ol') + f'<p>{esc(course["gai_outro"])}</p>')
    return out + '</section>'

css = (T / 'jmo_base.css').read_text(encoding='utf-8') + (T / 'extra.css').read_text(encoding='utf-8')
sessions = [{'n': i + 1, 'start': f'{d["date"]}T{SCHED["start"]}:00', 'end': f'{d["date"]}T{SCHED["end"]}:00'} for i, d in enumerate(DAYS)]
js = (T / 'app.js').read_text(encoding='utf-8').replace('/*SESSIONS*/[]', json.dumps(sessions))
page = ((T / 'shell.html').read_text(encoding='utf-8')
        .replace('{{CSS}}', css).replace('{{JS}}', js).replace('{{LESSON_INDEX}}', lesson_index_html())
        .replace('{{HERO}}', hero_html()).replace('{{REFERENCE}}', reference_html()).replace('{{LESSONS}}', lessons_html()))
(ROOT / 'index.html').write_text(page, encoding='utf-8')
print('wrote index.html', len(page) // 1024, 'KB;', len(LESSONS), 'lessons,',
      sum(len(L['req']) for L in LESSONS), 'required,', sum(len(L['fur']) for L in LESSONS), 'further')

"""seo-advisor requirements: Graphviz (WASM) diagrams + text -> HTML -> PDF (Chrome).

Usage: python build_requirements_pdf.py <folder with dot2svg.mjs and node_modules>
"""
import re
import subprocess
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).parent
GV = Path(sys.argv[1])
OUT_HTML = HERE / "requirements.html"
FONT = "Arial"

STYLE = {
    "start":    dict(shape="box", style="rounded,filled", fillcolor="#e3f4e8", color="#2e7d4f"),
    "step":     dict(shape="box", style="filled", fillcolor="#ffffff", color="#0b2a4a"),
    "human":    dict(shape="box", style="rounded,filled,bold", fillcolor="#fff8e6", color="#8a5a00"),
    "decision": dict(shape="diamond", style="filled", fillcolor="#fff3d6", color="#c77700", margin="0.04"),
    "source":   dict(shape="box", style="filled", fillcolor="#e4eefb", color="#0b5cad"),
    "later":    dict(shape="box", style="filled,dashed", fillcolor="#f2f5f9", color="#7a8899"),
    "gate":     dict(shape="box", style="filled", fillcolor="#fde7e7", color="#b42318"),
    "gatedec":  dict(shape="diamond", style="filled", fillcolor="#fde7e7", color="#b42318", margin="0.04"),
    "stop":     dict(shape="box", style="rounded,filled", fillcolor="#fde7e7", color="#b42318"),
    "store":    dict(shape="cylinder", style="filled", fillcolor="#efe7fb", color="#6941c6"),
    "ext":      dict(shape="box", style="filled", fillcolor="#e6f6f4", color="#0f766e"),
    "page":     dict(shape="note", style="filled", fillcolor="#ffffff", color="#475467"),
    "state":    dict(shape="box", style="rounded,filled", fillcolor="#ffffff", color="#344054"),
}
YESNO = {"Yes": "#2e7d4f", "Pass": "#2e7d4f", "No": "#b42318", "Fail": "#b42318"}


def label(title, detail=""):
    t = "<BR/>".join(f"<B>{escape(x)}</B>" for x in title.split("\n"))
    rows = f"<TR><TD>{t}</TD></TR>"
    if detail:
        d = "<BR/>".join(escape(x) for x in detail.split("\n"))
        rows += f'<TR><TD><FONT POINT-SIZE="10" COLOR="#4a5565">{d}</FONT></TD></TR>'
    return f'<<TABLE BORDER="0" CELLSPACING="0" CELLPADDING="1">{rows}</TABLE>>'


def n(id_, kind, title, detail="", **extra):
    a = " ".join(f'{k}="{v}"' for k, v in {**STYLE[kind], **extra}.items())
    return f"  {id_} [label={label(title, detail)} {a} penwidth=1.7];"


def tbl(id_, name, cols, color="#0b2a4a", bg="#eef2f7"):
    rows = "".join(f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10">{escape(c)}</FONT></TD></TR>' for c in cols)
    lab = (f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" COLOR="{color}">'
           f'<TR><TD BGCOLOR="{bg}"><B>{escape(name)}</B></TD></TR>{rows}</TABLE>>')
    return f'  {id_} [shape=plain label={lab}];'


def e(a, b, lab="", **extra):
    parts = [f'{k}="{v}"' for k, v in extra.items()]
    if lab:
        parts += [f"label=<<B> {escape(lab)} </B>>", f'fontcolor="{YESNO.get(lab, "#3b4654")}"']
    return f"  {a} -> {b} [{' '.join(parts)}];"


def same(*ids):
    return "  { rank=same; " + "; ".join(ids) + "; }"


def cluster(name, title, body, color="#9fb3c8", bg="#f7f9fb"):
    return [f"  subgraph cluster_{name} {{", f'    label=<<B>{escape(title)}</B>> fontsize=11 fontcolor="#3b4654" labeljust=l',
            f'    style="rounded,dashed" color="{color}" bgcolor="{bg}" margin=10', *body, "  }"]


def graph(body, rankdir="TB", nodesep=0.35, ranksep=0.4):
    return f'''digraph G {{
  graph [rankdir={rankdir} fontname="{FONT}" nodesep={nodesep} ranksep={ranksep} splines=spline bgcolor="transparent"
         pad=0.15 newrank=true compound=true];
  node  [fontname="{FONT}" fontsize=12 margin="0.14,0.07"];
  edge  [fontname="{FONT}" fontsize=11 color="#5a6675" penwidth=1.4 arrowsize=0.75];
''' + "\n".join(body) + "\n}\n"


D = {}

# Architecture (layers) ---------------------------------------------------------------------
D["arch"] = graph([
    *cluster("people", "People", [
        n("U1", "human", "Gurzu SEO team", "pastes a URL, reviews\nfindings and suggestions"),
        n("U2", "human", "Client team", "MyPipit: copies approved\ntext into its editor, saves"),
        n("U3", "later", "Expert reviewer (health)", "extendmy.life, Phase 5"),
    ], color="#c9a96b", bg="#fffaf0"),
    *cluster("clients", "Interfaces", [
        n("WEB", "step", "Web app", "React + TypeScript:\nanalyse a page, findings,\nsuggestions"),
        n("EXT", "later", "Chrome extension (Phase 4)", "fills the site editor\nwhen a person accepts"),
    ]),
    *cluster("core", "seo-advisor service (Python, FastAPI)", [
        n("API", "step", "API", "sites, pages, audit runs,\nsuggestions, reviews"),
        n("FP", "step", "Fetch one page", "safe fetcher: SSRF guard,\nrobots.txt, rate limit"),
        n("EX", "step", "Extract", "title, meta, headings,\nimages, links, structured\ndata, main text"),
        n("AU", "step", "Audit rules", "rules per page type,\nevidence and source"),
        n("DR", "step", "Suggest (DeepSeek)", "fixes with [ADD: ...],\na person reviews"),
        n("CK", "gate", "Checks", "no invented facts,\nno copied text"),
        n("CR", "later", "Crawler (Phase 3)", "all pages of a site"),
        n("WF", "later", "Schedules (Phase 3)", "DBOS: daily, weekly,\nmonthly runs"),
        n("RP", "later", "Reports (Phase 6)", "outcomes, weekly report"),
        "    API -> AU [style=invis]; FP -> DR [style=invis]; EX -> CK [style=invis];",
        "    AU -> CR [style=invis]; DR -> WF [style=invis]; CK -> RP [style=invis];",
    ], color="#6941c6", bg="#faf8ff"),
    n("DB", "store", "PostgreSQL 18", "sites, pages, snapshots,\naudit runs, findings,\nsuggestions, AI call log"),
    *cluster("data", "Data sources (read-only)", [
        n("S1", "page", "One client page", "a MyPipit blog post\n(the URL that a person gives)"),
        n("S5", "source", "AI model", "DeepSeek writes\nsuggestions"),
        n("S2", "later", "Later sources", "Search Console (Phase 3),\nCrUX, Bing Webmaster"),
    ], color="#0b5cad", bg="#f4f8fe"),
    e("U1", "WEB"), e("U2", "WEB"), e("U2", "EXT", style="dashed"), e("U3", "WEB", style="dashed"),
    e("WEB", "API", lhead="cluster_core"), e("EXT", "API", lhead="cluster_core", style="dashed"),
    e("CK", "DB", ltail="cluster_core"), e("DB", "S2", lhead="cluster_data", style="invis"),
    e("FP", "S1", ltail="cluster_core", lhead="cluster_data", label="read only"),
    same("U1", "U2", "U3"), same("WEB", "EXT"), same("API", "FP", "EX"), same("AU", "DR", "CK"), same("CR", "WF", "RP"),
    same("S1", "S5", "S2"),
], nodesep=0.3, ranksep=0.45)

# Data model (grid, header colour = group) -------------------------------------------------
TEN, INV, AUD, OPS = ("#344054", "#e4e7ec"), ("#0b2a4a", "#dbe7f5"), ("#b42318", "#fbe1de"), ("#6941c6", "#ece4fb")
CON = ("#2e7d4f", "#dcf2e3")
LATER = ("#7a8899", "#f2f5f9")
D["datamodel"] = graph([
    tbl("T1", "tenants", ["id (uuidv7)", "name"], *TEN),
    tbl("T3", "sites", ["id", "tenant_id", "base_url", "language", "page_types (rules)"], *TEN),
    tbl("I1", "pages", ["id", "site_id", "url", "page_type", "(only pages that a", "person analyses)"], *INV),
    tbl("I2", "page_snapshots", ["page_id, fetched_at", "http_status, final_url", "html (size limit)", "html_hash", "extracted (JSONB)"], *INV),
    tbl("A1", "audit_runs", ["id", "page_id, snapshot_id", "keyword", "rules_version", "started, finished"], *AUD),
    tbl("A2", "findings", ["run_id", "rule_id, severity", "evidence: found,", "expected, selector", "source, status"], *AUD),
    tbl("C1", "suggestions", ["run_id, finding_id", "field, text", "status (accepted,", "edited, rejected)"], *CON),
    tbl("O2", "llm_calls", ["model", "prompt_version", "tokens, cost"], *OPS),
    tbl("L1", "later (Phase 3 to 6)", ["users, schedules", "keywords, gsc_rows", "keyword_page_map", "content_items,", "content_versions,", "content_state_events,", "reviews, outcomes"], *LATER),
    e("T1", "T3", arrowhead="crow"), e("T3", "I1", arrowhead="crow"), e("I1", "I2", arrowhead="crow"),
    e("I1", "A1", arrowhead="crow"), e("I2", "A1", arrowhead="crow"), e("A1", "A2", arrowhead="crow"),
    e("A1", "C1", arrowhead="crow"), e("A2", "C1", arrowhead="crow", style="dashed"), e("C1", "O2", arrowhead="crow", style="dashed"),
    same("T1", "T3", "L1"), same("I1", "I2"), same("A1", "A2"), same("C1", "O2"),
], nodesep=0.45, ranksep=0.5)

# Flow A: analyse one page ------------------------------------------------------------------
D["onboard"] = graph([
    n("S", "start", "1. Paste a URL and a keyword", "for example a MyPipit blog post\nand \"Annapurna base camp trek\""),
    n("G", "decision", "On a registered\nsite?"),
    n("NO", "stop", "Refuse", "the tool reads only\nregistered sites"),
    n("F", "step", "2. Fetch one page", "safe fetcher: robots.txt,\nrate limit, SSRF guard; snapshot"),
    n("X", "step", "3. Extract the SEO content", "title, meta, headings, images,\nlinks, structured data, text"),
    n("A", "step", "4. Audit with rules", "each finding: evidence and\nsource; \"unknown\" if not seen"),
    n("SG", "step", "5. AI suggestions (DeepSeek)", "facts only from the page,\nother facts [ADD: ...]"),
    n("CK", "gatedec", "Checks\npass?"),
    n("RW", "step", "Rewrite once", "then fail"),
    n("R", "human", "6. A person reviews", "accept, edit or reject; copy into\nthe site editor and save there.\nThe tool never publishes."),
    n("RC", "start", "7. Check the page again", "new snapshot and audit run,\ncompared with the last run"),
    e("S", "G"), e("G", "NO", "No"), e("G", "F", "Yes"), e("F", "X"), e("X", "A"), e("A", "SG"), e("SG", "CK"),
    e("CK", "RW", "No"), e("RW", "CK"), e("CK", "R", "Yes"), e("R", "RC"),
    e("RC", "A", "next round", style="dashed", constraint="false"),
    same("G", "NO"), same("CK", "RW"),
], nodesep=0.5, ranksep=0.3)

# Flow B: check the page again (now); scheduled audits (Phase 3) -----------------------------
D["schedule"] = graph([
    n("T", "human", "A person asks for a new check", "after the client saved a change"),
    n("F", "step", "Fetch the page again", "new snapshot (same safe fetcher)"),
    n("A", "step", "Audit again", "same rules version, same keyword"),
    n("DF", "step", "Compare with the last run", "new, fixed and returning findings"),
    n("Q", "decision", "All findings\nfixed?"),
    n("OK", "start", "Mark the page as done", "keep both runs as history"),
    n("BK", "step", "Back to suggestions", "for the open findings"),
    n("LT", "later", "Phase 3: scheduled audits", "DBOS runs daily, weekly and\nmonthly for the whole site"),
    e("T", "F"), e("F", "A"), e("A", "DF"), e("DF", "Q"), e("Q", "OK", "Yes"), e("Q", "BK", "No"),
    e("LT", "F", "later", style="dashed"),
    same("T", "LT"), same("OK", "BK"),
], nodesep=0.5, ranksep=0.4)

# Flow C: from finding to fix ----------------------------------------------------------------
D["content"] = graph([
    n("F", "start", "Finding on the page", "from the audit run"),
    n("T", "decision", "Template or\nthis page?"),
    n("TF", "page", "Template fix request", "to the site's developers\n(fixes all pages of a type)"),
    n("DR", "step", "AI suggestion (DeepSeek)", "title, meta description, H1,\nalt text, content notes"),
    n("CK", "gatedec", "Checks\npass?"),
    n("RW", "step", "Rewrite once", "or mark the sentence"),
    n("R1", "human", "Gurzu review", "accept, edit or reject;\nnot the author"),
    n("Y", "later", "Expert or native review", "health (YMYL) or German:\nextendmy.life, Phase 5"),
    n("AP", "human", "Copy into the site editor", "a person saves;\nextension in Phase 4"),
    n("V", "step", "Check the page again", "Flow B"),
    n("M", "later", "Measure (Phase 6)", "Search Console after\n4, 8 and 12 weeks"),
    e("F", "T"), e("T", "TF", "template"), e("T", "DR", "page"), e("DR", "CK"),
    e("CK", "RW", "No"), e("RW", "CK"), e("CK", "R1", "Yes"), e("R1", "AP"),
    e("R1", "Y", "later", style="dashed"), e("Y", "AP", style="dashed"), e("AP", "V"), e("V", "M", style="dashed"),
    e("R1", "DR", "changes", style="dashed", constraint="false"),
    same("T", "TF"), same("CK", "RW"), same("R1", "Y"),
], nodesep=0.45, ranksep=0.34)

# Workflow states ----------------------------------------------------------------------------
D["states"] = graph([
    n("S1", "state", "Suggested", "created by the engine"),
    n("S2", "state", "Draft", "a person edits"),
    n("S3", "state", "In review (2i)", "Gurzu, second person"),
    n("S4", "state", "Expert review", "YMYL or German only"),
    n("S5", "state", "Client review"),
    n("S6", "state", "Approved"),
    n("S7", "state", "Applied", "a person saved it\nin the site editor"),
    n("S8", "start", "Live (verified)", "crawl confirms the change"),
    n("S9", "state", "Needs review", "audit finding or\nreview date reached"),
    n("SX", "stop", "Rejected"),
    n("SA", "later", "Archived"),
    e("S1", "S2", "accept"), e("S1", "SX", "dismiss"), e("S2", "S3", "submit"), e("S3", "S4", "YMYL/DE"),
    e("S3", "S5", "other"), e("S4", "S5"), e("S5", "S6", "approve"), e("S6", "S7", "apply"), e("S7", "S8", "crawl ok"),
    e("S3", "S2", "changes", style="dashed"), e("S5", "S2", "changes", style="dashed"),
    e("S8", "S9", "later", style="dashed"), e("S9", "S2", "edit", style="dashed"), e("S8", "SA", style="dashed"),
    same("S1", "SX"), same("S4", "S5"),
], nodesep=0.45, ranksep=0.42)

# Roadmap ------------------------------------------------------------------------------------
D["roadmap"] = graph([
    n("P0", "start", "Phase 0: set up the repo", "0.1 to 0.3 done; other steps\nstart when a slice needs them"),
    n("P1", "step", "Phase 1: one page, end to end", "MyPipit blog post: fetch, extract,\naudit with evidence, DeepSeek\nsuggestions, review (slices 1 to 5)"),
    n("G1", "gatedec", "90% of findings\ncorrect, 7 of 10\naccepted?"),
    n("P2", "step", "Phase 2: more page types", "listings, categories and\nstatic pages on MyPipit"),
    n("P3", "step", "Phase 3: whole site", "crawler, schedules, Search Console,\ncontent workflow, work queue"),
    n("G3", "gatedec", "Runs work for\n2 weeks?"),
    n("P4", "step", "Phase 4: extension", "fills the site editor;\na person saves"),
    n("P5", "step", "Phase 5: second site and languages", "test site extendmy.life: EN + DE,\nhreflang, native review, health rule"),
    n("P6", "step", "Phase 6: measure and report", "outcomes, reports, alerts"),
    n("PL", "later", "Later", "deployment with DevOps,\nmore sites, paid data"),
    n("FX", "step", "Fix rules and prompts"),
    e("P0", "P1"), e("P1", "G1"), e("G1", "P2", "Yes"), e("G1", "FX", "No"), e("FX", "P1"),
    e("P2", "P3"), e("P3", "G3"), e("G3", "P4", "Yes"), e("G3", "FX", "No"), e("P4", "P5"), e("P5", "P6"),
    e("P6", "PL", style="dashed"),
    same("G1", "FX"),
], nodesep=0.5, ranksep=0.3)

D["setup"] = graph([
    n("A", "start", "0.1 Machine", "mise, Docker, gh, Claude Code"),
    n("B", "step", "0.2 Repo skeleton", "folders, README, mise.toml,\n.env.example, NOTICE"),
    *cluster("base", "Code bases (in parallel)", [
        n("C1", "step", "0.3 Python", "uv, ruff, mypy, pytest,\nSettings"),
        n("C2", "store", "0.4 Database", "Compose, Alembic,\nfirst migration, fixtures"),
        n("C3", "step", "0.5 API", "FastAPI, errors, request ID,\nlogs, client generation"),
        n("C4", "step", "0.6 Web + extension", "Vite, TanStack, shadcn/ui,\noxlint, Vitest, WXT"),
    ]),
    n("D", "gate", "0.7 Hooks", "prek: hygiene, gitleaks,\nformat, lint"),
    n("E", "gate", "0.8 CI and GitHub", "required check, ruleset,\nDependabot, PR template"),
    n("F", "ext", "0.9 Claude Code", "CLAUDE.md, deny rules,\nhooks, skills, reviewer"),
    n("G", "page", "0.10 ADRs and diagrams", "8 to 10 ADRs, C4 level 1 and 2"),
    n("H", "gate", "0.11 Security and AI base", "SSRF guard, AI layer,\nrecorded fixtures, 20 evals"),
    n("Q", "gatedec", "0.12 Fresh clone\ncheck passes?"),
    n("X", "step", "Fix the setup"),
    n("Z", "start", "Start Phase 1", "feature work"),
    e("A", "B"), e("B", "C2", lhead="cluster_base"), e("C3", "D", ltail="cluster_base"), e("D", "E"), e("E", "F"), e("F", "G"), e("G", "H"),
    e("H", "Q"), e("Q", "Z", "Yes"), e("Q", "X", "No"), e("X", "Q"),
    same("C1", "C2", "C3", "C4"), same("Q", "X"),
], nodesep=0.35, ranksep=0.34)

D["method"] = graph([
    "  graph [layout=circo mindist=0.6];",
    n("Q", "human", "Choose one small part", "the next useful step,\nnot a whole phase"),
    n("R1", "source", "1. Research", "read the cited source,\nask Claude to explain,\nwrite the question"),
    n("E1", "later", "2. Experiment", "throwaway spike\nin experiments/"),
    n("I1", "step", "3. Implement", "small PR with tests,\nonly what the spike proved"),
    n("U1", "human", "4. Understand", "Claude walks through the code,\nshort note in docs/notes/"),
    n("UP", "page", "5. Review the plan", "strategy changed? Update PLAN.md,\nthis PDF and an ADR"),
    e("Q", "R1"), e("R1", "E1"), e("E1", "I1", "works"), e("I1", "U1"), e("U1", "UP"), e("UP", "Q"),
    e("E1", "R1", "does not work", style="dashed", color="#b42318"),
], nodesep=0.4, ranksep=0.4)

D["modules"] = graph([
    n("MAIN", "start", "main.py", "builds the app,\nmounts feature routers"),
    *cluster("feat", "features/ (each folder: api, service, schemas, models, repository, workflows)", [
        n("F1", "step", "sites", "tenants, sites"), n("F2", "step", "inventory", "sitemap list,\nfetch one page"),
        n("F3", "step", "audits", "rules, runs,\nfindings"), n("F6", "step", "drafts", "AI suggestions\n(DeepSeek)"),
        n("F4", "later", "search_data", "Phase 3"), n("F5", "later", "content", "Phase 3"), n("F7", "later", "reports", "Phase 6"),
    ], color="#2e7d4f", bg="#f3fbf5"),
    n("CORE", "store", "core/", "config, db, ids, tenancy,\nlogging, errors"),
    n("INT", "source", "integrations/", "http fetch + SSRF guard,\nLLM (DeepSeek); Search\nConsole, CrUX later"),
    e("MAIN", "F3", lhead="cluster_feat"),
    e("F3", "F2", label="service.py", style="dashed", color="#2e7d4f", constraint="false"),
    e("F6", "F3", label="service.py", style="dashed", color="#2e7d4f", constraint="false"),
    e("F3", "CORE", ltail="cluster_feat"), e("F3", "INT", ltail="cluster_feat"),
    e("INT", "CORE"),
    same("F1", "F2", "F3", "F6", "F4", "F5", "F7"), same("CORE", "INT"),
], nodesep=0.3, ranksep=0.6)

D["legend"] = graph([
    n("l1", "start", "Start or end"), n("l2", "step", "Platform step"), n("l3", "human", "A person acts"),
    n("l4", "decision", "Decision"), n("l5", "source", "Data source"), n("l6", "ext", "Extension"),
    n("l7", "gate", "Check or stop"), n("l8", "store", "Database"), n("l9", "page", "Web page or file"),
    n("l10", "later", "Later or optional"),
    same("l1", "l2", "l3", "l4", "l5"), same("l6", "l7", "l8", "l9", "l10"), "  l1 -> l6 [style=invis];",
], nodesep=0.22, ranksep=0.25)

for name, dot in D.items():
    (HERE / f"{name}.dot").write_text(dot, encoding="utf-8")
subprocess.run(["node", str(GV / "dot2svg.mjs"), *[str(HERE / f"{k}.dot") for k in D]], check=True, cwd=GV,
               stdout=subprocess.DEVNULL)


def svg(name, max_h="225mm"):
    s = (HERE / f"{name}.svg").read_text(encoding="utf-8")
    s = s[s.index("<svg"):]
    w_pt = float(re.match(r'<svg width="([\d.]+)pt"', s).group(1))
    s = re.sub(r'<svg width="[^"]+" height="[^"]+"', "<svg", s, count=1)
    return f'<div class="diagram" style="--w:{w_pt * 0.3528:.1f}mm; --mh:{max_h}">{s}</div>'


CSS = """
@page { size: A4; margin: 13mm 14mm 15mm 14mm; }
* { box-sizing: border-box; }
body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 9.2pt; line-height: 1.42; color: #1a1d23; margin: 0; }
h1 { font-size: 15.5pt; color: #0b2a4a; margin: 0 0 6px; border-bottom: 2px solid #0b2a4a; padding-bottom: 4px; }
h2 { font-size: 11.2pt; color: #0b2a4a; margin: 10px 0 5px; }
p { margin: 3px 0 7px; } ul, ol { margin: 3px 0 8px; padding-left: 20px; } li { margin: 1.5px 0; }
.page { break-after: page; } .page:last-child { break-after: auto; }
.kicker { color: #0b5cad; font-size: 9pt; letter-spacing: 2px; text-transform: uppercase; }
.lead { color: #3b4654; margin-bottom: 8px; }
table { border-collapse: collapse; width: 100%; font-size: 8.1pt; line-height: 1.32; margin: 4px 0 9px; }
th { background: #0b2a4a; color: #fff; text-align: left; padding: 4px 6px; border: 1px solid #0b2a4a; }
td { padding: 3.5px 6px; border: 1px solid #c9d3df; vertical-align: top; overflow-wrap: break-word; }
tr { break-inside: avoid; } tr:nth-child(even) td { background: #f7f9fb; }
.diagram { display: flex; justify-content: center; margin: 6px 0; }
.diagram svg { width: min(var(--w), 100%); height: auto; max-height: var(--mh); }
.note { border-left: 3px solid #0b5cad; background: #eef4fb; padding: 5px 9px; margin: 7px 0; font-size: 8.7pt; }
.caution { border-left: 3px solid #c77700; background: #fff6e8; padding: 5px 9px; margin: 7px 0; font-size: 8.7pt; }
.warning { border-left: 3px solid #b42318; background: #fdecec; padding: 5px 9px; margin: 7px 0; font-size: 8.7pt; }
.cover { padding-top: 18mm; } .cover h1 { font-size: 25pt; border: 0; margin: 6px 0 8px; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 7.8pt; background: #eef2f7; padding: 0 3px; }
.small table { font-size: 7.5pt; } .small td { padding: 3px 5px; }
.tag { display: inline-block; padding: 0 5px; border-radius: 3px; font-size: 7.6pt; font-weight: bold; }
.g { background: #e3f4e8; color: #1e5b39; } .v { background: #fde7e7; color: #8a1c13; } .i { background: #eef2f7; color: #344054; }
"""


def page(title, body, lead=""):
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    return f'<section class="page"><h1>{title}</h1>{lead_html}{body}</section>'


def table(headers, rows, widths=None):
    th = "".join(f'<th style="width:{w}">{h}</th>' if w else f"<th>{h}</th>"
                 for h, w in zip(headers, widths or [None] * len(headers)))
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><tr>{th}</tr>{trs}</table>"


G, V, I = '<span class="tag g">Chosen</span>', '<span class="tag v">Rejected</span>', '<span class="tag i">Later</span>'
P = []

P.append(f"""<section class="page cover">
<div class="kicker">Gurzu · seo-advisor · Requirements</div>
<h1>seo-advisor:<br>requirements and architecture</h1>
<p class="lead">This document gives the requirements, the architecture and the start plan for <b>seo-advisor</b>, a platform that audits, improves and manages the SEO content of several websites. It starts with <b>one page</b>: a person gives the URL of one page and a keyword, and the tool does SEO on that page. The whole site comes later. Two example sites, MyPipit and extendmy.life, are used to test it. The tool is general and is not shaped around these two sites. Read this document before you write code. The short work plan for Claude Code is <code>PLAN.md</code> at the repo root, next to <code>CLAUDE.md</code>. This PDF holds the same plan with reasons and diagrams.</p>
{table(["Item", "Value"], [
 ["Date", "5 October 2026. Revised 8 October 2026 (single page first)."],
 ["Status", "Draft for review. Built: the safe fetcher, the MyPipit sitemap list, the tables tenants and sites, the API and the web app. Next: Phase 1, slice 2 (fetch one MyPipit blog post and extract its SEO content). No change to the client sites. The plan is the current direction and can change."],
 ["Repository", "<code>seo-advisor</code> (new repository). It reuses tested parts of the SEOAdvisor prototype."],
 ["Example sites", "Test cases, not targets: MyPipit (<code>marketplace.mypipit.com</code>, travel, English, 58 URLs on 7 October 2026) first, blog posts first. extendmy.life (<code>extendmy.life</code>, longevity and health, English and German, about 474 URLs) later."],
 ["Decisions so far", "Single page first, then the whole site (8 Oct 2026). AI suggestions with DeepSeek. Read-only access to the sites. Gurzu SEO team reviews first, then the client approves. A person saves every change. Drafts in German need native review. Health-content review rule: decide before extendmy.life drafts start."],
 ["Evidence", "Google Search Central, Search Quality Rater Guidelines (11 Sep 2025), PostgreSQL, SQLite, DBOS, AWS and Microsoft architecture guidance, schema.org, web.dev, GOV.UK, RFC 9309, OWASP, NIST, DORA, GitHub, Anthropic. See sections 24 and 25."],
], ["22%", None])}
<h2>How to read the diagrams</h2>
{svg("legend", "34mm")}
</section>""")

P.append(page("1. Summary", f"""
<h2>What we build</h2>
<p>seo-advisor is one platform for many sites. It starts with one page. A person gives the URL of a page on a registered site and a target keyword. The tool fetches that page, extracts its SEO content and audits it. Each finding shows its evidence and its source. Then an AI suggests fixes, and a person reviews each suggestion. Later the tool scales to the whole site: an inventory of all pages, scheduled audits, a work queue, and results measured in Search Console.</p>
<h2>Main decisions</h2>
{table(["Topic", "Decision", "Reason"], [
 ["Scope", "Single page first. The person pastes a URL of a registered site and types a keyword. The sitemap list is only a page picker. The whole site comes in Phase 3.", "Owner decision (8 Oct 2026): do SEO on one page before the whole site."],
 ["Access to client sites", "Read-only. A person copies approved text into the site editor and saves. An extension fills the editor in Phase 4.", "No client code change needed. People stay in control."],
 ["AI provider", "DeepSeek writes suggestions. A person reviews each one.", "Owner decision (8 Oct 2026). The AI only writes text. Code counts and scores."],
 ["Database", "PostgreSQL 18 with pgvector", "Many writers at the same time (scheduler, workers, API). SQLite allows one writer (S20)."],
 ["Jobs and schedules", "On request in Phase 1. DBOS on the same PostgreSQL from Phase 3.", "Durable steps, schedules per site, retries, no extra server (S22)."],
 ["Tenancy", "One shared schema with tenant_id and site_id on every row", "Lowest cost and effort. Add row-level security when outside customers arrive (S23, S24)."],
 ["Fetching", "Plain HTTP (httpx) through the safe fetcher, one page at a time. A full crawl in Phase 3.", "Both sites send full content in the first HTML response (observed 5 Oct 2026)."],
 ["Reviews", "Gurzu second-person review (2i), then client approval. Expert review for health and native review for German.", "Google: health content must be accurate and written or reviewed by an expert (S2, S3)."],
 ["Tools and setup", "uv, pnpm, mise, Docker Compose, strict automatic checks, light process rules", "One setup command. New engineers can start fast (sections 15 to 19)."],
], ["18%", "44%", "38%"])}
<h2>How to begin</h2>
<ol><li>Read this document and <code>PLAN.md</code>. Agree on the open questions in section 23.</li>
<li>Setup steps 0.1 to 0.3 are done. The other setup steps start when a slice needs them (sections 16 to 18).</li>
<li>Build the page loop for one MyPipit blog post: fetch and extract (slice 2), audit (slice 3), AI suggestions (slice 4). In each slice, build the backend first, then its screen. Do not build AI suggestions before the audit results are correct.</li></ol>
<div class="warning">WARNING: Do not publish AI-written health content without an expert review. Google's rater guidelines rate an AI-written medical article made at scale as "Lowest: Scaled content abuse" (S1).</div>
"""))

P.append(page("How we work: research, experiment, implement", svg("method", "125mm") + table(
    ["Rule", "What it means"],
    [["Start small", "Build one small part at a time. Make it bigger later. Do not implement a whole phase at once."],
     ["Research first", "Read the source that the task names. Ask Claude Code to explain it. Write down the question that the part must answer."],
     ["Experiment before code", "Make a small throwaway test in the experiments folder. Keep what works. Write down what does not work."],
     ["Implement only what is proved", "Make a small pull request with tests. It contains only what the experiment proved."],
     ["Understand before you continue", "Ask Claude Code to walk through the new code until you can explain it yourself. Write a short note in docs/notes. Then choose the next part."],
     ["A general tool", "MyPipit and extendmy.life are example sites for tests. Do not shape the design around them."],
     ["The plan can change", "The phases are the current direction, not a contract. When a strategy changes, update PLAN.md, this PDF and an ADR. Strike out the replaced tasks and give the reason in one line."]],
    ["26%", "74%"]),
    "This project follows a cycle of research, experiment and implementation. Each small part goes through the cycle before the next part starts."))

P.append(page("2. The two sites today", table(
    ["Check", "MyPipit (marketplace.mypipit.com)", "extendmy.life"],
    [["Type", "Travel marketplace (treks, hotels, guides)", "Longevity and health marketplace (clinics, retreats, articles). YMYL topic (S1)."],
     ["Size", "58 URLs on 7 October 2026: 30 blog posts, 17 listings, 11 other pages (53 URLs on 2 October)", "About 474 URLs: 82 articles, 125 clinic pages, 3 categories, 11 subcategories, 13 groupings, 3 static pages, each in EN and DE"],
     ["Technology", "Rails, server-rendered pages", "Next.js, server-rendered pages"],
     ["Languages", "English", "English and German with reciprocal hreflang (en, de, x-default) on inner pages"],
     ["Good base", "Canonical, meta description, Open Graph, sitemap, BlogPosting data", "Canonical, good titles on articles and clinics, alt text on images, robots.txt with sitemap"],
     ["Main issues", "Titles without the searched trek name; image links expire after 1 hour; 41 of 88 images without alt text; no robots.txt", "Same meta description on all category pages; subcategory pages repeat the parent H1; articles have empty author and no dates in structured data; all sitemap lastmod values are the build time; home page has no canonical or hreflang; x-default redirects (307)"],
     ["Content editor", "Rails agency dashboard (Lexxy rich text)", "Not known yet (question in section 23)"],
     ["Search Console", "MyPipit team has access", "Not confirmed"],
     ["Order", "First. Blog posts first, one page at a time.", "Later (Phase 5)."]],
    ["14%", "40%", "46%"]), "Facts from the public pages, read with GET requests only, on 2, 5 and 7 October 2026."))

P.append(page("3. Requirements", table(
    ["ID", "Requirement", "Priority"],
    [["FR-1", "Register a site: base URL, language, page-type rules.", "Must"],
     ["FR-2", "A person gives one page URL and a target keyword. The tool accepts only URLs on a registered site.", "Must"],
     ["FR-3", "Fetch that one page read-only through the safe fetcher (SSRF guard, robots.txt, rate limit). Keep a snapshot.", "Must"],
     ["FR-4", "Extract the SEO content: title, meta description, canonical, meta robots, lang, H1 to H6, images and alt text, links and anchor text, Open Graph, structured data, main text and word count.", "Must"],
     ["FR-5", "Audit the page with the rules for its page type (blog posts first). Each finding has severity, evidence (found, expected, where) and a source. A check that cannot see its data says \"unknown\", not pass.", "Must"],
     ["FR-6", "Check the page again after a change. Compare with the last run: new, fixed and returning findings.", "Must"],
     ["FR-7", "AI suggestions for the title, meta description, H1, alt text and content notes. Facts only from the page; other facts are [ADD: ...].", "Should (slice 4)"],
     ["FR-8", "Checks on every suggestion: no invented numbers or names, no copied text.", "Must (with FR-7)"],
     ["FR-9", "A person accepts, edits or rejects each suggestion and copies it into the site editor. The tool never publishes.", "Must (with FR-7)"],
     ["FR-10", "Sitemap list as a page picker: read robots.txt and the sitemaps, show the URLs with their page type.", "Should"],
     ["FR-11", "Page inventory of the whole site; crawler; audits daily, weekly and monthly per site.", "Later (Phase 3)"],
     ["FR-12", "Search Console data every day; keyword-to-page map with one primary keyword per page and language; work queue ranked by effect and effort.", "Later (Phase 3)"],
     ["FR-13", "Content items with workflow states, roles, versions and events.", "Later (Phase 3)"],
     ["FR-14", "Chrome extension: show approved suggestions in the site editor and fill fields when a person accepts. It never saves.", "Later (Phase 4)"],
     ["FR-15", "Language versions (EN-DE, hreflang groups) and health rules.", "Later (Phase 5)"],
     ["FR-16", "Measure each change at 4, 8 and 12 weeks: per page first, then against unchanged pages of the same type. Weekly report and alerts.", "Later (Phase 6)"],
     ["NFR-1", "Read-only on client sites. Respect robots.txt (RFC 9309) and rate limits per host.", "Must"],
     ["NFR-2", "Every number shows its source and date. Every AI call is logged with model, prompt version and cost.", "Must"],
     ["NFR-3", "Multi-site and multi-tenant data model from day 1 (tenant_id, site_id on every row).", "Must"],
     ["NFR-4", "A failed source does not stop a run; the run records the gap.", "Must"],
     ["NFR-5", "Cost per site per month is tracked and capped.", "Should"],
     ["NFR-6", "Tests run without paid APIs (recorded data). CI on every pull request.", "Must"]],
    ["9%", "73%", "18%"]), "FR-1 to FR-10 make the page loop of Phase 1. FR-11 to FR-16 come when the tool scales."))

P.append(page("4. Users, roles and approvals", table(
    ["Role", "Who", "Can do", "Cannot do"],
    [["Admin", "Gurzu lead", "Add sites, users, schedules, rules", "Approve own drafts for YMYL items"],
     ["SEO editor", "Gurzu SEO team", "Edit drafts, run audits, submit for review, do the 2i review of another person's draft", "Review own draft"],
     ["Expert reviewer", "Medical expert (health) or native German speaker", "Approve or reject the facts or the language", "Change workflow settings"],
     ["Client approver", "MyPipit or extendmy.life team", "Final approval; apply and save in the site editor", "Change audit rules"],
     ["Viewer", "Anyone invited", "Read reports", "Edit"]],
    ["15%", "22%", "38%", "25%"]) + svg("states", "150mm"),
    "Nobody approves their own work. In Phase 1 a person accepts, edits or rejects each suggestion. The full states below come with the content workflow (Phase 3). Health (YMYL) and German content need an extra expert or native review."))

P.append(page("5. Architecture", svg("arch", "200mm") + """
<div class="note">NOTE: One service (a modular monolith) is enough for 1 to 2 engineers. Each module has a clear interface, so a module can move to its own service later. In Phase 1 the service works on one page at a time, on request. The dashed boxes come in later phases. The extension holds no logic and no keys; Chrome bans remotely hosted code (MyPipit evidence S17).</div>""",
    "Layers: people → interfaces → one Python service with clear modules → PostgreSQL → read-only data sources. Dashed boxes come later."))

P.append(page("5. Architecture (continued): code grouped by feature", svg("modules", "70mm") + """
<pre style="font-size:7.6pt;line-height:1.3;background:#f3f5f8;border:1px solid #d5dce6;padding:6px 9px;margin:6px 0">apps/api/src/seo_advisor/
  core/           config, db session, ids (uuidv7), tenancy, logging, errors (RFC 9457)
  integrations/   external clients only: http_fetch (+ SSRF guard), search_console, crux, llm
  features/
    sites/  inventory/  audits/  drafts/          (Phase 1: one page)
    search_data/  content/  reports/            (later phases)
      api.py  service.py  schemas.py  models.py  repository.py  workflows.py  prompts/
  main.py         builds the app and mounts each feature router
apps/api/tests/&lt;feature&gt;/          apps/web/src/features/&lt;feature&gt;/   (same features)</pre>""" + table(
    ["Rule", "Reason"],
    [["A feature imports another feature only through its service.py. It never imports their models or repository.", "Each feature can change inside without breaking others. import-linter protected contracts check this rule in CI (S45)."],
     ["core/ and integrations/ import no feature.", "Shared code stays small and has no hidden links to features."],
     ["Vendor APIs are called only in integrations/.", "A vendor change touches one folder (same rule as SEOAdvisor)."],
     ["A new feature is a new folder plus one line in main.py. Its tables go into the one shared migration history.", "Work stays in one place. A new engineer finds all code for a feature in one folder."],
     ["The web app uses the same feature names.", "One name for one thing, from database to screen."]],
    ["55%", "45%"]),
    "The platform is one service (a modular monolith). The code is grouped by feature, not by type. All code for one feature is in one folder."))

P.append(page("6. Data model", svg("datamodel", "175mm") + """
<div class="note">NOTE: IDs use <code>uuidv7()</code> (PostgreSQL 18), so rows sort by time. In Phase 1 the table pages holds only the pages that a person analyses, not the whole sitemap. Each check of a page adds a snapshot and an audit run, so two runs can be compared. Suggestions and AI call logs are never deleted.</div>""",
    "Every table has tenant_id and site_id (not all shown). Crow-foot arrows mean one-to-many. Header colours: grey = tenancy, blue = page and snapshot, red = audits, green = suggestions, purple = AI call log. The grey box lists the tables of later phases."))

P.append(page("7. Database: options we compared", table(
    ["Option", "Benefit", "Drawback", "Decision"],
    [["PostgreSQL 18 + pgvector", "Many writers; JSONB; full-text search with English and German stemmers; row-level security; partitioning; vectors in the same database (S20).", "A server to run. Row-level security needs care: table owners skip it unless forced.", G],
     ["SQLite", "No server; simple backups.", "One writer at a time, also in WAL mode. SQLite's own guide says to use a client/server database for many concurrent writers.", V],
     ["MongoDB", "Flexible documents.", "Our data is relational (sites → pages → items → versions). SSPL licence.", V],
     ["TimescaleDB", "Time-series helpers.", "Key features are under a licence that forbids selling as a service. Plain PostgreSQL is enough at this size.", V],
     ["Separate vector database", "Fast vector search at large scale.", "One more system. pgvector is enough for thousands of pages.", I]],
    ["18%", "40%", "32%", "10%"]) + table(
    ["PostgreSQL detail", "Rule for seo-advisor"],
    [["pgvector index", "HNSW for search speed. Indexed vectors are limited to 2,000 dimensions; ask the embedding model for a smaller size or use halfvec."],
     ["Full-text search", "Use the english and german configurations. German compound words need an extra dictionary later."],
     ["Partitioning", "Not now. The docs say it pays off when a table is larger than server memory. Add monthly partitions to gsc_rows later."],
     ["Row-level security", "Not in phase 0. The app filters by tenant_id. When outside customers arrive, enable RLS with FORCE and a non-owner app role."]],
    ["25%", "75%"]),
    "The platform has many writers at the same time. This decides the database."))

P.append(page("8. Flow A: analyse one page", svg("onboard", "215mm"),
    "The page loop of Phase 1. A person starts it for one page. Nothing runs on a schedule."))

P.append(page("9. Flow B: check the page again", svg("schedule", "120mm") + "<h2>Later (Phase 3): scheduled audits for the whole site</h2>" + table(
    ["Run", "What", "Why"],
    [["Daily", "robots.txt, sitemaps, status codes, new and removed URLs, Search Console sync", "Errors must show fast. Search Console data is 2 to 3 days late."],
     ["Weekly", "All rules on pages that changed and on a rotating sample", "Stable view without crawling everything every day."],
     ["Monthly", "Full audit, keyword map refresh, review dates, Core Web Vitals (CrUX API)", "Content and keywords change slowly. CrUX data covers 28 days."]],
    ["12%", "53%", "35%"]),
    "In Phase 1 a person asks for a new check after a change. Each check compares with the previous run, so the team sees what is new, fixed or back. Schedules come in Phase 3."))

P.append(page("10. Flow C: from finding to fix", svg("content", "205mm"),
    "A finding on the page becomes a suggestion. A template issue goes to the site developers. A page issue gets an AI suggestion that passes checks and a human review. A person copies it into the site editor and saves it."))

P.append(page("11. Managing many content items (Phase 3: whole site)", f"""
<p>This section is for Phase 3, when the tool scales to the whole site. Phase 1 works on one page at a time. extendmy.life alone has about 474 URLs. The platform must manage this volume without a person opening every page. These are the rules.</p>
{table(["Rule", "How it works", "Example"], [
 ["One inventory", "Every page, field and language version is a row. Nothing is edited outside the platform.", "The German and English versions of one article share one hreflang group."],
 ["Page types and templates", "Rules run per page type. A finding on many pages of one type is a template fix, not 100 single fixes.", "One meta description on all 17 category pages → one request to the developers."],
 ["Priority score", "Impact (Search Console impressions, page type value) × confidence ÷ effort. The queue shows the top items first.", "A clinic page with 3,000 impressions at position 8 comes before a page with 20 impressions."],
 ["Batches", "Work in batches of 5 to 10 items of the same type, so reviewers keep one context.", "Batch: 8 retreat pages, titles and descriptions only."],
 ["Keyword map", "One primary keyword per page and language. The platform blocks a second page with the same primary keyword.", "'longevity clinic poland' belongs to one clinic page only."],
 ["Review dates", "Each page gets a next review date. Health pages need a shorter cycle. The audit sets 'Needs review' when the date passes.", "Health article: review every 6 months (example, to agree)."],
 ["Major and minor changes", "Only a major change (new facts, prices, advice) updates dateModified and the sitemap lastmod.", "Fixing a typo is minor: dates stay."],
 ["Bulk actions with care", "Bulk changes are allowed only for structure (for example alt text drafts). Each item still needs review.", "40 alt text drafts reviewed in one screen."],
], ["17%", "48%", "35%"])}
<div class="caution">CAUTION: Do not generate many pages from one template without real added value. Google lists this as scaled content abuse (MyPipit evidence S12).</div>
"""))

P.append(page("12. Audit rules", '<h2>Phase 1: first rules for a blog post</h2><div class="small">' + table(
    ["Area", "Rule", "Source"],
    [["Title", "Present; fits about 600 pixels (rule of thumb; reuse the SEOAdvisor pixel check); the target keyword is in the title", "R3 §1"],
     ["Meta description", "Present and unique; 120 to 156 characters is a rule of thumb, not a Google rule", "R3 §2, §11"],
     ["Headings", "Exactly one H1; the keyword is in the H1; heading levels in order", "Practice"],
     ["Images", "Alt text present, descriptive and not stuffed; image URLs are stable (MyPipit image links expire after 1 hour)", "R3 §3.1, §3.2"],
     ["Social image", "og:image present, at least 1200 x 630 pixels", "R3 §3.3"],
     ["Indexing", "Canonical present and self-referencing; no noindex", "R3 §7"],
     ["Structured data", "BlogPosting with author, datePublished, dateModified, headline and image", "R3 §5.11"],
     ["Links", "Internal links are &lt;a href&gt; links with descriptive anchor text", "R3 §13.1"],
     ["Slug", "Readable words with hyphens, no IDs", "R3 §8.1"],
     ["Page", "lang attribute present; word count shown as information only (Google has no preferred word count)", "R3 §6.4"]],
    ["16%", "64%", "20%"]) + '</div><h2>Later: rules for the whole site, other page types and other sites</h2><div class="small">' + table(
    ["Group", "Rule", "Source"],
    [["Technical", "HTTP status 200; no redirect chains; HTML under 2 MB (Googlebot reads the first 2 MB)", "Google (S9)"],
     ["Technical", "robots.txt valid; Sitemap line present; parameter rules block all positions of filter parameters", "RFC 9309 (S10), Google faceted navigation (S8)"],
     ["Technical", "Sitemap lastmod changes only when the page content changes", "Google (S7), Bing (S11)"],
     ["Language", "hreflang links reciprocal, full URLs, same-language canonical, x-default to a real page", "Google (S5)"],
     ["Language", "Visible text is in the declared language; German text reviewed by a native speaker", "Google (S5)"],
     ["On-page", "Meta description unique across the site (no shared category text)", "Google"],
     ["Structured data", "Clinic pages: MedicalClinic (a LocalBusiness type) with name and address; no self-serving review stars", "schema.org, Google (S4)"],
     ["Health (YMYL)", "Named author or reviewer with real credentials; visible last reviewed date; no invented experts", "Google (S2, S3)"],
     ["Content", "Covers the basics for its page type; answers the main user questions; no keyword stuffing", "Google helpful content (S2)"],
     ["Freshness", "Review date not passed; dates change only with major changes", "Google (S2), GOV.UK (S16)"],
     ["Speed", "LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at the 75th percentile (when CrUX has data)", "web.dev (S12)"]],
    ["14%", "61%", "25%"]) + "</div>",
    "Each rule records its source. A rule that is only common practice or a rule of thumb says so. R3 is the MyPipit research file (requirements/research/03-mypipit-evidence.md)."))

P.append(page("13. Content generation rules", table(
    ["Rule", "Detail"],
    [["Facts only from the page", "The draft uses facts that are in the current page or in data that the client gave. Every other fact is an [ADD: ...] placeholder."],
     ["No copied text", "No run of 8 words may match another site's page."],
     ["Second model checks", "A model from another family checks that each sentence has support in the source."],
     ["German drafts", "The platform drafts German text, but a native German speaker must review it before approval. Machine translation alone is not enough (S6)."],
     ["Health (YMYL) drafts", "Rule to decide before extendmy.life drafts start: a named expert reviewer, or AI limited to non-medical text. Never invent authors or credentials (S3)."],
     ["Disclosure", "For health content, show who wrote and reviewed it, and how it was made (Who, How, Why) (S2)."],
     ["Legal check (Germany)", "German advertising law (HWG §11) limits before/after images and testimonials for cosmetic procedures. A lawyer must confirm how it applies to aesthetic clinic pages."],
     ["No word-count targets", "Google has no preferred word count. The draft covers what the user needs."],
     ["People publish", "The extension fills the fields. A person clicks Save. The platform never publishes."]],
    ["24%", "76%"]),
    "The same rules apply to every site. Health sites add expert review and stricter checks."))

P.append(page("14. Options we compared", table(
    ["Topic", "Option", "Benefit", "Drawback", "Decision"],
    [["Site access", "Read-only + extension", "No client code change; people stay in control", "The extension depends on the editor layout", G],
     ["", "Write through site APIs", "Fully automatic", "Needs developer access and trust on both sites", I],
     ["", "Export packs only", "Simple", "Manual copying, errors", V],
     ["Structure", "Modular monolith", "One deploy, simple for 1 to 2 engineers", "Must keep module borders clean", G],
     ["", "Microservices", "Independent scaling", "Too much operations work now", V],
     ["Code grouping", "By feature (sites, inventory, audits ...)", "All code for one feature in one folder. Small, clear changes", "Needs a rule check for imports between features", G],
     ["", "By type (all models, all services, all routes)", "Familiar", "One change touches many folders. Features mix", V],
     ["Jobs", "DBOS on PostgreSQL", "Durable steps, cron per site, no Redis", "Newer library", G],
     ["", "Procrastinate", "Simple PostgreSQL queue", "Schedules need own table", I],
     ["", "Celery + Redis", "Well known", "Extra Redis; one scheduler process only", V],
     ["Tenancy", "Shared schema + tenant_id", "Lowest cost and effort", "Isolation in the app until RLS", G],
     ["", "Schema per tenant", "Some isolation", "Every migration N times", V],
     ["Crawler", "httpx from sitemaps", "Fast, cheap, reuses SEOAdvisor code", "Not for JavaScript-only pages", G],
     ["", "Headless browser for all", "Sees rendered pages", "Slow, heavy; not needed for these sites", I],
     ["Repo", "New repo, reuse modules", "Clean multi-site design", "Some copying", G]],
    ["12%", "20%", "26%", "28%", "14%"])))

P.append(page("15. Technology stack", table(
    ["Layer", "Choice (version on 6 Oct 2026)", "Reason"],
    [["Code structure", "Modular monolith grouped by feature, import-linter contracts", "Easy to work in one feature at a time (section 5, continued)."],
     ["Tools and tasks", "mise 2026.10 pins Python, Node, uv, pnpm and prek. It also runs the project tasks.", "One file gives every person and CI the same tools and commands (S31)."],
     ["Python", "Python 3.14.8, uv 0.12 (lock file uv.lock). Package name seo_advisor (not seo_engine, which SEOAdvisor uses).", "3.15 is new and DBOS, FastAPI and Pydantic do not support it yet (S26). uv replaces pip, venv and pip-tools (S25)."],
     ["API", "FastAPI 0.142, Pydantic 2.13, pydantic-settings 2.15", "Typed inputs and outputs. OpenAPI generates the TypeScript client."],
     ["Database", "PostgreSQL 18 + pgvector 0.8.7, SQLAlchemy 2.1 (sync), psycopg 3, Alembic 1.20", "Sync code is simpler for new engineers and fits DBOS (S39)."],
     ["Jobs", "DBOS 3.2 on the same PostgreSQL, from Phase 3. Phase 1 runs on request.", "Durable steps and schedules without a second server (S22)."],
     ["Quality (Python)", "ruff 0.16 (lint and format), mypy 2.4 --strict, pytest 9.1 strict, testcontainers 4.15", "One type checker as the gate. Tests use a real database (S27, S28)."],
     ["Web app", "React 19.3, TypeScript 6.0.3, Vite 8.3, pnpm 12, TanStack Router, Query and Table, Tailwind CSS + shadcn/ui, oxlint + Prettier, Vitest 5. React Hook Form + Zod when the first real form needs them. Recharts from Phase 6", "TypeScript 7 has no tool API until 7.1. The Vite template uses oxlint (S29)."],
     ["API client", "openapi-typescript 7.13 + openapi-fetch 0.17", "Small and stable. CI fails if the client is out of date."],
     ["Extension", "WXT 0.21 (Manifest V3)", "Less custom build code. Shares Vite, React and TypeScript with the web app (S30)."],
     ["Logs and traces", "structlog 26.1, OpenTelemetry 1.45 (later step)", "Logs with request ID from day 1 (S38)."],
     ["AI", "DeepSeek writes suggestions (owner decision, 8 Oct 2026). A checker from another model family later.", "Prompts as versioned files. Every call logged with cost (S41)."],
     ["Docs", "playwright 1.63 (Python) and @hpcc-js/wasm-graphviz 1.29 (npm), docs only", "<code>mise run docs:pdf</code> builds this PDF with the installed Google Chrome."],
     ["Git and CI", "GitHub Actions, Dependabot, gitleaks, prek hooks", "Free tools. Paid GitHub security later (S33)."],
     ["Deployment", "Later, with DevOps", "Not in this plan."]],
    ["15%", "45%", "40%"]) + """<h2>All pinned versions (6 October 2026)</h2>
<p class="src">Python 3.14.8 · uv 0.12.23 · ruff 0.16.10 · mypy 2.4.0 · pytest 9.1.1 · testcontainers 4.15.0 · FastAPI 0.142.2 · Pydantic 2.13.5 · pydantic-settings 2.15.0 · SQLAlchemy 2.1.3 · psycopg 3.3.6 · Alembic 1.20.0 · DBOS 3.2.0 · structlog 26.1.0 · pytest-recording 0.14.0 · Node 24 LTS (Node 26 LTS from 28 October 2026) · pnpm 12.9 · Vite 8.3.3 · React 19.3.0 · TypeScript 6.0.3 · oxlint 1.87.0 · Prettier 3.9.9 · Vitest 5.0.3 · Playwright 1.63.0 · WXT 0.21.4 · openapi-typescript 7.13.0 · openapi-fetch 0.17.0 · mise 2026.10.3 · prek 0.5.5 · gitleaks 8.30.1 · pip-audit 2.10.1 · Docker image pgvector/pgvector:0.8.7-pg18-trixie · import-linter 2.15</p>""",
    "The versions are the current versions on 6 October 2026. Check them again on the day of the setup."))

P.append(page("16. Set up the repo", svg("setup", "150mm") + table(
    ["Principle", "What it means"],
    [["One command to start", "A new engineer runs <code>mise run setup</code> and then <code>mise run check</code> (or <code>make check</code>). Nothing else is necessary."],
     ["Automatic checks, light process", "Lint, format, types and tests run by themselves. Hooks only fix files or block secrets. Process rules stay few, so new engineers can work fast."],
     ["Decisions in writing", "A decision record (ADR) for each main choice. People and AI tools read the reason for each choice (S35)."],
     ["Same environment for all", "mise pins the tools. Docker Compose runs the database. Lock files fix every package version."],
     ["Safe by default", "No secrets in git. Actions pinned to commit IDs. The fetcher blocks internal addresses (S33, S37)."]],
    ["28%", "72%"]),
    "Steps 0.1 to 0.3 came first. Since 7 October 2026 the other steps start when a slice needs them, so feature work and setup go together."))

P.append(page("16. Set up the repo (continued): when each step starts", table(
    ["Step", "Starts with"],
    [["0.1 to 0.3", "Done."],
     ["0.4 Database", "Slice 2. Only the tables that each slice needs: tenants, sites (done); pages, page_snapshots (slice 2); audit_runs, findings (slice 3); suggestions, llm_calls (slice 4)."],
     ["0.5 API", "Started 8 Oct 2026 with the web app; structlog is still open."],
     ["0.6 Web app", "Started 8 Oct 2026: each slice now ends with its screen. The extension starts in Phase 4."],
     ["0.7 Hooks, 0.8 CI", "Before the first pull request into dev, or when the owner decides."],
     ["0.9 Claude Code settings", "When the owner decides. Recommended soon: deny reads of .env."],
     ["0.10 ADRs", "Write each ADR when its decision is made or first used."],
     ["0.11 SSRF guard", "Slice 1 (the first outbound fetch). Done."],
     ["0.11 AI layer, evals", "Slice 4 (AI suggestions, DeepSeek)."],
     ["0.12 Final check", "Before a second person joins."]],
    ["28%", "72%"]),
    "Feature-first (7 Oct 2026): each setup step starts when a slice needs it. Sections 17 and 18 give the full task and the \"done when\" of each step."))

P.append(page("17. Setup checklist, part 1", table(
    ["Step", "What to set up", "Done when"],
    [["0.1 Machine <span class='tag g'>Done</span>", "Install mise, Docker, the GitHub CLI and Claude Code. Set the git identity raksha-gurzu. Push through the github.com-gurzu SSH alias.", "The three tools report their versions and gh is logged in."],
     ["0.2 Repo skeleton <span class='tag g'>Done</span>", "Folders apps/api (with core, integrations and empty feature folders), apps/web, apps/extension, packages/api-client, docs (with decisions, architecture, design and notes), evals, experiments, infra, .github. Copy this requirements folder into the repo. README with a 5-minute setup, .gitignore, .editorconfig, .env.example with fake values, a proprietary NOTICE. mise.toml with tool versions and tasks (setup, dev, test, lint, typecheck, check, audit, db:up, db:migrate, db:seed, gen-client, evals, docs:pdf). The docs:pdf task rebuilds this PDF.", "A new person follows the README and <code>mise run setup</code> works on a fresh clone."],
     ["0.3 Python base <span class='tag g'>Done</span>", "pyproject.toml, uv.lock, dependency groups (dev, test, lint), a 7-day delay for new package releases (exclude-newer), src layout. ruff rules E F W I UP B SIM S ASYNC PT RUF DTZ N. mypy --strict with the Pydantic plugin. pytest strict mode and markers (unit, integration, e2e, live). import-linter protected and forbidden contracts for the feature rules. (Do not use the independence contract. It also blocks the allowed calls through service.py.) A vulnerability check task (<code>mise run audit</code>, pip-audit). A Settings class that reads all configuration from the environment and stops at start if a key is missing.", "<code>mise run check</code> passes. A forbidden import between features fails the check. A missing key stops start-up with a clear message."],
     ["0.4 Database base <span class='tag i'>Started</span>", "Docker Compose with the pgvector image. Mount the volume at /var/lib/postgresql (PostgreSQL 18 changed this path, S32). SQLAlchemy base with the Alembic naming convention. First migration: vector extension, uuidv7() keys, timestamps with time zone, first tables. Test fixtures: testcontainers starts one test database for each session, rollback after each test, DBOS reset. Seed script with 2 fake sites.", "Upgrade and <code>alembic check</code> pass on an empty database. An integration test passes twice in a row."],
     ["0.5 API base <span class='tag i'>Started</span>", "FastAPI under /api/v1 with a health route. An error handler for RFC 9457 problem details (FastAPI has none, S40). Request ID middleware. structlog. An operation ID on each route. A task that exports openapi.json and generates the TypeScript client.", "An error returns application/problem+json with the request ID. The web app calls /health through the generated client."],
     ["0.6 Web and extension base <span class='tag g'>Web done</span>", "Vite react-ts template with strict TypeScript flags, oxlint, Prettier, Vitest, Testing Library and MSW. TanStack Router, Query and Table. Tailwind CSS and shadcn/ui, with the components in src/shared/ui. Folders app, routes, features and shared, as in CLAUDE.md. Check the version, licence and advisories of each library that R4 does not cover. Keep the pnpm release delay. Allow no install scripts until a package needs one. WXT extension skeleton with minimal permissions and no remote code.", "Lint, type check, tests and build pass. The extension loads in Chromium and calls /health."]],
    ["14%", "56%", "30%"]),
    "The detail and the sources for each step are in research file R4 (requirements/research/04-project-setup.md). Section 16 says when each step starts."))

P.append(page("18. Setup checklist, part 2", table(
    ["Step", "What to set up", "Done when"],
    [["0.7 Hooks", "One .pre-commit-config.yaml, run by prek: file hygiene, gitleaks, ruff fix and format, oxlint and Prettier, lock file check, actionlint, zizmor.", "Hooks finish in less than 5 seconds. A planted fake key is blocked."],
     ["0.8 CI and GitHub", "One CI workflow. Pin actions to commit IDs and turn on the GitHub policy that requires pinned actions. Read-only token by default. Jobs: lint, types, tests, migrations, OpenAPI drift, web, extension, gitleaks, and one required job. Ruleset on main: pull request, required check, squash merge only, linear history, no force push. 0 approvals while one engineer works, 1 approval when a second engineer joins. Check the pull request title for Conventional Commits. Dependabot each week for uv, pnpm, actions and Docker. A pull request template with an AI-assisted line.", "A failing test blocks the merge. A direct push to main is refused. The first Dependabot pull request passes CI."],
     ["0.9 Claude Code", "CLAUDE.md is at the repo root (under 200 lines). .claude/settings.json: deny reads of .env files, keys, lock files, build output, node_modules, the generated client and PDFs, deny force push, allow the project commands, a format hook after edits, fast tests when Claude stops, sandbox on. Skills: new-endpoint, new-migration, run-evals. A security-reviewer subagent.", "Claude cannot read .env. Claude runs <code>mise run check</code> from CLAUDE.md alone."],
     ["0.10 Decisions and diagrams", "8 to 10 ADRs in MADR 4.0 format (layout, Python and uv, PostgreSQL and pgvector, DBOS, sync SQLAlchemy, code-first OpenAPI, AI providers, read-only rule, WXT, logging). C4 level 1 and 2 diagrams. A design document template.", "Each ADR has context, options, decision and consequences."],
     ["0.11 Security and AI base <span class='tag g'>Guard done</span>", "SSRF guard with tests for each blocked address range and for DNS rebinding (reuse from SEOAdvisor). AI layer at slice 4 (DeepSeek; reuse SEOAdvisor providers/llm.py): provider interface, model and price settings, llm_calls table, prompts as versioned files, recorded test fixtures with keys removed, cost limits per run and per day. One key for each person, and a spend limit at each provider. evals folder with 20 first cases and code-based graders.", "Guard tests pass before crawler code exists. A recorded AI call replays in CI with no network. <code>mise run evals</code> shows a score table."],
     ["0.12 Final check", "Fresh clone, setup, check, CI, secret block and push block, all from the README only.", "A second person or a new Claude session completes it in 15 minutes or less."]],
    ["15%", "55%", "30%"]) + """
<h2>Should do in weeks 2 to 4</h2>
<p>SSH commit signing. Issue forms, labels and milestones for each phase. Semgrep and a weekly dependency audit. A coverage floor that only goes up. Property tests for scoring code. 2 or 3 Playwright tests and one extension test. OpenTelemetry with a local trace viewer. Nightly evals with model graders. An OWASP ASVS level 1 checklist. Feature flags in the settings.</p>
<div class="caution">CAUTION: GitHub secret scanning and push protection cost money on a private repository. Use gitleaks in the hooks and in CI until the budget allows the paid feature (S33).</div>"""))

P.append(page("19. Working with Claude Code", table(
    ["Topic", "Rule"],
    [["CLAUDE.md", "CLAUDE.md and PLAN.md are at the repo root, not in the requirements folder. Keep it under 200 lines. Put in it the commands, the rules that differ from defaults and links to ADRs and PLAN.md. Do not copy long documents into it. Anthropic says that a long file makes Claude ignore instructions (S42)."],
     ["Context and tokens", "Load only the current step of PLAN.md. Do one task in each session and clear the context between tasks. Read only the research section that a task names. Use a subagent for wide searches. Do not load the PDF."],
     ["Plan first", "Use plan mode for work that touches many files or is not clear. For a large feature, let Claude ask questions and write a short design document first."],
     ["Proof, not claims", "Give Claude a check that it can run: tests, type check, build. Ask for the command and its output. A hook runs fast tests when Claude stops."],
     ["Tests first", "Write a failing test, confirm that it fails, then write the code (S41)."],
     ["Human review", "A person reads every line before the merge. The pull request template asks if AI helped and who reviewed it."],
     ["Secrets", "Deny rules stop Claude from reading .env files and keys. Keys go into the environment only. The sandbox is on."],
     ["Big files", "Deny rules also stop reads of lock files, build output, node_modules, the generated client and PDFs. One lock file can cost thousands of tokens."],
     ["Quiet output", "Commands and hooks print only failures, or the last 20 lines. A green run adds one line to the context."],
     ["Model and tools", "Use a smaller model for routine edits and for search subagents. Keep the larger model for planning and hard bugs. Switch off MCP servers that the project does not use."],
     ["Untrusted text", "Web pages and issue text can contain hidden instructions. Treat them as data. The AI that reads page text gets no tool that can write or send (S37)."]],
    ["20%", "80%"]) + "<h2>Working rules for all engineers</h2>" + table(
    ["Rule", "Detail"],
    [["Setup and checks", "One setup command (<code>mise run setup</code>) and one check command (<code>mise run check</code>)."],
     ["Pull requests", "Keep a pull request small: aim for 400 changed lines or fewer. Squash merge. Write the title in Conventional Commits form, for example <code>feat(api): add sitemap reader</code>. Only the title is checked."],
     ["Approvals", "0 approvals while one engineer works. 1 approval when a second engineer joins. Change the ruleset at that time."],
     ["Skipping a rule", "Skip a check only with a comment that gives the reason, for example a type-ignore comment with its error code and reason."],
     ["Tasks", "Tick a task in PLAN.md only when its \"done when\" is true. Log the time in Emitii on the matching card."]],
    ["20%", "80%"]),
    "These rules keep the cost of each session low and keep AI-written code safe to merge."))

P.append(page("20. Order of work", svg("roadmap", "150mm") + table(
    ["Phase", "Done when", "Estimate"],
    [["0. Set up the repo", "Steps 0.1 to 0.3 done. The other steps start when a slice needs them. The final check passes before a second person joins (step 0.12).", "1 to 1.5 weeks in total"],
     ["1. One page, end to end (MyPipit blog post)", "Slices 1 to 5 are done. 90 percent or more of findings are correct. 7 of 10 suggestions are accepted with small edits.", "2 to 3 weeks"],
     ["2. More page types on MyPipit", "Listings, blog categories and static pages have rule sets with sources. The page type also comes from the content.", "1 to 2 weeks"],
     ["3. Whole site", "A full crawl is stored. Schedules run for 2 weeks without a manual start. Duplicate keywords are blocked. The work queue shows the top 10 with reasons.", "2 to 3 weeks"],
     ["4. Extension", "A person applies and saves one approved suggestion. An item is Live only after the check confirms it.", "1 to 2 weeks"],
     ["5. Second site and languages (extendmy.life)", "English and German pages match the 12 sitemaps. The health rule and native review are enforced in code.", "2 to 3 weeks"],
     ["6. Measure and report", "Outcomes at 4, 8 and 12 weeks. A weekly report for each site owner.", "1 to 2 weeks"]],
    ["24%", "58%", "18%"]),
    "The phases are the current direction and can change. Each phase is built in small slices (see How we work). In each slice, build and check the backend first, then its screen. Each phase ends with a check. If the check fails, fix the rules or prompts before the next phase. Estimates are for one engineer."))

P.append(page("21. Tasks, phases 1 to 3", table(
    ["Phase", "Task", "Done when"],
    [["1", "Slice 1: safe fetcher (SSRF guard, robots.txt, rate limit for each host; reused from SEOAdvisor), sitemap reader, page type and language for each URL. The sitemap list is now the page picker.", "Done. The MyPipit URL list is the same as its sitemap URLs."],
     ["1", "Slice 2a: database base, tables tenants and sites, <code>make seed</code>", "Done."],
     ["1", "Web app and API for slice 1: sites, sitemap list, request trace, page-type rules and URL tester, <code>make dev</code>", "Done. The screens change in slice 2."],
     ["1", "<s>Slice 2b: save all sitemap pages</s>", "Removed (8 Oct 2026): only analysed pages are saved."],
     ["1", "Slice 2: fetch and extract one page. Spike with 1 MyPipit blog post. inventory.fetch_page (the URL must be on a registered site), tables pages and page_snapshots, the extractor. Screen: analyse a page (paste a URL or pick one from the sitemap list).", "The extracted fields of the fixture page are correct in tests. The screen shows them for a live MyPipit post."],
     ["1", "Slice 3: audit one page. Rules for blog posts with sources, severity and evidence; tables audit_runs and findings; the keyword is part of the run. Screen: findings, filter by severity, check again.", "Each finding has evidence and a source. Two runs of the same page can be compared."],
     ["1", "Slice 4: AI suggestions. AI layer with DeepSeek (step 0.11); drafts: suggestions with [ADD: ...], Pydantic check, one retry; tables suggestions and llm_calls; checks for invented facts and copied text. Screen: accept, edit or reject; copy.", "Every AI call is logged. No invented fact reaches review."],
     ["1", "Slice 5: the loop on 5 MyPipit blog posts with the SEO team", "90 percent or more of findings are correct. 7 of 10 suggestions are accepted with small edits."],
     ["2", "Rules for listings (travel structured data), blog categories and static pages", "Each type has its rule set with sources."],
     ["2", "Page type from the content (title, structured data), not only the URL", "The fixture pages get the correct type."],
     ["3", "Inventory of all sitemap pages; crawler with robots.txt rules, rate limit for each host and snapshots", "A full crawl is stored."],
     ["3", "DBOS schedules (daily, weekly, monthly) and comparison with the last run", "Runs work for 2 weeks without a manual start."],
     ["3", "Search Console sync, keyword-to-page map with one primary keyword for each page and language, cannibalisation check", "The platform blocks duplicates."],
     ["3", "Content items, versions, states and roles; work queue: impact × confidence ÷ effort", "The queue shows the top 10 items with reasons."]],
    ["8%", "57%", "35%"])))

P.append(page("22. Tasks, phases 4 to 6, and later work", table(
    ["Phase", "Task", "Done when"],
    [["4", "Extension for the test site editor: show approved suggestions, fill on Accept, never save", "A person applies and saves one approved suggestion."],
     ["4", "Verify after publish: fetch the page again", "An item becomes Live only after the check confirms it."],
     ["5", "Second site and languages (test site extendmy.life): English and German pages, hreflang groups, page types", "The pages match the 12 sitemaps."],
     ["5", "Language rules (R2 §3) and health rules (R2 §1 and §2)", "The known issues show as findings."],
     ["5", "German text needs native review. The health rule is in code.", "Nobody can skip either step."],
     ["6", "Outcomes at 4, 8 and 12 weeks: per page first, then compared with unchanged pages of the same type (needs Phase 3)", "The report shows outcomes for each change older than 4 weeks."],
     ["6", "Weekly report and alerts (email or Emitii)", "Each site owner gets one report each week."]],
    ["8%", "52%", "40%"]) + table(
    ["Later (needs a decision first)", "Note"],
    [["Deployment", "With DevOps: hosting, backups, login in front of the app."],
     ["Competitor analysis", "Owner decision: later."],
     ["Paid keyword data", "Only if free data is too thin."],
     ["Row-level security and outside accounts", "When outside customers arrive."],
     ["GitHub Secret Protection and CodeQL", "When the budget allows."],
     ["Sentry, SBOM, release automation", "With deployment."],
     ["TypeScript 7, Python 3.15", "After the tools support them."]],
    ["40%", "60%"])))

P.append(page("22. Change log", '<div class="small">' + table(
    ["Date", "Change", "Reason"],
    [["5 Oct 2026", "Plan created: phases 0 to 5, PostgreSQL, DBOS, read-only access with an extension", "Requirements research (R1 to R3)"],
     ["6 Oct 2026", "Setup phase added: uv, pnpm, mise, strict checks, light process rules", "Setup research (R4). Easy start for new engineers"],
     ["6 Oct 2026", "General tool. Small parts. Research, experiment, implement", "Owner decision"],
     ["6 Oct 2026", "Modular monolith grouped by feature. Security rules in CLAUDE.md", "Owner decision"],
     ["6 Oct 2026", "Review: repeated content removed. Session habits for people moved from CLAUDE.md to PLAN.md", "Keep both files small"],
     ["6 Oct 2026", "CLAUDE.md kept as CLAUDE.template.md until it is copied. The PDF is rebuilt with every plan change. import-linter uses protected and forbidden contracts", "Owner decision. Contract check"],
     ["6 Oct 2026", "PLAN.md and CLAUDE.md stay at the repo root. There is no CLAUDE.template.md", "Owner decision"],
     ["7 Oct 2026", "Frontend: TanStack Router and Table, Tailwind CSS and shadcn/ui. React Hook Form and Zod in Phase 2. Recharts in Phase 5. Web folder layout", "Owner decision"],
     ["7 Oct 2026", ".gitattributes and folder READMEs added to step 0.2. CONTRIBUTING.md and SECURITY.md moved from Should to step 0.2. A db:down task added", "Owner decision"],
     ["7 Oct 2026", "Step 0.3: protected import contracts are added for each feature. pip-audit checks uv.lock. The pnpm checks join mise run check in step 0.6. The 7-day delay gives ruff 0.16.9 and mypy 2.3.1", "One wildcard contract cannot limit a feature to its own internals. Owner decision"],
     ["7 Oct 2026", "Feature-first: Phase 1 in 5 slices. Steps 0.4 to 0.12 start when a slice needs them. Empty placeholder folders removed", "Owner decision: see a real feature first"],
     ["8 Oct 2026", "Backend and frontend in parallel: every slice ends with its screen. API (step 0.5, without structlog) and web app (step 0.6) started early. make wraps the mise tasks. The fetcher records each request for the Activity screen. jsdom added for web tests. TypeScript 6.0.3 (openapi-typescript needs the TypeScript API)", "Owner decision: see what each feature does"],
     ["8 Oct 2026", "Single page first: Phase 1 is one MyPipit blog post end to end (fetch, extract, audit with evidence, DeepSeek suggestions, review). The sitemap list is a page picker. The whole site moves to Phase 3, the extension to Phase 4, extendmy.life to Phase 5, reports to Phase 6. Backend first, then its screen, in each slice. Docs packages playwright and @hpcc-js/wasm-graphviz for mise run docs:pdf", "Owner decision: do SEO on one page before the whole site"]],
    ["14%", "56%", "30%"]) + "</div>",
    "When a strategy changes, strike the old task in PLAN.md, add a line to this change log, and update this PDF and the ADR."))

P.append(page("23. Open questions and risks", table(
    ["Item", "Type", "What to do"],
    [["DeepSeek API key", "Dependency", "The owner gives the key before slice 4. It goes into the environment (Settings), never into code or git."],
     ["AI provider data terms", "Open question", "DeepSeek is chosen (8 Oct 2026). Read its data terms before slice 4 sends client page text to it."],
     ["extendmy.life editor and CMS", "Open question", "Find out which editor the authors use. The extension must support it."],
     ["Search Console for extendmy.life", "Open question", "Get read access to the domain property."],
     ["Health review rule", "Owner decision", "Decide before extendmy.life drafts start: expert reviewer or AI limited to non-medical text."],
     ["German native reviewer", "Dependency", "Name a person. Without one, German drafts stay in Draft."],
     ["German law for aesthetic clinics (HWG)", "Legal", "Ask a lawyer before drafts for aesthetic clinic pages."],
     ["Review cycle for health pages", "Open question", "Agree how often health pages need a review, for example every 6 months."],
     ["Code ownership", "Open question", "Find out if Gurzu or the client owns the code. This sets the NOTICE text."],
     ["One page is not the whole picture", "Risk", "Some checks need other pages (duplicate keywords, internal links to the page). The sitemap list helps a little. The full checks come in Phase 3."],
     ["Extension and editor changes", "Risk", "A weekly test checks that the editor fields still exist."],
     ["Small sites, few queries", "Risk", "Search Console hides rare queries. Add paid keyword data only if free data is too thin."],
     ["New tool versions", "Risk", "pnpm 12, Vitest 5 and SQLAlchemy 2.1 are new major versions. Lock files and Dependabot delays reduce the risk."],
     ["Expectations", "Risk", "No tool guarantees rank 1. Measure before and after each change."]],
    ["27%", "15%", "58%"])))

P.append(page("24. Sources", '<div class="small">' + table(
    ["ID", "Source", "Trust"],
    [["S1", "Google, Search Quality Rater Guidelines, 11 Sep 2025. guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf", "Primary"],
     ["S2", "Google Search Central, \"Creating helpful, reliable, people-first content\" (updated 1 Oct 2026)", "Primary"],
     ["S3", "Same guide: YMYL content \"must be highly accurate and consistent with established expert consensus\". Fabricated creator profiles are \"a form of deception\".", "Primary"],
     ["S4", "Google Search Central, \"Article structured data\". schema.org MedicalClinic, MedicalWebPage, Physician", "Primary"],
     ["S5", "Google Search Central, \"Tell Google about localized versions of your page\"", "Primary"],
     ["S6", "Google Search Central, guidance on machine translation and scaled content (MyPipit evidence S12, S13)", "Primary"],
     ["S7", "Google Search Central Blog, \"Sitemaps ping endpoint is going away\" (lastmod accuracy), 26 Jun 2023", "Primary"],
     ["S8", "Google Search Central, \"Managing crawling of faceted navigation URLs\" (Dec 2024)", "Primary"],
     ["S9", "Google Search Central, Google crawlers overview (2 MB HTML limit), JavaScript SEO basics", "Primary"],
     ["S10", "IETF RFC 9309, Robots Exclusion Protocol", "Primary"],
     ["S11", "Bing Webmaster Blog, \"The importance of setting the lastmod tag\" (Feb 2023)", "Primary (Microsoft)"],
     ["S12", "web.dev, Core Web Vitals. Chrome for Developers, CrUX API", "Primary"],
     ["S13", "Google Search Central Blog, Search Console weekly and monthly views (Dec 2025), custom annotations (Nov 2025)", "Primary"],
     ["S14", "StatCounter, search engine market share Germany (Sep 2026)", "Secondary"],
     ["S15", "IndexNow documentation. Bing Webmaster API access (learn.microsoft.com)", "Primary"],
     ["S16", "GOV.UK, \"Write change notes\". GOV.WALES, \"Peer reviewing content (2i)\"", "Primary"],
     ["S17", "Drupal Content Moderation overview. WordPress post status", "Vendor or open source"],
     ["S18", "Brodersen et al. (2015), causal impact with Bayesian structural time-series models, Annals of Applied Statistics", "Peer-reviewed"],
     ["S19", "MyPipit plan evidence: requirements/research/03-mypipit-evidence.md", "Primary sources inside"],
     ["S20", "PostgreSQL 18 documentation. SQLite \"Appropriate Uses\" and \"Write-Ahead Logging\". pgvector README", "Primary"],
     ["S21", "Martin Fowler, \"Temporal Patterns\" and \"Event Sourcing\". PostgreSQL trigger audit example", "Secondary (expert)"],
     ["S22", "DBOS documentation (scheduled workflows, steps, testing). Procrastinate documentation", "Vendor or open source"],
     ["S23", "AWS Prescriptive Guidance, multi-tenant SaaS partitioning models for PostgreSQL, and RLS", "Vendor guidance"],
     ["S24", "Microsoft Azure Architecture Center, storage and data in multitenant solutions (2026-08-21)", "Vendor guidance"]],
    ["7%", "78%", "15%"]) + "</div>",
    "Sources S1 to S24 were checked on 5 October 2026. Full notes with quotes are in the research folder (R1, R2, R3)."))

P.append(page("25. Sources for the setup", '<div class="small">' + table(
    ["ID", "Source", "Trust"],
    [["S25", "uv documentation (dependencies, locking, settings). PEP 621, PEP 735, PEP 751", "Official, standard"],
     ["S26", "PEP 790, Python 3.15 release schedule. PyPI metadata for DBOS, FastAPI, Pydantic (checked 6 Oct 2026)", "Standard, official"],
     ["S27", "Ruff documentation. \"Mypy 2.0 Released\" (May 2026). Pyrefly 1.0 blog. Astral ty blog", "Official"],
     ["S28", "pytest documentation, configuration (pytest 9 TOML config and strict mode). Testcontainers for Python guide", "Official, vendor"],
     ["S29", "\"Vite 8.0 is out!\" (March 2026). \"Announcing TypeScript 7.0\" (July 2026). create-vite react-ts template. ESLint v10 release", "Official"],
     ["S30", "WXT documentation. Playwright \"Chrome extensions\" guide", "Official"],
     ["S31", "mise documentation. Thoughtworks Technology Radar Vol 34 (April 2026)", "Official, vendor opinion"],
     ["S32", "Docker library documentation for PostgreSQL 18 (new data directory). PostgreSQL 18 release notes", "Official"],
     ["S33", "GitHub Docs: rulesets, secure use of Actions, licensing. GitHub Changelog: SHA-pinning policy (Aug 2025), Dependabot uv support (Mar 2025) and cooldown (Jul 2026), Secret Protection and Code Security (Mar 2025)", "Vendor"],
     ["S34", "Conventional Commits 1.0.0. DORA, trunk-based development and delivery metrics (updated Jan 2026)", "Standard, official"],
     ["S35", "MADR 4.0.0 (adr.github.io). C4 model (c4model.com). Diátaxis (diataxis.fr)", "Official"],
     ["S36", "Google Engineering Practices: \"Small CLs\" and \"The Standard of Code Review\"", "Official (Google)"],
     ["S37", "OWASP ASVS 5.0. NIST SP 800-218 (SSDF 1.1). OWASP SSRF Prevention Cheat Sheet. OWASP Top 10 for LLM Applications 2025", "Standard"],
     ["S38", "structlog \"Logging Best Practices\". OpenTelemetry Python documentation", "Official"],
     ["S39", "\"SQLAlchemy 2.1.0 Released\" (Sep 2026). Alembic \"The Importance of Naming Constraints\". RFC 9562 (UUIDs)", "Official, standard"],
     ["S40", "RFC 9457 Problem Details for HTTP APIs. Google AIP-158 (pagination), AIP-185 (versioning). FastAPI pull request 15951 (closed, not merged)", "Standard, official"],
     ["S41", "Anthropic, \"Building effective agents\" (Dec 2024) and \"Demystifying evals for AI agents\" (Jan 2026). Simon Willison, \"Agentic Engineering Patterns\" (Feb 2026)", "Vendor, secondary"],
     ["S43", "Kirsten Westeinde, Shopify Engineering, \"Deconstructing the Monolith: Designing Software that Maximizes Developer Productivity\" (21 Feb 2019). Quote: \"re-organize it by real-world concepts (like orders, shipping, inventory, and billing)\"", "Secondary (company engineering blog)"],
     ["S44", "Jimmy Bogard, \"Vertical Slice Architecture\" (19 Apr 2018). Quote: \"Minimize coupling between slices, and maximize coupling in a slice.\"", "Secondary (expert)"],
     ["S45", "import-linter 2.15 (4 Sep 2026, BSD licence) on PyPI and its documentation: contract types forbidden, protected, layers, independence, acyclic siblings", "Official"],
     ["S42", "Claude Code documentation: \"Best practices\", \"How Claude remembers your project\" (target under 200 lines), hooks, skills, subagents, security", "Vendor"]],
    ["7%", "78%", "15%"]) + "</div>",
    "Sources S25 to S45 were checked on 6 October 2026. Full notes, versions and unverified items are in research file R4."))

html = f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>seo-advisor requirements</title><style>{CSS}</style></head><body>{''.join(P)}<script>window.mermaidDone = true;</script></body></html>"
OUT_HTML.write_text(html, encoding="utf-8")
print("wrote", OUT_HTML, "pages:", len(P))

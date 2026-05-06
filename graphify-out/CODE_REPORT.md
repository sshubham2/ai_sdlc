# Graph Report - C:\Users\sshub\ai_sdlc  (2026-05-06)

## Corpus Check
- 50 files · ~70,733 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 40 nodes · 74 edges · 8 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `assemble()` - 11 edges
2. `main()` - 9 edges
3. `safe_str()` - 8 edges
4. `render_finding_card()` - 7 edges
5. `esc()` - 5 edges
6. `render_progress_block()` - 4 edges
7. `render_sidebar()` - 4 edges
8. `build_dependencies()` - 4 edges
9. `card_severity_class()` - 3 edges
10. `pill_severity_class()` - 3 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities

### Community 0 - "assemble.py"
Cohesion: 0.39
Nodes (8): assemble(), load_findings(), main(), md_to_html(), parse_prior_state(), assemble.py — composes diagnose-out/diagnosis.html from per-pass artifacts.  Out, read_optional(), render_hero()

### Community 1 - "safe_str()"
Cohesion: 0.47
Nodes (6): card_severity_class(), pill_severity_class(), Self-contained card with inline annotation form. data-severity drives live progr, render_finding_card(), safe_str(), severity_class()

### Community 2 - "main()"
Cohesion: 0.33
Nodes (6): assign_sc_ids(), confirmed_findings(), detect_cycles(), main(), parse_html_state(), Extract embedded JSON state from diagnosis.html.

### Community 3 - "build_backlog.py"
Cohesion: 0.47
Nodes (5): priority_score(), build_backlog.py — turn confirmed findings from a diagnose-out/ into backlog.md., render_backlog(), risk_profile(), topo_with_priority()

### Community 4 - "render_progress_block()"
Cohesion: 0.5
Nodes (4): Live progress counter for the sidebar. Numbers populated from JS., TOC + live progress counter., render_progress_block(), render_sidebar()

### Community 5 - "build_dependencies()"
Cohesion: 0.5
Nodes (4): build_dependencies(), evidence_files(), graphify_blast_radius(), _parse_text_nodes()

### Community 6 - "get_findings()"
Cohesion: 0.67
Nodes (3): get_findings(), load_findings_fallback(), Fallback: load findings from per-pass YAMLs.

### Community 7 - "esc()"
Cohesion: 1.0
Nodes (2): esc(), render_resolved_section()

## Knowledge Gaps
- **7 isolated node(s):** `assemble.py — composes diagnose-out/diagnosis.html from per-pass artifacts.  Out`, `Self-contained card with inline annotation form. data-severity drives live progr`, `Live progress counter for the sidebar. Numbers populated from JS.`, `TOC + live progress counter.`, `build_backlog.py — turn confirmed findings from a diagnose-out/ into backlog.md.` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `esc()`** (2 nodes): `esc()`, `render_resolved_section()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
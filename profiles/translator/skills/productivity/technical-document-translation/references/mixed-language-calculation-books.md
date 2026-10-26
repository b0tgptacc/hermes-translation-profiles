# Mixed-language calculation books and drawing sets

Use this when the requested source language appears only in labels, notes, load cases, or drawings while most of a long PDF is already in another language.

## Scope decision

- Translate only the language the user requested unless they explicitly ask to translate the existing English too.
- State that the output is a **page-linked companion translation**, not an in-place translated drawing.
- Preserve formulas, Latin profile marks, coordinates, load combinations, element IDs, and existing English.

## Extraction and coverage

1. Extract with page boundaries preserved.
2. Select every line containing source-language characters and retain its source-page marker.
3. Record PDF extractor warnings. Missing CMaps or font maps mean the recovered text may not cover every visible glyph; disclose that limitation.
4. Absence of extracted source-language text on a page is not the same as a missing page. Report pages with extractable source text, not a misleading “missing-page” count.

## Companion format

For each source-bearing page:

```markdown
<!-- SOURCE_PAGE 74 -->
## Страница 74

Оригинал: ...
Перевод: ...
```

Keep repeated lines; repetitions on drawings can be positionally meaningful.

## Deterministic reconstruction

Parallel workers sometimes duplicate page markers, emit empty pairs, or trim lines. Treat their files as provisional.

1. Build an exact ordered list of source lines containing source-language characters.
2. Parse worker `Оригинал` → `Перевод` pairs into a mapping.
3. Reconstruct the chunk from the source order, inserting each page marker once.
4. Verify:
   - source and `Оригинал` sequences match exactly after trimming outer whitespace;
   - pair counts match;
   - page markers are unique, sorted, and equal to the source-bearing page set;
   - target lines contain no source-language ideographs;
   - numeric and Latin identifier sequences are preserved.

Use `scripts/verify_bilingual_fragments.py` for the final gate.

## Structural engineering terminology traps

- `组合梁`: steel–concrete composite beam; use the project-approved equivalent (e.g. «сталежелезобетонная балка»), not generic «комбинированная балка».
- `中梁` / `边梁`: internal beam / edge beam.
- `钢构件应力比`: utilization ratio of steel members by stress.
- `侧振成份`: translational vibration component, not necessarily “lateral” in a modal legend.
- `多遇地震`: frequent earthquake / frequent seismic action.
- `吊`: crane load in load combinations when context confirms it.
- `屋面雪`: roof snow load.
- `做法: 阶形现浇`: construction: stepped cast-in-place/monolithic; preserve grammatical agreement in the target language.

## OCR-fused marks

Extraction may insert Chinese glyphs into profile marks or coordinates, e.g. a profile resembling `HM2组44合X1梁75[39]` or a foundation mark resembling `DJ-29阶`.

- Restore a mark only when the surrounding repeated geometry makes it unambiguous and an independent reviewer confirms it.
- Otherwise preserve dimensions and mark the designation as requiring visual verification.
- Never convert a possibly fused structural mark into an invented word or number.
- If page rendering is unavailable, say so explicitly.

## Reviewer instructions

Reviewers should evaluate the requested-language translation only. Existing English intentionally preserved by scope is not a translation failure. Review:

- source-line coverage and identifiers;
- domain terminology;
- fused marks/profiles;
- numbers and formula tokens;
- repeated drawing labels;
- load-combination terminology.

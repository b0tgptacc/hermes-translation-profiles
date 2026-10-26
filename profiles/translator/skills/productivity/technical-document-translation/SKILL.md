---
name: technical-document-translation
description: "Use when translating long technical documents end-to-end."
version: 1.0.0
metadata:
  hermes:
    tags: [translation, pdf, technical-documents, quality-assurance]
    category: productivity
---

# Technical Document Translation

Produce a complete, editable, verified translation of a long technical PDF or document. This workflow is for standards, specifications, engineering reports, manuals, and other documents where omissions, shifted table cells, inconsistent terminology, or altered obligations are unacceptable.

## Required outcome

Deliver the translated artifact, not merely sample pages or a prose summary. Unless the user requests otherwise, produce:

- editable Markdown as the canonical translated text;
- Word `.docx` for editing;
- PDF for distribution;
- a clear unofficial-translation disclaimer when the translation is not certified.

## Workflow

### 1. Inspect before translating

1. Determine page count, encryption, text-layer coverage, tables, equations, and scans.
2. Prefer direct text extraction for text PDFs; use OCR only for image-only pages.
3. Preserve page boundaries using explicit markers such as `<!-- SOURCE_PAGE 17 -->`.
4. Record empty source pages rather than silently dropping them.
5. Render representative pages and every structurally important table when possible. A clean text layer can still scramble columns.

### 2. Establish terminology

Create a compact source→target glossary before parallel work. Include:

- document title and names of related standards;
- recurring engineering systems and process terms;
- modal verbs (`shall`, `应`, `必须`) and how obligations are expressed;
- abbreviations, units, drawing types, and regulatory names.

Use one canonical title for every cross-referenced standard. Do not let parallel translators invent local variants.

For Chinese–Russian petrochemical terminology, consult `references/chinese-russian-engineering.md`.

### 3. Split on page boundaries

- Split by source pages, normally 10–15 pages per chunk.
- Keep tables entirely within one chunk where practical.
- Prefix every page with its source-page marker.
- Give every translator the same glossary and the same instructions: translate fully, do not summarize, preserve numbering, tables, units, symbols, and page markers.

### 4. Translate in parallel

Parallelize independent chunks, but require each worker to write an absolute output path and report:

- page range;
- marker count;
- remaining source-language character count;
- any illegible or structurally ambiguous source area.

Treat worker self-reports as unverified until the parent checks the files.

### 5. Mechanical completeness gates

Before formatting, verify programmatically:

- translated page markers exactly equal the full source sequence;
- no non-empty source page maps to an empty translation page;
- no source-language ideographs remain outside intentionally preserved names;
- clause identifiers and numbered references from the source are represented in the target;
- standards, units, dates, acronyms, and table numbers are retained;
- suspiciously short page-length ratios are investigated.

Do not use character-count parity as proof of semantic completeness; it is only an anomaly detector.

### 6. Independent bilingual review — fail closed

Use reviewers who did not produce the translation. Divide the full document among them and require a report covering:

- omissions and invented meaning;
- numbers, units, standards, and table numbering;
- changed modality or obligations;
- inconsistent terminology;
- shifted table rows, units, or notes;
- misleading literal translations of domain terms.

A reviewer `FAIL` means the artifact is not deliverable. Apply every material correction, then rerun the gates. Do not merely attach the review report to a known-bad translation.

### 7. Table recovery rules

PDF text extraction often linearizes columns incorrectly. For every table with suspicious units or notes:

1. compare row labels and numbering with the source;
2. render and visually inspect the original page;
3. relocate units and notes by semantic fit only when the source page confirms it;
4. mark unresolved cells as requiring source confirmation instead of guessing;
5. verify the final number of columns and Markdown separators.

Typical red flags: area units attached to chemicals, currency attached to transport volume, imported-equipment notes attached to fuel, or row numbers shifted into subrows.

### 8. Build artifacts

Use Markdown as the single source of truth. Generate HTML/DOCX/PDF from the corrected Markdown so fixes propagate consistently.

- Insert source-page labels and page breaks.
- Use print CSS for A4, readable margins, heading hierarchy, table wrapping, widows/orphans, and page numbers.
- A translated PDF may have more pages than the source; preserve source-page markers rather than forcing identical pagination.
- If converting HTML with a headless browser, extract the produced PDF text afterward to confirm it rendered real text rather than blank pages.

### 9. Final verification

Required checks:

- all source-page markers present and ordered;
- source-language residue count is zero or explicitly justified;
- DOCX package opens as a valid ZIP/XML package and contains expected page breaks;
- PDF text extraction returns substantial Cyrillic/target-language text;
- first and last sections exist;
- representative pages are visually legible;
- all independent-review findings have been corrected;
- file sizes are non-zero and stable;
- optional SHA-256 hashes are recorded for integrity.

## Reporting

State:

- source page count and translated PDF page count;
- formats delivered;
- what was verified;
- material limitations, including uncertified status or unresolved source defects.

Never claim a translation is complete merely because all chunks returned. Completion requires aggregation, independent review, correction, artifact generation, and read-back verification.

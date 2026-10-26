---
name: format-preserving-translation
description: Preserve document structure during EN/ZH to RU translation.
version: 0.1.0
author: MASTER
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [translation, docx, pdf, ocr, russian, quality-assurance]
    category: productivity
    related_skills: [technical-document-translation, document-intelligence-pipelines, docx, pdf, powerpoint, xlsx, ocr-and-documents]
---

# Format-Preserving Translation

Translate English or Chinese technical documents into Russian using the active Hermes model only. Preserve the source package and layout where the format permits it, and fail closed when the requested fidelity cannot be proven.

## When to Use

- Translate DOCX, PPTX, XLSX, born-digital PDF, or scanned PDF to Russian.
- Preserve tables, formulas, identifiers, images, headers, footers, notes, links, page geometry, and styles.
- Produce an editable Russian master plus a rendered PDF when possible.
- Build a source-faithful facsimile translation for scanned PDFs.

Do not use external translation, OCR, storage, or document APIs. Do not overwrite the source file.

## Required Supporting Skills

Load these as applicable:

- `technical-document-translation` for glossary, chunking, bilingual review, and completeness gates.
- `document-intelligence-pipelines` for deterministic extraction and coverage accounting.
- `docx`, `powerpoint`, `xlsx`, `pdf`, and `ocr-and-documents` for format-specific work.

## Fidelity Classes

Assign one class before translation:

- `NATIVE_STRUCTURAL`: editable OOXML. Preserve the original package skeleton and modify only mapped text units.
- `PDF_NATIVE_LAYOUT`: born-digital PDF with reliable text coordinates. Preserve page geometry, but require render comparison.
- `SCANNED_LAYOUT_LOCKED`: scanned or unreliable-OCR PDF. Rebuild each physical page in Russian at the same page size, page number, margins, headings, tables, columns, notes, and block geometry. The output must have the same physical page count and must be readable without the source document.
- `FACSIMILE_EVIDENCE`: optional QA artifact only. Keep source pages unchanged for audit, but never use this as the user-facing translated document.
- `RECONSTRUCTED`: unconstrained OCR/layout reconstruction. Never call this format preservation; disclose all changed geometry.
- `BLOCKED`: encrypted, corrupted, incomplete coverage, unreadable source, or fidelity requirement cannot be met.

A scanned PDF cannot remain pixel-identical after Chinese or English glyphs are replaced by longer Russian text. The required deliverable is therefore `SCANNED_LAYOUT_LOCKED`: semantic and geometric equivalence with the same pagination, not identical pixels. If complete text cannot fit inside the locked page geometry above the minimum readable font size, return `BLOCKED — manual DTP required` rather than adding companion pages or silently changing pagination.

## Procedure

### 1. Intake and quarantine

1. Preserve the source read-only and compute SHA-256.
2. Validate signature/container, encryption, page/slide/sheet count, macros, OLE, external links, and ZIP expansion limits.
3. Inventory every structural unit. Each expected unit must end as `native_extracted`, `ocr_extracted`, `intentionally_empty`, `unsupported`, or `failed`.
4. Stop when `failed > 0`; use `PARTIAL` when material `unsupported > 0`.

Completion criterion: source manifest and fidelity class are recorded before translation.

### 2. Extract stable translation units

Every unit needs a stable locator, source language, context, protected tokens, and formatting constraints. Never send binary packages or raw OOXML to the model.

```json
{
  "unit_id": "docx:word/document.xml:p42",
  "part": "/word/document.xml",
  "container": "table:3/row:2/cell:4",
  "source_language": "zh",
  "source": "设计压力",
  "context": "equipment data table",
  "protected_tokens": ["MPa"],
  "max_lines": 2
}
```

Preserve formulas, standards, clause IDs, equipment tags, coordinates, units, dates, drawing numbers, field codes, and nonlinguistic identifiers exactly.

### 3. Translate with the active Hermes model

1. Establish separate EN→RU and ZH→RU glossaries.
2. Translate fully; never summarize.
3. Preserve modality: `shall`, `must`, `应`, and `必须` must remain obligations.
4. Keep stable unit IDs in every response.
5. Split on page or structural boundaries and keep tables whole.
6. Use delegated workers only when they inherit the same configured provider and receive the same glossary.

Completion criterion: every non-empty source unit has one non-empty target or an explicit blocking finding.

### 4. Reinsert deterministically

- DOCX: preserve paragraph/run properties, numbering, tables, relationships, fields, bookmarks, comments, revisions, footnotes/endnotes, headers/footers, text boxes, drawings, and OMML.
- PPTX: preserve slide masters, layouts, shapes, groups, notes, chart data, SmartArt, rotations, and text directions.
- XLSX: translate text values/comments only; preserve formulas, types, names, validations, merges, widths, heights, number formats, print areas, hidden state, and charts.
- PDF: prefer the source DOCX/PPTX/XLSX. Use overlay only for bounded labels with proven Unicode mapping and embedded Cyrillic fonts.
- Scanned PDF: use coordinate-aware DTP reconstruction. Preserve page size/count, margins, block order, table grid geometry, clause numbering, notes, and printed page numbers. Use facsimile output only as an internal QA reference.

Completion criterion: package validation passes and source structural counts match the output contract.

### 5. Render and verify

1. Render with the target office engine or PyMuPDF for PDF.
2. Check page count, clipping, overflow, collisions, blank pages, missing glyphs, table shifts, headers/footers, formulas, and vertical text.
3. Compare numbers, units, standards, clause identifiers, links, and source-language residue.
4. Independently review omissions, terminology, and changed obligations.
5. Report `PASS`, `PARTIAL`, or `BLOCKED`; never hide exceptions.

Completion criterion: editable artifact, rendered artifact, manifest, and QA report agree.

## Scanned-PDF Commands

Resolve the skill script under the active profile:

```text
$HERMES_HOME/skills/productivity/format-preserving-translation/scripts/pdf_facsimile.py
```

Use through `terminal`:

```bash
python "$HERMES_HOME/skills/productivity/format-preserving-translation/scripts/pdf_facsimile.py" inspect SOURCE.pdf --output manifest.json
python "$HERMES_HOME/skills/productivity/format-preserving-translation/scripts/pdf_facsimile.py" sample SOURCE.pdf --pages 6,30 --output sample.pdf --render-dir rendered
python "$HERMES_HOME/skills/productivity/format-preserving-translation/scripts/pdf_facsimile.py" extract SOURCE.pdf --pages 6,30 --output units.json
python "$HERMES_HOME/skills/productivity/format-preserving-translation/scripts/pdf_facsimile.py" build SOURCE.pdf translations.json --output translated-facsimile.pdf
python "$HERMES_HOME/skills/productivity/format-preserving-translation/scripts/pdf_facsimile.py" verify SOURCE.pdf translations.json translated-facsimile.pdf --output qa.json
```

The facsimile helper is an evidence tool, not the final deliverable. The final scanned-PDF renderer must consume a reviewed page-layout specification and emit one Russian output page for each selected source page:

```bash
python "$HERMES_HOME/skills/productivity/format-preserving-translation/scripts/pdf_layout_locked.py" build layout.json --output translated-layout-locked.pdf
python "$HERMES_HOME/skills/productivity/format-preserving-translation/scripts/pdf_layout_locked.py" verify layout.json translated-layout-locked.pdf --output qa.json
```

Its acceptance gates are: equal page count and dimensions, table/region geometry within declared tolerances, no overflow or missing glyphs, and bilingual review PASS.

## Pitfalls

- A text layer does not prove a PDF is born digital; scanned pages often carry noisy OCR over a full-page image.
- PDF→Markdown→translation→DOCX is reconstruction, not preservation.
- Character-count similarity is not semantic completeness.
- Replacing text across fragmented runs without an inline-code map loses emphasis and fields.
- LibreOffice may repaginate Microsoft Office files; qualify it against a golden corpus.
- Font substitution can change layout even when style names remain unchanged.
- Do not use the word `complete` until every source unit, page, and review finding has a terminal status.

## Verification

For every delivery record:

- source/output SHA-256;
- fidelity class;
- physical source and output page counts;
- translated unit count and unresolved count;
- source-language residue exceptions;
- structural invariants;
- renderer and font substitutions;
- visual inspection coverage;
- final `PASS`, `PARTIAL`, or `BLOCKED`.

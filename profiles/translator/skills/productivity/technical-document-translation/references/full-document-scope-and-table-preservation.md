# Full mixed-language document translation

Use this when a technical PDF contains multiple source languages and the user wants a Russian deliverable with tables preserved.

## Lock the scope

- “Translate Chinese to Russian” means translate Chinese and preserve existing English unless the user explicitly includes English.
- “Translate the document into Russian” means translate all non-Russian narrative text, including existing English.
- For a substantially mixed-language file, state the exact scope before launching a large fan-out. If the difference is hundreds of pages and the wording is ambiguous, clarify.
- A source-language-only result is a page-linked companion translation, not a fully translated document.

## Preserve calculations and tables

- Keep formulas, Latin profile marks, coordinates, load combinations, element IDs, and nonlinguistic codes unchanged.
- Use Markdown tables only when column boundaries are unambiguous.
- Use fenced `text` blocks for wide calculation tables, drawings, and damaged column layouts; preserve every source row and its order.
- Split work by extracted byte size, not a fixed page count. Isolate 50–130 KB schematic pages instead of placing them in ordinary 20-page batches.
- Never repair an OCR-fused profile or structural mark by guessing. Preserve it and annotate that visual confirmation is required.

## Completion gates

- Every physical source page, including empty pages, has one ordered `SOURCE_PAGE` marker.
- All source-language narrative is translated according to the locked scope.
- Numbers, coefficients, formulas, profile marks, table row counts, and standard identifiers survive deterministic comparison.
- Independent reviewers check prose ranges and schematic/table ranges separately.
- Final DOCX/PDF is generated from one corrected canonical source and read back before delivery.

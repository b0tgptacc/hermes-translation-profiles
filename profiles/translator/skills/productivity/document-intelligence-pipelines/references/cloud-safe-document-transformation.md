# Cloud-safe document transformation

Use this reference when creating a pseudonymized copy of an Office or PDF document for an external model while preserving useful structure and layout.

## Assurance boundary

- Encryption protects the local recovery bundle; it does not make an encrypted document useful to a cloud model.
- The transferable artifact is a separately generated pseudonymized copy.
- Call it `PASS_CLOUD_SAFE_COPY` only for the declared detector and format scope. Always warn that pseudonymization is not mathematical anonymity and retained dates, amounts, rare combinations, images, and layout may remain quasi-identifiers.
- Raw source bytes, extraction/OCR output, mappings, recovery keys, and tool results stay inside the local trust boundary.

## Required pipeline

1. Preserve the source; write a separate generically named output.
2. Validate signature/container and enforce limits before expansion or rasterization:
   - compressed input size;
   - ZIP entry count, per-entry size, total expanded size, expansion ratio, duplicate/encrypted entries;
   - PDF page count, xref count, per-page pixels and total rendered pixels.
3. Inventory every terminal package part as sanitized, removed, intentionally preserved, or blocked. Unknown binary parts block.
4. Extract text from all relevant OOXML XML, attributes, formulas/string constants, metadata, comments, notes, revisions, chart caches, shared/inline strings, names, relationships and thumbnails.
5. Block or explicitly handle macros, ActiveX, OLE/embedded packages, digital signatures, external links, attachments, JavaScript, forms and annotations.
6. Run deterministic DLP first. An optional trusted local/private model may add only exact source substrings; validate each returned substring against source text.
7. Use request-scoped, non-semantic pseudonyms. Same-length replacements that preserve whitespace and punctuation reduce reflow and allow run-spanning OOXML rewrites.
8. OCR every supported image/page requiring visual inspection in an isolated no-network worker. Treat its JSON as untrusted:
   - exact one-result-per-input cardinality;
   - unique exact filenames;
   - strict object/list/string/numeric types (reject booleans as integers);
   - positive geometry, bounded finite confidence;
   - fragment text must equal joined word text;
   - low-confidence counts must recompute exactly;
   - visible foreground without reliable OCR/VLM or recognized machine-code coverage blocks.
9. Permanently redact PDFs, remove active/external metadata, save non-incrementally with garbage collection, then reopen with a second parser.
10. Re-extract, re-render and re-OCR the output. Scan native text, XML, object streams and UTF-8/UTF-16 encodings for known originals. Any residual blocks and deletes the output.
11. Store the exact source and mapping in a local encrypted recovery bundle using a per-document data key wrapped by OS-bound key protection. Restrict the vault ACL.
12. Publish outputs and restores atomically. Write and fsync a same-directory temporary file, then use an exclusive atomic publication that cannot overwrite an existing destination; delete temporaries on every failure.

## Formatting rules

- Preserve styles, table/cell structure, formulas, page/slide/sheet geometry and supported image dimensions.
- Do not claim pixel identity. PDF replacement glyphs and redacted image regions may differ.
- Preserve alpha when supported. Block unsupported image modes and multi-frame images rather than silently flattening them.
- If a structure cannot be safely preserved and inspected, return `BLOCKED`, not a downgraded artifact presented as safe.

## Adversarial acceptance fixtures

Include at minimum:

- strings split across OOXML runs;
- formulas containing emails/secrets;
- hidden sheets/slides, comments, notes, headers/footers and thumbnails;
- phones, Luhn-valid cards, bank/tax identifiers, dates and monetary amounts;
- born-digital, scanned, mixed and oversized PDFs;
- ZIP bombs, duplicate entries, excessive package entries and unknown binaries;
- QR/barcode images, transparent PNG, multi-frame TIFF and low-confidence OCR;
- missing, duplicate, malformed and internally inconsistent OCR records;
- recovery with a wrong key, interrupted disk write and a concurrently existing destination;
- byte-exact restoration and confirmation that failure leaves no partial plaintext.

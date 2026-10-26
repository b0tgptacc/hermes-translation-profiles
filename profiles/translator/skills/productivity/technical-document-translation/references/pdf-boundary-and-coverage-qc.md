# Chinese–Russian Technical PDF Boundary and Coverage QC

Use this reference alongside `chinese-russian-engineering.md` for long standards split across parallel translators.

## Physical coverage versus declared coverage

A table of contents can list annexes or later sections that are not physically present in the supplied PDF. Before claiming completeness:

1. Count physical PDF pages and non-empty extracted pages.
2. Compare the final physical heading with the table of contents.
3. Check every declared appendix/annex actually has page content.
4. Translate only what exists; never reconstruct absent annexes.
5. State exactly which listed appendices or page ranges are absent from the supplied file.

## Chunk-boundary stitching

Page-boundary splitting can break a sentence, table row, or heading across two workers. Run a dedicated stitch pass after aggregation:

- inspect the final paragraph of every source chunk and the first paragraph of the next;
- look for duplicated or conflicting verbs (`могут быть` + `представлять`), missing conjunctions, split terminology, and tables interrupted by page markers;
- preserve the source-page marker while repairing the sentence around it;
- rerun the clause-number inventory after all replacements. A broad terminology replacement can accidentally strip a heading prefix such as `9.7`.

## Additional petrochemical terms

| Chinese | Preferred Russian | Pitfall |
|---|---|---|
| 净化压缩空气 / 非净化压缩空气 | очищенный / неочищенный сжатый воздух | Do not substitute осушенный/неосушенный unless drying is explicit. |
| 视镜 | смотровое стекло | Not «смотровой фонарь». |
| 公用系统管道及仪表流程图（UID） | схема трубопроводов и КИПиА общезаводских систем (UID) | Preserve the source abbreviation exactly; do not normalize to U&ID. |
| 长周期设备 | оборудование с длительным сроком изготовления (long-lead equipment) | Refers to procurement lead time, not operating cycle. |
| 物料 | технологическая среда / обрабатываемый продукт | In equipment data, not necessarily construction material. |
| 管道应力设计规定 | требования к анализу напряжений и обеспечению гибкости трубопроводов | Broader than a generic strength calculation. |
| 安全仪表系统 (SIS) | система противоаварийной автоматической защиты (ПАЗ; SIS) | Keep both Russian project term and source acronym. |
| 电信号配管 | защитные/кабельные трубы электрических сигнальных линий | Not «трубки электрических сигналов». |
| 系统冗余和后备 | избыточность (резервирование) и резервное обеспечение системы | Do not invent hot standby. |
| 扩音对讲系统 | система громкоговорящей и переговорной связи | Dispatch telephone is a separate system. |
| 水喷淋 / 水喷雾 | водяное орошение / водяное распыление | Do not automatically collapse into sprinkler/deluge terminology. |
| 总概算表 / 综合概算表 / 单位工程概算表 | таблица общей сметы / таблица комплексной сметы / смета по отдельному объекту строительства | Keep the three document classes distinct. |

## Post-edit gates

After reviewer corrections and terminology replacements:

- compare all clause identifiers (`1.1`, `9.7`, etc.) source-to-target again;
- verify table column counts and subrow numbering;
- search for every rejected old term from the review report;
- regenerate DOCX/PDF from the corrected canonical Markdown, then read both back;
- record missing physical annexes as a source limitation, not a translation omission.

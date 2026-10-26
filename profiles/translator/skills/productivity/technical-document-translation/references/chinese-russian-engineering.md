# Chinese–Russian Petrochemical Engineering Translation Notes

Use this reference for technical standards and FEED/basic-engineering documents. Confirm project-specific terminology with the client's glossary when available.

## Core terms

| Chinese | Preferred Russian | Notes |
|---|---|---|
| 石油化工工厂 | нефтехимический завод | Use consistently in document titles. |
| 基础工程设计 | базовое проектирование | May correspond to FEED depending on contract; do not silently substitute «рабочее проектирование». |
| 生产装置 | технологическая установка | |
| 公用工程 | общезаводские инженерные системы | Utilities. |
| 公用物料 | общезаводские инженерные среды | Steam, water, air, nitrogen, etc.; never generic «материалы». |
| 辅助设施 | вспомогательные объекты | |
| 总图 | генеральный план | |
| 储运 | хранение и транспортировка | |
| 给排水 | водоснабжение и канализация | |
| 供配电 | электроснабжение и распределение | |
| 过程控制 | управление технологическим процессом | |
| 设计专篇 | специальный раздел проектной документации | |
| 安全设施设计专篇 | специальный раздел по проектированию средств обеспечения безопасности | Keep 设计. |
| 职业病危害预评价报告 | отчёт о предварительной оценке вредных производственных факторов и риска профессиональных заболеваний | Use one canonical form. |
| 三废 | сточные воды, отходящие газы и твёрдые отходы | Avoid literal «три вида отходов». |
| 旁滤 | фильтрация части потока | Side-stream filtration; «байпасная» may be understood but is less precise. |
| 泡沫消防水 | вода для пенного пожаротушения | Not premixed foam solution unless the source says so. |
| 防渗漏 | противофильтрационная защита | Especially for underground wastewater structures and landfills. |
| 生产执行系统 | система управления производственными операциями (MES) | Preserve MES. |
| 网闸 | шлюз сетевой изоляции | Not a generic network gateway. |
| 设备网络 | сеть полевых устройств | Context may include fieldbus. |
| 换热站 | теплообменная станция | Use one term throughout the section. |
| 火炬气回收 | рекуперация факельного газа | Flare gas recovery; not generic disposal. |
| 仪表空气 | воздух КИПиА | |
| 污泥 | осадок (шлам) | |
| 污油 | уловленные нефтепродукты / загрязнённое нефтяное масло | Do not merge with 污泥. |
| 维修 | ремонтное хозяйство | In plant-wide facility sections; do not automatically add maintenance. |
| 在线监测 | непрерывный (онлайн-) мониторинг | |

## Drawing and system abbreviations

Preserve source abbreviations and define them once when useful: PFD, UFD, P&ID, U&ID, UEPD, DCS, SIS, PLC, SCADA, GDS, MES, ERP, CRM, SCM, OA, EIP.

## Table-specific checks

- Confirm every unit against the rendered source page.
- Imported-equipment notes belong to equipment totals, not utilities.
- `万元` means ten thousand yuan and normally belongs to investment/cost rows.
- `104m2` in extracted text usually represents `10⁴ m²`; verify which row owns it.
- `m³/a`, `m³/h`, `t/a`, `kg/h`, `MPaG`, and `Nm³/h` are easy to shift by one row during PDF extraction.
- Subrows `(1)…(n)` should not inherit main-row numbers accidentally.

## Legal status

Unless certified, label the artifact as an unofficial translation and require comparison with the Chinese original for contractual, regulatory, or legal use.

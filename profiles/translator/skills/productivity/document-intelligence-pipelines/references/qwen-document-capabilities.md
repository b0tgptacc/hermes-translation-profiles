# Qwen document-capability boundaries

Use this reference when a Qwen-family model is proposed for document parsing or OCR. Verify current upstream documentation before deployment; product names and serving behavior change.

## Capability separation

- A native vision-language checkpoint can accept image/video inputs only when the serving stack loads the matching multimodal processor and exposes a compatible request schema.
- Direct PDF/DOCX/XLSX ingestion is a framework or hosted-product feature unless the checkpoint documentation explicitly says otherwise.
- Qwen-Agent DocParser is preprocessing and retrieval: it parses supported files, chunks them, applies retrieval, and sends selected structured text to the model. It is not proof of visual OCR for scans.
- Qwen-VL document formats, Qwen-OCR tasks, and Qwen-Doc hosted extraction are separate products. Do not attribute their layout, OCR, rotation, PDF, or strict-schema guarantees to another checkpoint.
- JSON syntax or JSON Schema validates shape, not semantic fidelity to the source document.

## Qwen3.8-27B baseline

The official Qwen3.8-27B model card describes a native vision-language 27B dense model, with native context length 262,144 and optional extension toward 1,000,000 through serving configuration. The same card does not establish that every downstream alias or OpenAI-compatible deployment exposes vision, tool parsing, or the same context window.

Before relying on a deployment, record:

1. exact model/checkpoint and quantization;
2. serving engine and version;
3. multimodal processor loaded;
4. text and image request contracts;
5. tool-call parser/chat template;
6. structured-output mode actually supported;
7. configured context/output limits.

## Endpoint acceptance fixture

Run under the network mode that can actually reach the service:

- text sentinel returns exact expected text;
- one harmless tool call has valid name/arguments and completes a round trip;
- a small image with known printed text tests `image_url` handling;
- a layout fixture tests table/coordinate fidelity;
- malformed structured output triggers local validation and bounded retry;
- source coordinates survive through the final answer.

For VPN-only endpoints that cannot coexist with the current operator profile, static preparation is valid but must be reported as `PASS STATIC / LIVE NOT RUN — VPN ONLY`, never as full runtime acceptance.

## Primary sources

- Qwen3.8-27B model card: https://huggingface.co/Qwen/Qwen3.8-27B
- Qwen function calling: https://qwen.readthedocs.io/en/latest/framework/function_call.html
- Qwen-Agent RAG / DocParser: https://qwenlm.github.io/Qwen-Agent/en/guide/core_moduls/rag
- Qwen3-VL document parsing cookbook: https://raw.githubusercontent.com/QwenLM/Qwen3-VL/main/cookbooks/document_parsing.ipynb
- Qwen OCR documentation: https://www.alibabacloud.com/help/en/model-studio/qwen-vl-ocr
- pypdf extraction vs OCR: https://pypdf.readthedocs.io/en/latest/user/extract-text.html
- PyMuPDF OCR guidance: https://pymupdf.readthedocs.io/en/latest/recipes-ocr.html

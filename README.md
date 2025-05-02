# vLLM Think Formatter

This [OpenWebUI Filter Function](https://openwebui.com/f/rjtpp/vllm_think_formatter) post-processes responses from vLLM-based reasoning models to fix formatting issues and improve readability.

## 💡 What It Does

- Detects and wraps reasoning content (`<think>...</think>` or custom tags) in a collapsible `<details>` block.
- Automatically inserts a missing `<think>` tag when only `</think>` is present (common in some vLLM outputs).
- Displays a summary showing how long the model took to generate the reasoning.
- Formats reasoning lines as blockquotes (`>`) to match OpenWebUI’s visual styling.

> [!NOTE]  
> This filter processes responses **after the full output is generated**. It does not modify content during streaming.
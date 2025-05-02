# vLLM Think Formatter

This [OpenWebUI Filter Function](https://openwebui.com/f/rjtpp/vllm_think_formatter) post-processes responses from vLLM-based reasoning models to fix formatting issues and improve readability.

## 💡 What It Does

There are two methods for formatting reasoning content:

### Steaming Formatting (v1.3.0+)

- Injects the opening `<think>` tag into the first streamed chunk to ensure reasoning is wrapped correctly during live generation.


### Post-Processing

- Detects and wraps reasoning content (default: `<think>...</think>`) in a collapsible `<details>` block.
- Automatically inserts a missing `<think>` tag when only `</think>` is present (common in vLLM outputs).
- Displays a summary showing how long the model took to generate the reasoning.
- Formats reasoning lines as blockquotes (`>`) to match OpenWebUI's visual styling.

> [!NOTE]  
> **Streaming support** was introduced in **v1.3.0**, allowing the filter to inject a `<think>` tag into the first streamed chunk.  
> However, this may not work consistently across all setups, and the filter does **not check for `</think>`** before injecting the opening tag.

## ⚙️ Configuration

You can customize the `Valves` class in the settings.

| Field             | Default       | Description                                            |
|-------------------|---------------|--------------------------------------------------------|
| `THINK_TAG_OPEN`  | `<think>`     | The opening tag used to mark reasoning content.        |
| `THINK_TAG_CLOSE` | `</think>`    | The closing tag used to mark reasoning content.        |
| `USE_STREAMING`   | `True`        | Enables streaming-based tag injection and timing.      |


> [!TIP]  
> Long reasoning outputs can still cause some lag when expanding the `<details>` block in OpenWebUI — especially during streaming.  
> Setting `USE_STREAMING = False` may slightly improve performance by preventing blockquote rendering until the full response is complete.  
> For best results, avoid expanding the reasoning block while it’s still being generated.
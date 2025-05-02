"""
title: vLLM Think Formatter
author: RJTPP
author_url: https://github.com/RJTPP
repo_url: https://github.com/RJTPP/open-webui-vllm-think-formatter
version: 1.2.1
license: MIT

Description:
This filter post-processes vLLM responses by wrapping reasoning content in a collapsible <details> block.
It fixes missing <think> tags and formats the output after the full response has been generated (not during streaming).
Useful when using vLLM APIs that return </think> but omit the starting <think> tag.
"""
from pydantic import BaseModel, Field
from time import time
import re


class Filter:
    
    class Valves(BaseModel):  
        THINK_TAG_OPEN: str = Field(
            default="<think>", description="The reasoning open tag. Default: <think>"
        )
        THINK_TAG_CLOSE: str = Field(
            default="</think>", description="The reasoning close tag. Default: </think>"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.start_think = None
        self.end_think = None
        pass

    def inlet(self, body, **kwargs):
        self.start_think = time()
        self.end_think = None
        return body
    
    def stream(self, event: dict) -> dict:
        if self.end_think:
            return event
        
        for choice in event.get("choices", []):
            delta = choice.get("delta", {})
            if "content" in delta:
                if self.valves.THINK_TAG_CLOSE in delta["content"]:
                    self.end_think = time()
                    break
        return event

    def outlet(self, body, **kwargs):
        text = body["messages"][-1]["content"]
        elapsed = int((self.end_think or time()) - self.start_think)
        think_summary = f"<details>\n<summary>Thought for {elapsed} seconds</summary>\n\n"
        think_end = "\n</details>"

        # Patch missing <think> tag
        if self.valves.THINK_TAG_CLOSE in text and not text.lstrip().startswith(self.valves.THINK_TAG_OPEN):
            text = f"{self.valves.THINK_TAG_OPEN}\n" + text

        think_content = self.extract_think_content(text)
        respond_content = self.extract_after_think(text)

        if think_content is None or respond_content is None:
            return body  # Skip formatting if tags are not found

        # Format reasoning block as quote
        think_content = ">" + think_content.replace("\n", "\n>")

        # Combine everything
        text = f"{think_summary}{think_content}\n{think_end}{respond_content}"
        body["messages"][-1]["content"] = text
        return body
    
    
    def extract_think_content(self, text: str) -> str | None:
        match = re.search(rf"{self.valves.THINK_TAG_OPEN}(.*?){self.valves.THINK_TAG_CLOSE}", text, re.DOTALL)
        return match.group(1).strip() if match else None


    def extract_after_think(self, text: str) -> str | None:
        match = re.search(rf"{self.valves.THINK_TAG_CLOSE}\s*(.*)", text, re.DOTALL)
        return match.group(1).strip() if match else None

"""
title: vLLM Think Formatter
author: RJTPP
author_url: https://github.com/RJTPP
version: 1.1.0

This filter post-processes vLLM responses by wrapping reasoning content in a collapsible <details> block.
It fixes missing <think> tags and formats the output after the full response has been generated (not during streaming).
Useful when using vLLM APIs that return </think> but omit the starting <think> tag.
"""
from pydantic import BaseModel, Field
from time import time
import re


class Filter:
    
    class Valves(BaseModel):  
        THINK_TAG_START: str = Field(
            default="<think>", description="The reasoning open tag. Default: <think>"
        )
        THINK_TAG_END: str = Field(
            default="</think>", description="The reasoning close tag. Default: </think>"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.start_think = None
        pass

    def inlet(self, body, **kwargs):
        self.start_think = time()
        return body

    def outlet(self, body, **kwargs):
        text = body["messages"][-1]["content"]
        think_summary = f"<details>\n<summary>Thought for {int(time() - self.start_think)} seconds</summary>\n\n"
        think_end = "\n</details>"

        # Patch missing <think> tag
        if self.valves.THINK_TAG_END in text and not text.lstrip().startswith(self.valves.THINK_TAG_START):
            text = f"{self.valves.THINK_TAG_START}\n" + text

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
        match = re.search(rf"{self.valves.THINK_TAG_START}(.*?){self.valves.THINK_TAG_END}", text, re.DOTALL)
        return match.group(1).strip() if match else None


    def extract_after_think(self, text: str) -> str | None:
        match = re.search(rf"{self.valves.THINK_TAG_END}\s*(.*)", text, re.DOTALL)
        return match.group(1).strip() if match else None

"""
title: vLLM Think Formatter
author: RJTPP
author_url: https://github.com/RJTPP
git_url: https://github.com/RJTPP/open-webui-vllm-think-formatter.git
repo_url: https://github.com/RJTPP/open-webui-vllm-think-formatter
version: 1.3.0
license: MIT

Description:
This filter post-processes vLLM responses by wrapping reasoning content in a collapsible <details> block.
It also patches missing <think> tags and tracks reasoning time by detecting the </think> tag during streaming.
Useful for vLLM APIs that return a closing </think> tag but omit the opening <think> tag.
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
        USE_STREAMING: bool = Field(
            default=True, description="Use streaming mode. Default: True"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.start_think = None
        self.end_think = None
        self.is_starting = False

    def inlet(self, body: dict, **kwargs) -> dict:
        self.is_starting = True
        self.start_think = time()
        self.end_think = None
        return body
    
    def stream(self, event: dict, **kwargs) -> dict:
        if self.end_think or (self.valves.USE_STREAMING and not self.is_starting):
            return event
        
        for choice in event.get("choices", []):
            delta = choice.get("delta", {})
            if "content" in delta:
                if self.valves.USE_STREAMING and self.is_starting and self.valves.THINK_TAG_OPEN not in delta["content"]:
                    delta["content"] = f"{self.valves.THINK_TAG_OPEN}\n{delta['content']}"
                    self.is_starting = False
                if self.valves.THINK_TAG_CLOSE in delta["content"]:
                    self.end_think = time()
                    break
        return event

    def outlet(self, body: dict, **kwargs) -> dict:
        if self.valves.USE_STREAMING:
            return body
        
        text = body["messages"][-1]["content"]
        elapsed = int((self.end_think or time()) - self.start_think)
        think_summary = f"<details>\n<summary>Thought for {elapsed} {'second' if elapsed == 1 else 'seconds'}</summary>\n\n"
        think_end = "\n</details>"

        # Patch missing <think> tag
        if self.valves.THINK_TAG_CLOSE in text and not text.lstrip().startswith(self.valves.THINK_TAG_OPEN):
            text = f"{self.valves.THINK_TAG_OPEN}\n" + text

        think_content = self.extract_think_content(text)
        respond_content = self.extract_after_think(text)

        # Skip formatting if tags are not found
        if think_content is None or respond_content is None:
            return body

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

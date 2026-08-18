"""YACUNP Local LLM category nodes."""

from .generate_text import YacunpGenerateText
from .load_model_llama_cpp import YacunpLoadModelLlamaCpp
from .load_model_lmstudio import YacunpLoadModelLMStudio
from .make_advanced_llm_arguments import YacunpMakeAdvancedLLMArguments
from .make_basic_llm_arguments import YacunpMakeBasicLLMArguments
from .system_prompt_presets import YacunpSystemPromptPresets
from .unload_model import YacunpUnloadModel

NODES = [
    YacunpMakeBasicLLMArguments,
    YacunpMakeAdvancedLLMArguments,
    YacunpLoadModelLlamaCpp,
    YacunpLoadModelLMStudio,
    YacunpSystemPromptPresets,
    YacunpGenerateText,
    YacunpUnloadModel,
]

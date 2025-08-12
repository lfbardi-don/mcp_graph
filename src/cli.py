from langchain_core.messages import HumanMessage, SystemMessage
from prompt import SYSTEM_PROMPT

# Maps for user input selections
SIZE_MAP = {"1": "512x512", "2": "768x768", "3": "1024x1024"}
STYLE_MAP = {"1": "digital-art", "2": "photorealistic", "3": "anime", "4": "watercolor"}


def prompt_for_image_request() -> tuple[str, str, str, SystemMessage]:
    size_sel = input("\nChoose image size:\n\n1) 512x512\n2) 768x768\n3) 1024x1024\n\n-> ").strip()
    style_sel = input("\nChoose image style:\n\n1) digital-art\n2) photorealistic\n3) anime\n4) watercolor\n\n-> ").strip()

    size = SIZE_MAP.get(size_sel, "512x512")
    style = STYLE_MAP.get(style_sel, "digital-art")

    prompt = input("\nPlease provide a detailed description of the scene or subject you want:\n\n-> ").strip()

    system_msg = SystemMessage(content=SYSTEM_PROMPT)
    return size, style, prompt, system_msg


def build_human_message(size: str, style: str, prompt: str) -> HumanMessage:
    return HumanMessage(content=f"Create an image with size {size} and style {style}. {prompt}")

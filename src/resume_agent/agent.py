import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from resume_agent.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

load_dotenv()


def extract_json(text: str) -> dict:
    text = text.strip()

    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(f"没有找到 JSON 内容，原始返回：\n{text}")

    json_str = text[start:end + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"JSON 解析失败：{e}\n原始内容：\n{json_str}"
        )


def analyze_resume(
    profile: str,
    resume: str,
    jd: str,
    api_key: str | None = None,
) -> dict:
    """
    api_key:
      - 如果传了，就用调用方提供的 Key
      - 如果没传，就回退到环境变量 DEEPSEEK_API_KEY
    """
    key = api_key or os.getenv("DEEPSEEK_API_KEY")

    if not key:
        raise ValueError(
            "没有可用的 DeepSeek API Key。"
            "请在页面上填写你自己的 Key，或配置环境变量。"
        )

    client = OpenAI(
        api_key=key,
        base_url="https://api.deepseek.com",
    )

    user_prompt = USER_PROMPT_TEMPLATE.format(
        profile=profile,
        resume=resume,
        jd=jd,
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    return extract_json(content)
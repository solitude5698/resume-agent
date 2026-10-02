import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from resume_agent.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def extract_json(text: str) -> dict:
    """
    从模型返回的文本里提取 JSON。
    兼容三种情况：
    1. 纯 JSON
    2. ```json ... ``` 包裹
    3. JSON 后面还有多余解释文字
    """
    text = text.strip()

    # 情况 2：被 ```json ... ``` 包裹
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()

    # 情况 3：从第一个 { 到最后一个 }
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


def analyze_resume(profile: str, resume: str, jd: str) -> dict:
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
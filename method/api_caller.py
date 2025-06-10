import openai
from openai import OpenAI
import dashscope
from dashscope import Generation


def _call_deepseek_api(prompt: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )

    return response.choices[0].message.content


def _call_openai_api(prompt: str, api_key: str) -> str:
    """
    调用 OpenAI ChatGPT API
    """
    try:
        # 设置 API 密钥
        openai.api_key = api_key

        # 调用 ChatGPT API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 可替换为 gpt-4
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=512,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        # 返回生成内容
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[OpenAI API Error] {str(e)}"


def _call_qwen_api(prompt: str, api_key: str) -> str:
    """
    调用阿里云 Qwen API
    """
    try:
        # 设置 DashScope API 密钥
        dashscope.api_key = api_key

        # 初始化生成模型
        generation = Generation(model="qwen-max")  # 可替换为 qwen-plus 或 qwen-turbo

        # 发起请求
        response = generation.call(
            prompt=prompt,
            temperature=0.7,
            top_p=0.8,
            max_tokens=512
        )

        # 返回生成内容
        return response.output.text.strip()

    except Exception as e:
        return f"[Qwen API Error] {str(e)}"

import requests
import json
import yaml

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)



def call_chatanywhere_api(user_prompt_json_str):
    """
    接受一个 JSON 字符串（来自你的询诊数据），
    自动构造 prompt，调用 ChatAnywhere API，
    返回模型生成结果。
    """

    config = load_config()
    url = config["api"]["base_url"]
    key = config["api"]["api_key"]

    # url = "https://api.chatanywhere.tech/v1/chat/completions"

    headers = {
        "Authorization": f"{key}",
        "Content-Type": "application/json"
    }

    # 允许输入既可以是 dict 也可以是 str
    if isinstance(user_prompt_json_str, str):
        try:
            data_json = json.loads(user_prompt_json_str)
        except Exception as e:
            raise ValueError(f"提供的 user_prompt_json_str 不是合法 JSON 字符串: {e}")
    else:
        data_json = user_prompt_json_str

    # 构造 prompt：让模型基于 JSON 生成医学总结、初步诊断、诊疗建议
    system_prompt = f"""
    你是一名三甲医院主治医师，你需要根据给定的问诊 JSON 数据，
    给出本次和患者的 JSON 格式的问诊对话总结：
    1) 本次问诊总结（要言简意赅） 
    2) 初步诊断（基于医生内容提取关键疾病） 
    3) 诊疗建议（医生提供的诊疗方案浓缩）。
    所有输出必须基于文本内容，不得杜撰未出现的医学信息。请直接提供这个问诊对话总结，无需包含任何问候语或重复任何其他内容。
"""

    user_prompt = f"""
下面是完整的问诊 JSON 数据：

{json.dumps(data_json, ensure_ascii=False, indent=2)}


【输出要求】
- 必须输出 **严格 JSON 格式**
- 不要包含额外解释
- 字段必须是：
  - 本次问诊总结
  - 初步诊断
  - 诊疗建议

【输出 JSON 样例】
{{
  "本次问诊总结": "……",
  "初步诊断": "……",
  "诊疗建议": "……"
}}

"""

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"请求失败: {response.status_code}, {response.text}")


# ==========================
# 示例：如何使用
# ==========================
if __name__ == "__main__":
    # 假设 your_json_str 就是你贴出来的那个超长 JSON
    your_json_str = """{ ...  ... }"""

    result = call_chatanywhere_api(your_json_str)
    print(json.dumps(result, ensure_ascii=False, indent=2))



# 请基于其中的信息生成 JSON 格式的医学总结（问诊总结、初步诊断、诊疗建议），样例格式为：
# "{
#     "本次问诊总结" : "患者连续三天无法正常进入睡眠，医生判断为甲亢复发，需要尽快到线下就诊，必要时候需要进行手术。",
#     "初步诊断" : "甲亢复发",
#     "诊疗建议" : "禁食海鲜，保持良好情绪。服用甲巯咪唑每天一次3/4片。尽快线下就诊。"
# }"
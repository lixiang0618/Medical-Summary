import pandas as pd
import json
import numpy as np

def to_python_type(x):
    """将 numpy 类型转换成 Python 类型，避免 JSON 报错"""
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if pd.isna(x):
        return None
    return x

def build_summary_json(
        consult_id,
        details_file="./original_data/detail.xlsx"
    ):
    """
    根据 consult_id 从 detail.xlsx 查找记录，
    重命名字段 → 构造成 JSON 字符串 → 返回。
    """

    # 读取 detail 表
    df = pd.read_excel(details_file)

    # 查找记录
    record = df[df["id"] == consult_id]
    if record.empty:
        raise ValueError(f"detail.xlsx 中未找到 id={consult_id} 的记录")

    record = record.iloc[0]

    # 字段映射：原列名 → 新列名
    mapping = {
        "id": "id",
        "uid": "uid",
        "bc_title_type": "问诊类型",
        "disease_description": "患者疾病描述",
        "height_weight": "身高体重",
        "disease": "疾病名称",
        "allergy_history": "过敏史",
        "disease_duration": "患病时长",
        "hospital_department": "线下就诊过的医院",
        "medication_situation": "用药情况",
        "hope_help": "患者希望的帮助",
        "past_history": "病史",
        "suggestions_summary": "医生提供患者的问诊总结",
        "suggestions_primary": "医生提供患者的初步诊断",
        "suggestions_dispose": "医生提供患者的诊疗建议",

        # 你特别强调要加入的字段
        "msgboard": "本次对话详情",
        "other_communication": "患者与医生其他问诊",
    }

    # 构造最终 JSON 数据
    final_data = {}

    for old_key, new_key in mapping.items():
        if old_key in record:
            final_data[new_key] = to_python_type(record[old_key])
        else:
            final_data[new_key] = None

    # 最外层再套一层 JSON
    result = {
        "consult_id": consult_id,
        "data": final_data
    }

    # 转成字符串（现在不会报错）
    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    return json_str


# 示例调用
# print(build_summary_json(3571))

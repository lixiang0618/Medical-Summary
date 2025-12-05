import pandas as pd

# ===== 全局缓存，只加载一次 =====
_df_details = None
_df_list = None
_df_doctor = None

def load_data(details_file, list_file, doctor_file):
    global _df_details, _df_list, _df_doctor
    if _df_details is None:
        print("⏳ 正在加载Excel数据（仅首次加载）...")
        _df_details = pd.read_excel(details_file)
        _df_list = pd.read_excel(list_file)
        _df_doctor = pd.read_excel(doctor_file)
        print("✅ Excel 数据加载完毕。\n")


def get_full_record(consult_id,
                    details_file="./original_data/detail.xlsx",
                    list_file="./original_data/list.xlsx",
                    doctor_file="./original_data/糖尿病医生信息.xlsx"):

    # 1. 加载全局数据
    load_data(details_file, list_file, doctor_file)

    df_details = _df_details
    df_list = _df_list
    df_doctor = _df_doctor

    # 2. 查 details
    record = df_details[df_details["id"] == consult_id]
    if record.empty:
        print(f"❌ details.xlsx 中未找到 id={consult_id}")
        return None

    # 3. 获取关联 id
    bingcheng_id = record["bingcheng_id"].iloc[0]
    doctor_id = record["doctor_id"].iloc[0]

    # 4. list.xlsx 映射
    record_list = df_list[df_list["bingcheng_id"] == bingcheng_id]
    record_list = record_list.head(1)  # 强制只取 1 条

    # 5. 医生信息表
    record_doc = df_doctor[df_doctor["doctor_id"] == doctor_id]
    record_doc = record_doc.head(1)  # 强制只取 1 条

    # 6. 横向拼接
    merged = pd.concat(
        [record.reset_index(drop=True),
         record_list.reset_index(drop=True),
         record_doc.reset_index(drop=True)],
        axis=1
    )

    print("✅ 合并后的唯一完整记录：")
    print(merged)

    return merged


# ==== 示例 ====
get_full_record(11)

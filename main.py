# main.py
import argparse
from SQL_summary_json import build_summary_json
from model_calling import call_chatanywhere_api
from rich import print_json


def main():
    parser = argparse.ArgumentParser(description="Generate medical summary by ID")
    parser.add_argument("id", type=int, help="Record ID")
    args = parser.parse_args()

    # 生成 JSON
    summary_json = build_summary_json(args.id)
    print(f"[INFO] Generated JSON for ID={args.id}")

    # 模型调用
    result = call_chatanywhere_api(summary_json)

    # 用 rich 打印 JSON
    print_json(data=result)


if __name__ == "__main__":
    main()











# # 9980 3571
# summary_json = build_summary_json(3571)
# # print(summary_json)
#
# result_summary = call_chatanywhere_api(summary_json)
# print(result_summary)
#
# print_json(data=result_summary)   # 美观输出
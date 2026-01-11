# server.py
import flwr as fl

# 新版 metrics 聚合函数
def weighted_average(metrics):
    """
    metrics: list of (num_examples, metrics_dict) tuples
    返回: 全局指标 dict
    """
    if not metrics:
        return {}

    total_examples = sum(num for num, _ in metrics)
    aggregated = {}

    for num, metric in metrics:
        for k, v in metric.items():
            aggregated[k] = aggregated.get(k, 0) + v * (num / total_examples)

    return aggregated

# FedAvg 策略
strategy = fl.server.strategy.FedAvg(
    fraction_fit=1.0,
    fraction_evaluate=1.0,
    min_fit_clients=3,
    min_evaluate_clients=3,
    min_available_clients=3,
    evaluate_metrics_aggregation_fn=weighted_average,
)

# Server 配置
server_config = fl.server.ServerConfig(num_rounds=5)

# 启动 server
fl.server.start_server(
    server_address="127.0.0.1:8080",
    strategy=strategy,
    config=server_config
)

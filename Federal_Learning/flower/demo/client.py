# client.py
import flwr as fl
import torch
import torch.nn as nn
import torch.optim as optim
from model import MLP
from data import load_data
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import sys
import numpy as np

# args: client_id
client_id = int(sys.argv[1])
csv_path = r"D:\Desktop\Healthcare\finalfeatures.csv"  # 你的 CSV 路径

# 加载数据
train_loader, test_loader, input_dim = load_data(csv_path, client_id, num_clients=3)

# 初始化模型
model = MLP(input_dim)
loss_fn = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Flower 客户端
class FraudClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        return [val.cpu().numpy() for val in model.state_dict().values()]

    def set_parameters(self, parameters):
        params_dict = zip(model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        model.train()
        for x, y in train_loader:
            optimizer.zero_grad()
            logits = model(x)
            loss = loss_fn(logits, y)
            loss.backward()
            optimizer.step()
        return self.get_parameters({}), len(train_loader.dataset), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        model.eval()

        y_true = []
        y_prob = []

        with torch.no_grad():
            for x, y in test_loader:
                logits = model(x)
                probs = torch.softmax(logits, dim=1)[:, 1]
                y_prob.extend(probs.cpu().numpy())
                y_true.extend(y.cpu().numpy())

        y_pred = (np.array(y_prob) > 0.5).astype(int)

        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1": f1_score(y_true, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(y_true, y_prob),
        }

        return 0.0, len(y_true), metrics

# 启动客户端
fl.client.start_numpy_client(server_address="127.0.0.1:8080", client=FraudClient())

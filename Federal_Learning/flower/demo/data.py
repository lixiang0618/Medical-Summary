# data.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import torch
from torch.utils.data import TensorDataset, DataLoader

def load_data(csv_path, client_id, num_clients=3, batch_size=32, test_size=0.2, seed=42):
    df = pd.read_csv(csv_path)

    # 标签
    y = df["欺诈状态"].values

    # 特征（去掉个人编码和label）
    X = df.drop(columns=["个人编码", "欺诈状态"]).values

    # 随机打乱
    rng = np.random.default_rng(seed)
    indices = rng.permutation(len(X))

    # 均分给 client
    splits = np.array_split(indices, num_clients)
    client_indices = splits[client_id]

    X_client = X[client_indices]
    y_client = y[client_indices]

    # train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_client, y_client, test_size=test_size, random_state=seed
    )

    # 标准化（仅用本 client 的统计量）
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # 转 torch tensor
    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.long)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_test = torch.tensor(y_test, dtype=torch.long)

    # DataLoader
    train_loader = DataLoader(TensorDataset(X_train, y_train), batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(TensorDataset(X_test, y_test), batch_size=batch_size, shuffle=False)

    return train_loader, test_loader, X_train.shape[1]

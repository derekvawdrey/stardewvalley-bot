import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class DQNAgent:
    def __init__(self, state_dim, action_dim, lr, gamma, epsilon, epsilon_decay, buffer_size):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.memory = deque(maxlen=buffer_size)
        self.model = DQN(state_dim, action_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)

    def act(self, state):
        random_value = np.random.rand()
        if random_value <= self.epsilon:
            return np.random.choice(self.action_dim)
        else:
            q_values = self.model(torch.tensor(state, dtype=torch.float32))
            return torch.argmax(q_values).item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                next_state_tensor = torch.tensor(next_state, dtype=torch.float32)
                with torch.no_grad():
                    target_model_output = self.model(next_state_tensor)
                target = reward + self.gamma * torch.max(target_model_output).item()
            state_tensor = torch.tensor(state, dtype=torch.float32)
            target_f = self.model(state_tensor)
            target_f[action] = target
            target_f = target_f.detach().numpy()
            self.optimizer.zero_grad()
            loss = nn.MSELoss()(torch.tensor(target_f), self.model(state_tensor))
            loss.backward()
            self.optimizer.step()
        if self.epsilon > 0.01:
            self.epsilon *= self.epsilon_decay


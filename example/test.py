import rA9.nn as nn
from rA9.optim import Adam
import rA9.nn.functional as F
from rA9.autograd import Variable
from rA9.nn.modules import Module
from rA9.utils import PoissonEncoder
from rA9.utils.data import DataLoader
from rA9.datasets.mnist import MnistDataset, collate_fn


class SNN(Module):
    def __init__(self):
        super(SNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=10, kernel_size=5)
        self.active1 = nn.LIF(key=1)
        self.conv2 = nn.Conv2d(in_channels=10, out_channels=20, kernel_size=5)
        self.active2 = nn.LIF(key=2)
        self.pool1 = nn.Pooling(size=2, channel=10)
        self.active3 = nn.LIF(key=3)
        self.pool2 = nn.Pooling(size=2, channel=20)
        self.active4 = nn.LIF(key=4)
        self.fc1 = nn.Linear(out_features=50, in_features=320)
        self.active5 = nn.LIF(key=5)
        self.fc2 = nn.Linear(out_features=10, in_features=50)
        self.active6 = nn.LIF(key=6)
        self.output = nn.Output(out_features=10)

    def forward(self, x, time):
        x = self.active1(self.conv1(x), time)
        x = self.active2(self.pool1(x), time)
        x = self.active3(self.conv2(x), time)
        x = self.active4(self.pool2(x), time)
        x = x.view(-1, 320)
        x = self.active5(self.fc1(x), time)
        x = self.active6(self.fc2(x), time)
        return self.output(x, time)


model = SNN()
model.train()

PeDurx = 50
batch_size = 16
Pencoder = PoissonEncoder(duration=PeDurx)
optimizer = Adam(model.parameters(), lr=0.01)

train_loader = DataLoader(dataset=MnistDataset(training=True, flatten=False),
                          collate_fn=collate_fn, shuffle=True,
                          batch_size=batch_size)

test_loader = DataLoader(dataset=MnistDataset(training=False, flatten=False),
                         collate_fn=collate_fn, shuffle=False,
                         batch_size=batch_size)

for epoch in range(15):
    for i, (data, target) in enumerate(train_loader):
        data = Variable(Pencoder.Encoding(data))
        target = Variable(target)
        output = model(x=data, time=1)
        loss = F.Spikeloss(outputs=output, labels=target, time_step=10)
        loss.backward()
        optimizer.step()
        print("Epoch:" + str(epoch) +"Step:"+ str(i) + "loss:" + str(loss.data))

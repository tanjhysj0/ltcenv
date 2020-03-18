# ltcenv
照gym的格式编写莱特币环境，用于强化学习的研究
action的值为-1到1之间,代表持仓
运行前先[安装catalyst](https://enigma.co/catalyst/install.html "安装catalyst")
代码市例:
```python
from ENV import LTCENV
import random
env = LTCENV()

observation = env.reset()

while True:
    action = random.uniform(-1, 1)
    observation_, r, Done = env.step(action)
    print(observation)
    print(r)
    if Done:
        print("完了")
        break


```
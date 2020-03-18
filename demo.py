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

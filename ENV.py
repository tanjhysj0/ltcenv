#!coding:utf-8
import multiprocessing
import os, time, random
import pandas as pd
from catalyst import run_algorithm
from catalyst.api import (order_target_percent, symbol)

NAMESPACE = 'ltc_DDPG'
# 开始日期
START_DATE = pd.to_datetime('2019-3-6', utc=True)
# 结速日期
END_DATE = pd.to_datetime('2019-3-7', utc=True)
# 观测历史条数
BAR_COUNT = 5

class LTCENV():
    def reset(self):
        self.pipe = multiprocessing.Pipe()

        self.p1 = multiprocessing.Process(target=run_algorithm, kwargs=
        {
            "capital_base": 1000,
            "data_frequency": "minute",
            "initialize": self.__initialize,
            "handle_data": self.__handle_data,
            "analyze": self.__analyze,
            "exchange_name": 'bitfinex',
            "algo_namespace": NAMESPACE,
            "quote_currency": "usd",
            "start": START_DATE,
            "end": END_DATE,
        })
        # 开启框架进程
        self.p1.start()
        # 执行第一步
        self.pipe[1].send(0)
        # 等响应
        respone = self.pipe[1].recv()
        return respone[0]

    def __initialize(self, context):
        context.i = 1
        context.asset = symbol('ltc_usd')
        context.set_commission(maker=0.002, taker=0.001)  # 设置手续费

    def __handle_data(self, context, data):
        if context.i > 1:
            # 执行完动作后发送相关观测
            ltc_value = data.current(context.asset, "price") * float(context.portfolio.positions[context.asset].amount)
            value = ltc_value + float(context.portfolio.cash)
            # 当前资产-现在资产
            rewards = value - context.value
            self.pipe[0].send([context.observation, rewards, False])

        # 接收动作并执行动作
        action = self.pipe[0].recv()
        order_target_percent(context.asset, action)
        short_data = data.history(context.asset,
                                  ('open', 'close', 'high', 'low', 'volume'),
                                  bar_count=BAR_COUNT,
                                  frequency="1m", )
        context.observation = short_data.values

        ltc_value = data.current(context.asset, "price") * float(context.portfolio.positions[context.asset].amount)
        context.value = ltc_value + float(context.portfolio.cash)
        context.i += 1

    def __analyze(self, context, perf):

        self.pipe[0].send([context.observation, 0, True])
        pass

    def step(self, action):
        # 发送动作
        self.pipe[1].send(action)
        # 响应观测
        respone = self.pipe[1].recv()
        if respone[-1]:
            # 如果结束了，终止这个进程
            self.p1.terminate()
        return respone

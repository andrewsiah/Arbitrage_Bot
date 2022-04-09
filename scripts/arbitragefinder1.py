# start --script 2script.py

from decimal import Decimal

from hummingbot.strategy.script_strategy_base import ScriptStrategyBase
from hummingbot.core.utils.trading_pair_fetcher import TradingPairFetcher

s_decimal_0 = Decimal(0)


class ArbitrageFinder1(ScriptStrategyBase):
    # It is best to first use a paper trade exchange connector
    # while coding your strategy, once you are happy with it
    # then switch to real one.
    arbitrage_markets = ["gate_io_paper_trade", "ascend_ex_paper_trade"]

    trading_pair_fetcher: TradingPairFetcher = TradingPairFetcher.get_instance()
    if trading_pair_fetcher.ready:
        trading_pairs_1 = trading_pair_fetcher.trading_pairs.get(arbitrage_markets[0], [])
        trading_pairs_2 = trading_pair_fetcher.trading_pairs.get(arbitrage_markets[1], [])
    trading_pairs_set = list(set(trading_pairs_1).intersection(trading_pairs_2))
    trading_pairs_set = trading_pairs_set[0:50]

    markets = {arbitrage_markets[0]: trading_pairs_set, arbitrage_markets[1]: trading_pairs_set}
    min_profitability = Decimal('0.007')

    def on_tick(self):
        self.logger().info(f"trading_pairs_1 {self.trading_pairs_set}")
        self.notify_hb_app_with_timestamp(f"1: {self.arbitrage_markets[0]}; 2: {self.arbitrage_markets[1]}")
        for pair in self.trading_pairs_set:
            try:
                market_1_bid = self.connectors[self.arbitrage_markets[0]].get_price(pair, False)
                market_1_ask = self.connectors[self.arbitrage_markets[0]].get_price(pair, True)
                market_2_bid = self.connectors[self.arbitrage_markets[1]].get_price(pair, False)
                market_2_ask = self.connectors[self.arbitrage_markets[1]].get_price(pair, True)
                profitability_buy_1_sell_2 = market_1_bid / market_2_ask - 1
                profitability_buy_2_sell_1 = market_2_bid / market_1_ask - 1

                if profitability_buy_1_sell_2 > self.min_profitability:
                    self.notify_hb_app_with_timestamp(f"{pair}: buy_1_sell_2: {profitability_buy_1_sell_2:.5f}")
                if profitability_buy_2_sell_1 > self.min_profitability:
                    self.notify_hb_app_with_timestamp(f"{pair}: buy_2_sell_1: {profitability_buy_2_sell_1:.5f}")
            except BaseException:
                self.logger().info(f"{pair} has no bid or ask order book")

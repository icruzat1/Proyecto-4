"""Compare causal, integer strategies on the official practice series."""
import csv
from collections import deque
from pathlib import Path

PRICES = Path(__file__).resolve().parents[1] / "tb/practica.csv"
INITIAL_CASH = 10_000
FEE = 5
WINDOW = 8
THRESHOLD = 3
QUANTITY = 16


def simulate(prices, strategy):
    cash, shares, orders = INITIAL_CASH, 0, 0
    pending = 0
    peak, drawdown = cash, 0
    window = deque(maxlen=WINDOW)
    for tick, price in enumerate(prices):
        if pending > 0:
            quantity = min(pending, max(0, (cash - FEE) // price))
            if quantity:
                cash -= quantity * price + FEE
                shares += quantity
                orders += 1
        elif pending < 0:
            quantity = min(-pending, shares)
            if quantity and cash + quantity * price >= FEE:
                cash += quantity * price - FEE
                shares -= quantity
                orders += 1

        equity = cash + shares * price
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
        pending = 0
        if strategy == "buy_hold" and tick == 0:
            pending = 63
        elif strategy in ("momentum", "reversion") and len(window) == WINDOW:
            difference = price * WINDOW - sum(window)
            signal = difference if strategy == "momentum" else -difference
            if signal >= THRESHOLD * WINDOW:
                pending = max(0, QUANTITY - shares)
            elif signal <= -THRESHOLD * WINDOW:
                pending = -shares
        window.append(price)
    return equity, orders, orders * FEE, drawdown


def course_benchmark(prices):
    shares = (INITIAL_CASH - FEE) // prices[0]
    cash = INITIAL_CASH - FEE - shares * prices[0]
    peak, drawdown = INITIAL_CASH, 0
    for price in prices:
        equity = cash + shares * price
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
    return equity, 1, FEE, drawdown


def main():
    with PRICES.open(newline="", encoding="utf-8") as source:
        prices = [int(row["price"]) for row in csv.DictReader(source)]
    print("serie,estrategia,patrimonio,ordenes,comisiones,drawdown")
    midpoint = len(prices) // 2
    for label, series in (("primera", prices[:midpoint]),
                          ("segunda", prices[midpoint:]), ("completa", prices)):
        for strategy in ("hold", "buy_hold", "momentum", "reversion"):
            metrics = simulate(series, strategy)
            print(label, strategy, *metrics, sep=",")
        print(label, "course_buy_hold", *course_benchmark(series), sep=",")


if __name__ == "__main__":
    main()

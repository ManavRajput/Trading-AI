import pandas as pd
import numpy as np

def calculate_sma(prices, period):
    if len(prices) < period:
        return np.nan  # Not enough data
    return pd.Series(prices).rolling(window=period).mean().iloc[-1]

def calculate_ema(prices, period):
  if len(prices) < period:
        return np.nan  # Not enough data
  return pd.Series(prices).ewm(span=period, adjust=False).mean().iloc[-1]

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return np.nan

    price_changes = pd.Series(prices).diff(1).dropna()
    gains = price_changes.where(price_changes > 0, 0.0)
    losses = -price_changes.where(price_changes < 0, 0.0)

    avg_gain = gains.rolling(window=period).mean().iloc[-1]
    avg_loss = losses.rolling(window=period).mean().iloc[-1]

    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
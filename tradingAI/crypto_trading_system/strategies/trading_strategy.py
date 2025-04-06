def make_trading_decision(message):
    technical_indicators = message.get('technical_indicators', {})
    fundamental_data = message.get('fundamental_data', {})
    human_psychology = message.get('human_psychology', {})
    sentiment = message.get('sentiment', {})

    sma_20 = technical_indicators.get('sma_20')
    ema_12 = technical_indicators.get('ema_12')
    rsi_14 = technical_indicators.get('rsi_14')
    market_cap = fundamental_data.get('market_cap')
    volume_24h = fundamental_data.get('volume_24h')
    compound_sentiment = sentiment.get('compound')
    fear = human_psychology.get('fear')
    greed = human_psychology.get('greed')

    # Check if ALL required values are NOT None before making comparisons
    if all(v is not None for v in [sma_20, ema_12, rsi_14, volume_24h, market_cap, compound_sentiment]):
        if ema_12 > sma_20 and rsi_14 < 70 and compound_sentiment > 0.2:
            return "BUY"
        elif ema_12 < sma_20 and rsi_14 > 30 and compound_sentiment < -0.2:
            return "SELL"
        elif volume_24h > market_cap * 0.1:
            return "BUY"
    if all(v is not None for v in [rsi_14, fear]):
        if fear > 0.7 and rsi_14 < 30:
            return "BUY"
    if all(v is not None for v in [rsi_14, greed]):
        if greed > 0.7 and rsi_14 > 70:
            return "SELL"
    return "HOLD"
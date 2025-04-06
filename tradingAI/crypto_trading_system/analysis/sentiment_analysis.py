import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

try:
    analyzer = SentimentIntensityAnalyzer()
except LookupError:
    nltk.download('vader_lexicon')
    analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    if text is None: # check if text is None
        return {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0} # return default value if text is None
    scores = analyzer.polarity_scores(text)
    return scores
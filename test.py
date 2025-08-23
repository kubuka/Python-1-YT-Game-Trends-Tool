from transformers import pipeline
from langdetect import detect


sentiment_pipeline = pipeline("sentiment-analysis", model = 'cardiffnlp/twitter-roberta-base-sentiment-latest')
pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")
trans = pipe("Hvala na dijeljenju, sjajan video!  Imam jedno jednostavno pitanje: U svom OKX novčaniku imam nešto USDT i imam 12 riječi: clap zone acid tube also among tape museum boy film soda salt. Kako mogu poslati taj USDT na Binance?")
print(trans)
sentiment = sentiment_pipeline(trans[0]['translation_text'])
print(sentiment)

#res = sentiment_pipeline(data)


#zrobić czyszczenie tekstu, usunięcie znaków specjalnych, emoji, linków itp.
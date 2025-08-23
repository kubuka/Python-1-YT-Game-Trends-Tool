from googleapiclient.discovery import build
import requests
import pandas as pd
from datetime import date, timedelta
import time
from isodate import parse_duration
from googleapiclient.errors import HttpError
import ast
import re
from transformers import pipeline, AutoTokenizer
from langdetect import detect, LangDetectException
import emoji 

game_name = input('Wpisz nazwe gry: ').lower()

### API YT
API_KEY = 'AIzaSyCaDs5KJfbQO-MwbFneDnj9yDy0SGYU91I'

def fetch_yt_data(game_name,video_duration):
    """
    Fetches YouTube video data for a given game name.
    Returns a DataFrame with video details.
    """
    youtube = build(
        'youtube', 
        'v3', 
        developerKey='AIzaSyCaDs5KJfbQO-MwbFneDnj9yDy0SGYU91I')

    filter_date = date.today() - timedelta(days=2) 
    next_page_token = None
    old_video = True
    df = pd.DataFrame()
    df['comments'] = ''

    ############################### pobieranie danych z YT

    while old_video:
        requests = youtube.search().list(
            part='snippet',
            q=game_name,
            type='video',
            order='date',
            videoDuration=video_duration,
            eventType='completed',
            pageToken=next_page_token,
            maxResults=50
        )
        vid_ids = []
        response = requests.execute()
        for item in response['items']:
            if item['snippet']['publishedAt'] >= filter_date.isoformat():
                video_id = item['id']['videoId']
                vid_ids.append(video_id)
                df.loc[video_id, 'title'] = item['snippet']['title']
                df.loc[video_id, 'publishedAt'] = item['snippet']['publishedAt'].split('T')[0]
                df.loc[video_id, 'channelName'] = item['snippet']['channelTitle']       
            else:
                old_video = False
                break

        requests = youtube.videos().list(
            part='statistics,contentDetails',
            id=','.join(vid_ids)
        )

        vidresponse = requests.execute()
        for item in vidresponse['items']:
            video_id = item['id']
            if video_id in df.index:
                df.loc[video_id, 'duration'] = parse_duration(item['contentDetails']['duration']).total_seconds()
                df.loc[video_id, 'viewCount'] = int(item['statistics'].get('viewCount', 0))
                df.loc[video_id, 'likeCount'] = int(item['statistics'].get('likeCount', 0))
                df.loc[video_id, 'commentCount'] = int(item['statistics'].get('commentCount', 0))

            else:
                print(f"Brak statystyk dla ID: {video_id}")
        
  
        for video_id in vid_ids:
            comments_next_page_token = None
            comments_list = []
            try:
                while True:
                    comment_response = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        textFormat='plainText',
                        pageToken=comments_next_page_token,
                        maxResults=100
                    )
                    
                    
                    requests = comment_response.execute()
                    for item in requests['items']:
                        comment_snippet = item['snippet']['topLevelComment']['snippet']
                        comments_list.append(comment_snippet['textDisplay'])
                    
                    comments_next_page_token= requests.get('nextPageToken', None)

                    if len(comments_list) >= 200:
                        df.at[video_id, 'comments'] = comments_list  
                        break

                    if not comments_next_page_token:
                        df.at[video_id, 'comments'] = comments_list         
                        break

            except HttpError as error:
                if error.resp.status == 403:
                    print(f"Błąd 403: {video_id}")
                    df.at[video_id, 'comments'] = [] 
                    

        next_page_token = response.get('nextPageToken')
        time.sleep(1)

        if not next_page_token:
            break

    next_page_token = None
    return df
   

df = pd.concat([fetch_yt_data(game_name, 'medium'), fetch_yt_data(game_name, 'long')]) 
df = df[df.columns[1:].tolist() + [df.columns[0]]]
df.to_csv('youtube_data.csv')
#df2 = pd.read_csv('youtube_data.csv', index_col=0)

#Analiza sentymentu komentarzy

print('df orginaly komentarze')
print(df['comments'])
df_exploded = df[df['comments'].str.len() > 0]
df_exploded = df_exploded.explode('comments').reset_index()
print(df_exploded.head())

def normalize_comment(comment):

    comment = comment.lower()
    comment = comment.replace('\n', ' ').strip()
    comment = re.sub(r'http\S+', '', comment)
    comment = re.sub(r'@\w+', '', comment)  # Usunięcie wzmiankowania
    comment = re.sub(r'#[\w-]+', '', comment)  # Usunięcie hashtagów

    comment = emoji.demojize(comment) # zamienia emoji na tekst, np. :red_heart:
    comment = re.sub(r':\w+:', '', comment)
    comment = re.sub(r'[^\w\s.,?!-]', '', comment, flags=re.UNICODE)

    timestamp_pattern = r'\b(\d{1,2}:\d{2}(:\d{2})?)\b'
    comment = re.sub(timestamp_pattern, '', comment)
    return comment

def safe_detect(text):
    try:
        if text and len(text.strip()) > 3:
            return detect(text)
        else:
            return 'unknown'
    except LangDetectException:
        return 'unknown'
tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-mul-en")
translation_pipeline = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en", max_length=512,truncation=True, tokenizer=tokenizer)

df_exploded['comments'] = df_exploded['comments'].astype(str).apply(normalize_comment)
df_exploded['lang'] = df_exploded['comments'].apply(safe_detect)

to_translate = df_exploded[ (df_exploded['lang'] != 'en') & (df_exploded['lang'] != 'unknown')]['comments'].tolist()
eng_not_translated = df_exploded[df_exploded['lang'] == 'en']['comments'].tolist()
unknwon_not_translated = df_exploded[df_exploded['lang'] == 'unknown']['comments'].tolist()

translated_results = translation_pipeline(to_translate)
translated_texts = [res['translation_text'] for res in translated_results]

df_exploded['translated_comments'] = ''

#rozdzielic to na 3 grupy zeby pozniej nie robic sentymentu z unknown   !!!!!!

df_exploded.loc[(df_exploded['lang'] != 'en') & (df_exploded['lang'] != 'unknown'), 'translated_comments'] = translated_texts
df_exploded.loc[(df_exploded['lang'] == 'en'), 'translated_comments'] = eng_not_translated
df_exploded.loc[(df_exploded['lang'] == 'unknown'), 'translated_comments'] = unknwon_not_translated

#analiza sentymentu
sentiment_pipeline = pipeline("sentiment-analysis")
comments_to_analyze = df_exploded[(df_exploded['lang'] != 'unknown')]['translated_comments'].tolist()
sentiment_results = sentiment_pipeline(comments_to_analyze, max_length=512, truncation=True)
sentiments = [1 if result['label'] == 'POSITIVE' 
                else -1 if result['label'] == 'NEGATIVE'
                else 0  for result in sentiment_results]

df_exploded['sentiment'] = 0
df_exploded.loc[df_exploded['lang'] != 'unknown', 'sentiment'] = sentiments


df_final = df_exploded.groupby('index').agg(
    lang=('lang', list),  
    translated_comments=('translated_comments', list),
    sentiment=('sentiment', list)
).reset_index()

df = df.merge(df_final, left_index=True, right_on='index', how='left')

#cleanup

df['translated_comments'] = df['translated_comments'].fillna('').apply(
    lambda x: x if isinstance(x, list) else []
)
df['sentiment'] = df['sentiment'].fillna('').apply(
    lambda x: x if isinstance(x, list) else []
)

df.loc[df['lang'] == 'unknown', 'sentiment'] = df.loc[df['lang'] == 'unknown', 'sentiment'].apply(lambda x: [])
df['sentiment_summary'] = df['sentiment'].apply(lambda x: sum(x) if isinstance(x, list) else 0)


df.set_index('index', inplace=True)
df.to_csv('youtube_data_translated.csv')
print(df)


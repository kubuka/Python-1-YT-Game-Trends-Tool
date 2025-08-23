 
    # old_video = True

    #                                 ######LONGI TUTAJ#######
    # while old_video:
    #     requests = youtube.search().list(
    #         part='snippet',
    #         q=game_name,
    #         type='video',
    #         order='date',
    #         videoDuration='long',
    #         eventType='completed',
    #         pageToken=next_page_token,
    #         maxResults=50
    #     )
    #     vid_ids = []
    #     response = requests.execute()
    #     for item in response['items']:
    #         if item['snippet']['publishedAt'] >= filter_date.isoformat():
    #             video_id = item['id']['videoId']
    #             vid_ids.append(video_id)
    #             df.loc[video_id, 'title'] = item['snippet']['title']
    #             df.loc[video_id, 'publishedAt'] = item['snippet']['publishedAt'].split('T')[0]
    #             df.loc[video_id, 'channelName'] = item['snippet']['channelTitle']       
    #         else:
    #             old_video = False
    #             break

    #     requests = youtube.videos().list(
    #         part='statistics',
    #         id=','.join(vid_ids)
    #     )

    #     vidresponse = requests.execute()
    #     for item in vidresponse['items']:
    #         video_id = item['id']
    #         if video_id in df.index:
    #             df.loc[video_id, 'viewCount'] = int(item['statistics'].get('viewCount', 0))
    #             df.loc[video_id, 'likeCount'] = int(item['statistics'].get('likeCount', 0))
    #             df.loc[video_id, 'commentCount'] = int(item['statistics'].get('commentCount', 0))
    #         else:
    #             print(f"Brak statystyk dla ID: {video_id}")

    #     next_page_token = response.get('nextPageToken')
    #     # if  len(dump) > dumpsize:
    #     #     pages = False
    #     time.sleep(1)

    #     if not next_page_token:
    #         break






# for i in range(pages):
#     requests = youtube.search().list(
#         part='snippet',
#         q=game_name,
#         type='video',
#         order='date',
#         videoDuration='long',
#         eventType='completed',
#         pageToken=next_page_token,
#         maxResults=20
#     )

#     response = requests.execute()
#     all_40videos.extend(response['items'])
#     next_page_token = response.get('nextPageToken')
#     time.sleep(1)

#     if not next_page_token:
#         break


# with open('20data.json', 'w') as f:
#     json.dump(all_20videos, f, indent=4)

# with open('40data.json', 'w') as f:
#     json.dump(all_40videos, f, indent=4)

# ############################ ogarnianie jsona



# with open('20data.json', 'r') as f:
#     all_20videos = json.load(f)
# with open('40data.json', 'r') as f:
#     all_40videos = json.load(f)


# for video in chain(all_20videos,all_40videos):
#     video_id = video['id']['videoId']
#     title = video['snippet']['title']
#     publish_time = (video['snippet']['publishedAt']).split('T')[0] 
#     channel_name = video['snippet']['channelTitle']
#     video_data =[video_id, title, publish_time, channel_name]

#     if publish_time >= filter_date.isoformat():     #to dać na sam koniec przy sklejaniu DataFrame  
#         temp_df.append(video_data)
#     else:
#         continue

# ############################## zapisywanie do DataFrame

# df = pd.DataFrame(temp_df, columns=columns)         #to tez
# df = df.set_index('videoId')
# print(df)


# for id in df.index:
#     requests = youtube.videos().list(
#         part='statistics',
#         id=id
#     )

#     response = requests.execute()
#     if response['items']:
#         video_stats = response['items'][0]['statistics']
#         df.loc[id, 'viewCount'] = video_stats['viewCount']
#         df.loc[id, 'likeCount'] = video_stats['likeCount'] if 'likeCount' in video_stats else 0
#         df.loc[id, 'commentCount'] = video_stats['commentCount'] if 'commentCount' in video_stats else 0
#     else:
#         print(f"Brak statystyk dla ID: {id}")
#         df.loc[id, 'viewCount'] = 0
#         df.loc[id, 'likeCount'] = 0
#         df.loc[id, 'commentCount']

# print(df)
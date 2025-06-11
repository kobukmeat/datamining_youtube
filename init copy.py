from googleapiclient.discovery import build
import pandas as pd
from tqdm import tqdm
from datetime import datetime

API_KEY = 'AIzaSyDo7MITNIkvYaF3Qcddk0FGW0k2Wfi5Scs'  # 발급받은 API 키 입력
youtube = build('youtube', 'v3', developerKey=API_KEY)

video_items = []
next_page_token = None

# 100개 수집 (50개씩 2회)
for _ in range(4):
    response = youtube.videos().list(
        part='snippet,statistics',
        chart='mostPopular',
        regionCode='KR',
        maxResults=50,
        pageToken=next_page_token
    ).execute()
    video_items.extend(response['items'])
    next_page_token = response.get('nextPageToken')
    if not next_page_token:
        break

data = []
for idx, item in enumerate(tqdm(video_items, desc="채널 정보 수집", ncols=80), start=1):
    title = item['snippet']['title']
    views = int(item['statistics'].get('viewCount', 0))
    channel = item['snippet']['channelTitle']
    channel_id = item['snippet']['channelId']
    like_count = int(item['statistics'].get('likeCount', 0))
    published_at = item['snippet']['publishedAt']  # 업로드 날짜
    # 구독자수
    channel_response = youtube.channels().list(
        part='statistics',
        id=channel_id
    ).execute()
    subscribers = int(channel_response['items'][0]['statistics'].get('subscriberCount', 0))
    data.append({
        '순번': idx,
        '제목': title,
        '조회수': views,
        '좋아요수': like_count,
        '닉네임': channel,
        '구독자수': subscribers,
        '업로드날짜': published_at
    })

df = pd.DataFrame(data, columns=['순번', '제목', '조회수', '좋아요수', '닉네임', '구독자수', '업로드날짜'])

# 파일명에 데이터 수집 시각 포함 (예: youtube_trending_2025-06-12_0013.xlsx)
now = datetime.now().strftime('%Y-%m-%d_%H%M')
file_name = f'youtube_trending_{now}.xlsx'
df.to_excel(file_name, index=False)
print(f"{file_name} 파일이 생성되었습니다.")

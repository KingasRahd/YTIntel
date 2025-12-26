from langchain_google_genai import ChatGoogleGenerativeAI
from googleapiclient.discovery import build
import os
import pandas as pd
import json
import streamlit as st
from dotenv import load_dotenv
import isodate

load_dotenv()

api_key=os.getenv('API_KEY')
yt=build('youtube','v3',developerKey=api_key)

#creating empty data frame
df=pd.DataFrame() 
fdf=pd.DataFrame()

def preprocessing(uploads_id,goals,next_page_id):

    #declaring the global dataframes within function
    global fdf,df

    #parsing upload playlist videos
    request=yt.playlistItems().list(
    playlistId=uploads_id,
    part=['contentDetails'],
    maxResults=50,
    pageToken=next_page_id
)
    response=request.execute()

    #storing the next page id if any, else storing None in next_page_id
    try:
        next_page_id=response['nextPageToken'] 
    except: 
        next_page_id=None

    #extracting the video ids of a batch of 20 video items
    v_id=[]
    for item in response['items']:
        v_id.append(item['contentDetails']['videoId']) 

    #fetching details of all video ids at once
    request=yt.videos().list(
    id=','.join(v_id,),
    part='statistics,contentDetails,snippet'
)
    response=request.execute()

    #extracting important details of each video id and storing them in respective list
    title=[]
    desc=[]
    thumbnails=[]
    tags=[]
    duration=[]
    views=[]
    likes=[]
    comments=[]
    date=[]
    for item in response['items']:
        try:title.append(item['snippet']['title'])
        except:title.append(None)

        try:desc.append(item['snippet']['description'])
        except:desc.append(None)

        try:thumbnails.append(item['snippet']['thumbnails']['medium']['url'])
        except:thumbnails.append(None)

        try:tags.append(item['snippet']['tags'])
        except:tags.append(None)

        pub_date=item['snippet']['publishedAt']
        pub_date=pub_date[:pub_date.index('T')]
        try: date.append(pub_date)
        except: date.append(None)

        time=item['contentDetails']['duration']
        time=isodate.parse_duration(time)
        total_seconds = int(time.total_seconds())
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        time=f'{h}:{m}:{s}'    
        try:duration.append(time)
        except:duration.append(None)
        
        try:views.append(item['statistics']['viewCount'])
        except:views.append(None)

        try:likes.append(item['statistics']["likeCount"])
        except:likes.append(None)

        try:comments.append(item['statistics']['commentCount'])
        except:comments.append(None)

    vdf=pd.DataFrame(
{
    'VID':v_id,
    'Title':title,
    'Duration':duration,
    'Views':views,
    'Likes':likes,
    'Comments':comments,
    'Thumbnail':thumbnails,
    'Tags':tags,
    'Description':desc,
    'Date':date
}
)
    #converting vdf['Tags'] from list to clean string values
    vdf['Tags']=vdf['Tags'].astype(str).str.translate(str.maketrans('','',"[]'"))

    #adding video URLs
    vdf['URL']=vdf['VID'].apply(lambda x:f"https://www.youtube.com/watch?v={x}")

    #converting the batch to json format before feeding to LLM
    video_data=vdf[['VID','Title','Description','Tags','Views','Likes','Duration','Date']].to_json(orient='records')
    video_data=json.loads(video_data)

    #sending batch to LLM for filtering
    filtered_df=feed_llm(video_data,goals)

    if type(filtered_df)==str:
        df=pd.concat([df,vdf])
        return fdf.reset_index(drop=True),next_page_id,df.shape[0]
    
    #extracting common data in vdf and filtered data and merging on VID
    filtered_df=pd.merge(vdf,filtered_df,on='VID',how='right')
    
    #now add this batch to the final data frame 'df'
    df=pd.concat([df,vdf])
    fdf=pd.concat([fdf,filtered_df])

    #returning fdf,next_page_id and no. of rows in df 
    return fdf.reset_index(drop=True),next_page_id,df.shape[0]

    
def feed_llm(video_data,goals):

    #making LLM object
    model=ChatGoogleGenerativeAI(model="gemini-2.5-flash",google_api_key=api_key,temperature=0.0)  

    #prompt generation
    prompt=prompt=f'''
    You are an intelligent assistant designed to help users find the most relevant YouTube videos based on their learning or personal development goals.

    You will receive:
    1. A clear description of the user's goals.
    2. A list of video metadata, where each video includes:
        - Video ID (VID)
        - Title
        - Description
        - Tags
        - View count
        - Like count
        - Duration
        - Upload date

    Your tasks are:

1. **Strictly analyze** each video’s usefulness with respect to the user’s specific goals, current trends, and future prospects **within the explicitly mentioned domain only** (e.g., if the user wants AI/ML content, do NOT include videos about Web Development, App Dev, or unrelated fields).
   
2. Only select videos that are **highly relevant, directly beneficial**, and **central** to the user’s goal domain. Do not include videos that are tangential, background-related, or generally informative but outside the domain.

3. Be highly picky and precise. Select only videos that add clear, valuable knowledge **within the field mentioned** by the user (no general productivity, career tips, etc. unless it's *directly linked* to the domain).

4. For each selected video, provide a brief justification explaining why it is relevant and valuable for the user's specific goals.

5. Tag a category to each video depending on the nature of the video:

### 🧠 Examples of Categories

    #### For technical/educational content:
    - **Must Watch** – Crucial for the goal; high impact
    - **Foundational** – Covers basics or prerequisites
    - **Extra Knowledge** – Not essential but interesting
    - **Practical Tutorial** – Step-by-step guides or coding walkthroughs
    - **Quick Wins** – Easy tricks/tips with instant results
    - **Conceptual Clarity** – Explains key ideas clearly
    - **Advice** – General guidance from experience
    - **Deep Dive** – In-depth exploration of a topic

    #### For self-help/personal development:
    - **Core Mindset Shift** – Changes perspective significantly
    - **Actionable Advice** – Tips that can be directly applied
    - **Concept Explainer** – Breaks down personal growth theories
    - **Motivational** – Inspires action or energy
    - **Habit Building** – Focuses on behavior change
    - **Psychological Insight** – Mental models or cognitive insights
    - **Extra Perspective** – Broader views that enrich thinking

for other video genres add video according to your judgement but dont create too many tags

6. Do not include videos that seem like clickbait judging from views, likes and comment count
    
7. If **no videos match the goal domain strictly**, return the 'NA':

    ---

    For each selected video, return a JSON object in the following format:
    (
        "VID": "<video_id>",
        "Category":"<video_category>"
        "Justification": "<brief explanation of why this video is relevant and categorized as such>"
    )

    Only include videos that *genuinely align* with the user's goals and will help them grow or make progress.

    ---

    ### USER GOALS:
    {goals}

    ---

    ### VIDEO DATA:
    {video_data}
    '''

    result=model.invoke(prompt)
    filtered_data=result.content
    filtered_data=filtered_data.replace('json','')
    filtered_data=filtered_data.replace('`','')
    try:filtered_data=json.loads(filtered_data)
    except:return 'NA'
    filtered_data=pd.DataFrame(filtered_data)
    return filtered_data



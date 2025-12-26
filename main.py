from googleapiclient.discovery import build
import os
import pandas as pd
import json,time
import streamlit as st
from dotenv import load_dotenv
import preprocessor

load_dotenv()

api_key=os.getenv('API_KEY')
yt=build('youtube','v3',developerKey=api_key)

#categories=set()
next_page_id=None

col=st.columns([1,7])
col[0].image('https://imgs.search.brave.com/JcNizJbvdueXE1HaRjeJO004oNeH5dvxggxG1Hh8jDE/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvMjE3/OTU4MjE3NC9waG90/by95b3V0dWJlLWdv/bGQtaWNvbi1lbGVt/ZW50LW9uLXdoaXRl/LWJhY2tncm91bmQu/anBnP2I9MSZzPTYx/Mng2MTImdz0wJms9/MjAmYz1qR0xLZ2hu/b2pua1lJNzgyd0JD/d19aTl9iV3NPUWJv/V3pKNEJmNjRIYkhB/PQ')
col[1].title(' YTIntel')
st.markdown('#### Your smart assistant for analyzing YouTube channels and recommending videos tailored to your personal learning goals.')
st.write('*Reload on Crash')
col=st.columns([1,1,1])
col[2].markdown('###### Built by ~ Sagnik✨')
st.markdown('---')
####################################
#insert streamlit code for user input here
st.markdown("### 🎯 Your Learning Preferences")
st.markdown("###### Paste a YouTube channel ID and tell us what you want to learn. We'll filter the videos so you get only the most useful content.")
col=st.columns([2,1])
ch_id=col[0].text_input('Drop your Channel ID here')# 'UCarWcnSwdzAlSTo0RCuhKZg'
goals=col[0].text_area('What are you hoping to learn or achieve?')
preprocessor.fdf=pd.DataFrame()
preprocessor.df=pd.DataFrame()
st.markdown('---')
####################################
try:
    st.write(api_key)
    if ch_id and goals:
        
        #calling channel
        request=yt.channels().list(
        id=ch_id,
        part=['contentDetails','snippet','statistics']
        )
        response=request.execute()
        
        #from snippet
        ch_name=response['items'][0]['snippet']['title']
        ch_desc=response['items'][0]['snippet']['description']
        ch_thumbnail=response['items'][0]['snippet']['thumbnails']['medium']['url']

        #from contentDetails
        uploads_id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        #from statistics
        subscribers=response['items'][0]['statistics']['subscriberCount']
        total_videos=response['items'][0]['statistics']['videoCount']

        channel={
                'Name':ch_name,
                'Description':ch_desc,
                'Thumbnail':ch_thumbnail,
                'Uploads_ID':uploads_id,
                'Subscribers':subscribers,
                'Total_Videos':total_videos
            }

        st.markdown("### 📺 Channel Overview")
        col=st.columns([1,1,1])
        col[0].image(channel['Thumbnail'])
        col[1].subheader(channel['Name'])
        col[1].markdown(f"##### {channel['Subscribers']} subscribers")
        col[1].markdown(f"###### {channel['Total_Videos']} videos")
        st.markdown('---')

        placeholder=st.empty()

        if (('filtered_df' not in st.session_state) or (st.session_state['ch_id']!=ch_id) or (st.session_state['goals']!=goals)):
    
            st.session_state['ch_id']=ch_id
            st.session_state['goals']=goals
            with st.spinner('Searching Relevant Videos for You'):
                while True:
                    st.session_state['filtered_df'],next_page_id,st.session_state['rows']=preprocessor.preprocessing(uploads_id,goals,next_page_id)
                    placeholder.write(f"Filtered {st.session_state['filtered_df'].shape[0]}/{st.session_state['rows']} videos ") 
                    time.sleep(4)
                    if next_page_id==None:
                        break
                    
        ndf=st.session_state['filtered_df']
        rows=st.session_state['rows']

        st.title('Recommended Videos :')
        st.subheader(f'{ndf.shape[0]}/{rows}')
        st.markdown('---')

        #edge case
        if ndf.empty:
            col=st.columns([1,1,1])
            col[1].image('https://imgs.search.brave.com/XuvQlzKHLLsQIFwrlxSmvCItKffQDk9QWA81aKeCCOM/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly93d3cu/cG5naXRlbS5jb20v/cGltZ3MvbS8xNTAt/MTUwNTcxMV9uby1y/ZXN1bHQtcG5nLXRy/YW5zcGFyZW50LXBu/Zy5wbmc',width=200)
            st.markdown('##### No videos matched your goal. Try adjusting your Input?')

        


        try:   # this is to handle the edge case of 0 videos filtered when ndf is empty
        
            #creating a csv file
            csv_data=ndf[['Title','Category','URL','Justification']]
            csv_data=csv_data.to_csv(index=False)

            #making the download button
            col=st.columns([3,1])
            col[1].download_button(
                label='Download List as CSV',
                data=csv_data,
                file_name='YTIntel_Filtered_Videos.csv',
                mime='text/csv'
            )

            #selecting category
            categories=ndf['Category'].unique()
            category=st.selectbox('Select Category',categories)

            #category wise data selection
            filtered_df=ndf.query('Category==@category')
           
            col=st.columns([3,1,3])
            col[1].markdown(f"**Videos : {filtered_df.shape[0]}**")
            st.markdown('')

            #display format 1
            for i in range(filtered_df.shape[0]):
                col=st.columns([1,3])
                col[0].markdown(f"[![Video Thumbnail]({filtered_df.iloc[i]['Thumbnail']})]({filtered_df.iloc[i]['URL']})")
                col[1].markdown(f"**{filtered_df.iloc[i]['Title']}**")
                col[1].markdown(f"**Reason:** {filtered_df.iloc[i]['Justification']}")
                col[1].markdown(f"**Category:** {filtered_df.iloc[i]['Category']}")
                


            #display format 2
            # col=st.columns([1,1,1])
            # for i in range(0,filtered_df.shape[0],3):
            #     col[0].markdown(f"[![Video Thumbnail]({filtered_df.iloc[i]['Thumbnail']})]({filtered_df.iloc[i]['URL']})")
            #     col[0].markdown(f"**{filtered_df.iloc[i]['Title']}**")
            #     col[0].markdown(f"**Reason:** {filtered_df.iloc[i]['Justification']}")
            #     col[0].markdown('---')

            #     try:
            #         col[1].markdown(f"[![Video Thumbnail]({filtered_df.iloc[i+1]['Thumbnail']})]({filtered_df.iloc[i+1]['URL']})")
            #         col[1].markdown(f"**{filtered_df.iloc[i+1]['Title']}**")
            #         col[1].markdown(f"**Reason:** {filtered_df.iloc[i+1]['Justification']}")
            #         col[1].markdown('---')
            #     except:pass

            #     try:
            #         col[2].markdown(f"[![Video Thumbnail]({filtered_df.iloc[i+2]['Thumbnail']})]({filtered_df.iloc[i+2]['URL']})")
            #         col[2].markdown(f"**{filtered_df.iloc[i+2]['Title']}**")
            #         col[2].markdown(f"**Reason:** {filtered_df.iloc[i+2]['Justification']}")
            #         col[2].markdown('---')
            #     except:pass
        
        except: pass
        
    else:
        col=st.columns([1,5,1])
        col[1].image('https://imgs.search.brave.com/tgdRA2tRkRiMe_7WcJJqUcGYIeO2uxhb6kNlYK2uHLQ/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly90aHVt/YnMuZHJlYW1zdGlt/ZS5jb20vYi9vbGQt/bWFuLWZpc2hpbmct/Y3V0ZS1jYXJ0b29u/LXN0eWxlLWlzb2xh/dGVkLWZsYXQtdmVj/dG9yLWlsbHVzdHJh/dGlvbi13aGl0ZS1i/YWNrZ3JvdW5kLTcw/MDcwNzUxLmpwZw',width=200)
        st.markdown('**Enter a channel and your goal to get tailored video recommendations!**')

except:
    col=st.columns([1,2,1])
    col[1].image('https://imgs.search.brave.com/ugXIgQXTYCTqNh3ao8z2c33C01MaH4AWaGzems_xz8s/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pLnBp/bmltZy5jb20vb3Jp/Z2luYWxzL2EwLzJh/Lzc2L2EwMmE3NjQ3/ZDUyODQxNjk2MmY0/OTM4OWZkYTc1M2My/LmpwZw',width=100)
    st.markdown('**Oops! That doesn’t look right. Please check your input and try again.**')

st.markdown('---')
import streamlit as st
from PIL import Image 
from utils.modules import detect, detectVideo, getDataframe
from utils.modules import getFlag, setFlag, resetFlag
from utils.modules import initial_setup


@st.cache_data
def convert_df(df):
    """
        Reads the counts dataframe and
        returns in CSV format.
    """
    return df.to_csv().encode('utf-8')

def processImage():
    """
        UI Part if the users chooses
        to proceess a image.
    """
    threhold = st.slider('Choose a threshold value', 0.0, 1.0, 0.40)
    image_file = st.file_uploader("Upload An Image",type=['png','jpeg','jpg'])
    if image_file is not None:
        file_details = {"FileName":image_file.name,"FileType":image_file.type}
        file_type = (image_file.type).split('/')[1]
        input_file_name = f"data/Input.{file_type}"
        with open(input_file_name,mode = "wb") as f: 
            f.write(image_file.getbuffer())    
        first_process = int(getFlag())
        count = detect(input_file_name, confidence=threhold)
        img_ = Image.open("data/result.jpg")
        st.subheader(f"People Count = {count}")
        st.image(img_)
        with open("data/result.jpg", "rb") as file:
            st.download_button(
                    label="Download image",
                    data=file,
                    file_name="Processed.jpg",
                    mime="image/jpg"
                ) 

def processVideo():
    """
        UI Part if the users chooses
        to proceess a video.
    """
    threhold = st.slider('Choose a threshold value', 0.0, 1.0, 0.40)
    uploaded_video = st.file_uploader("Upload a Video", type = ['mp4','mpeg','mov'])
    if uploaded_video is not None :
        file_type = (uploaded_video.type).split('/')[1]
        input_file_name = f"data/Input.{file_type}"
        if uploaded_video != None:
            vid = input_file_name
            with open(vid, mode='wb') as f:
                f.write(uploaded_video.read()) 
                
            st_video = open(vid,'rb')
            video_bytes = st_video.read()
            first_process = int(getFlag())
            if first_process == 1:
                with st.spinner('Processing the video ⌛️'):
                    detectVideo(vid, confidence=threhold)
                setFlag()
                first_process = int(getFlag())
            st_video = open('data/output.mp4','rb')
            video_bytes = st_video.read()
            st.video(video_bytes)
            df = getDataframe()
            st.markdown("<h3 style='text-align: center;'>People Visit Trend 📊</h3>", unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])

            col1.line_chart(data=df, x='Time', y='Count')
            col2.dataframe(data=df, )
            row1, row2, _ = st.columns([3, 3, 5])
            with open("data/output.mp4", "rb") as file:
                btn = row1.download_button(
                        label="Download video",
                        data=file,
                        file_name="Processed.mp4",
                        mime="video/mp4"
                    )
            csv = convert_df(df)

            row2.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='data/density.csv',
                mime='text/csv',
            )


def main():
        """
            UI Part of the entire application.
        """
        st.set_page_config(
            page_title ="Track-X",
            page_icon = "🧊",
            menu_items={
        'About': "# iKurious People Track-X"
            } 
        )    
        st.markdown("<h1 style='text-align: center;'>People <span style='color: #9eeade;'>Track-X</span></h1>", unsafe_allow_html=True)  
        st.subheader("Artificial Intelligent System")
        option = st.selectbox(
    'What Type of File do you want to work with?',
    ('Images', 'Videos'))
        if option == "Images":
            st.title('Image Analysis')
            processImage()
        else:
            st.title('Video Analysis')
            st.button("Reset", on_click=resetFlag)
            processVideo()

        with st.expander("About People Track-X"):
            st.markdown( '<p style="font-size: 30px;"><strong>Welcome to the People \
                <span style="color: #9eeade;">Track-X</span> App!</strong></p>', unsafe_allow_html= True)
            st.markdown('<p style = "font-size : 20px; color : white;">This application was \
                built  to analyse the <strong>People Density</strong> \
                    on a particular place.</p>', unsafe_allow_html=True)

if __name__ == '__main__':
    __author__ = 'Mahimai Raja J'
    __version__ = "1.0.0"
    initial_setup()
    main()

# 📌 NOTE :
# Do not modify the credits unless you have 
# legal permission from the authorizing authority .

# Thank you for helping to maintain the integrity of the 
# open source community by promoting fair and ethical 
# use of open source software 💎.
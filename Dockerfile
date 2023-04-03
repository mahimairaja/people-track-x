# To pull my container 
FROM mahimairaja/people-trackx:0.2

# To copy all files and directories into the container
COPY . .

# To the set the working directory 
WORKDIR app

# To open the port 8501 for Streamlit
EXPOSE 8501

# To execute the application
CMD ["streamlit", "run", "app.py"]
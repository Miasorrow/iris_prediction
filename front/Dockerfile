FROM python:3.12

WORKDIR /app

RUN pip install streamlit 

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
# syntax=docker/dockerfile:1

FROM python:3.9

WORKDIR /ravi-proj

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .


CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app

CMD ["python","-m","flask","run","--host=0.0.0.0"] 
#uncomment above line, if you want to run the docker image in the container
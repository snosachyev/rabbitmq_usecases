FROM python:3.9

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY .. /code/app

WORKDIR /code/app
RUN ["/bin/bash", "-c", "pwd"]

ENTRYPOINT ["/bin/bash", "-c", "uvicorn producer.main:app --host $APP_HOST --port $APP_PORT"]

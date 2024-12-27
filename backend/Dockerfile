FROM --platform=linux/amd64 python:3.10.9-slim-buster
LABEL maintainer="tetiana.kozakova901@gmail.com"

WORKDIR /app


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /vol/web/media
RUN mkdir -p /app/media/uploads/users


RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user

RUN chown -R django-user:django-user /vol/
RUN chmod -R 755 /vol/web/
RUN chown -R django-user:django-user /app/media
RUN chmod -R 755 /app/media

USER django-user
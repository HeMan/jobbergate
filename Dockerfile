FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk --update add libffi-dev build-base
ENV STATIC_PATH /app/jobbergate/static
COPY ./requirements.txt ./uwsgi.ini /app/
COPY ./jobbergate /app/jobbergate
COPY ./apps /app/apps
RUN pip install -r /app/requirements.txt


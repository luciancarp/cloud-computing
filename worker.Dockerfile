FROM python:alpine3.7
COPY /cnd-worker /cnd-worker
WORKDIR /cnd-worker
RUN pip install -r requirements.txt
EXPOSE 3000
CMD python ./cnd_worker.py
FROM python:alpine3.7
WORKDIR /cnd-worker
COPY cnd_worker.py .
# RUN pip install -r requirements.txt
EXPOSE 3000
CMD python ./cnd_worker.py
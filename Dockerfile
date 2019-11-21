FROM python:alpine3.7
COPY /cnd /cnd
WORKDIR /cnd
# RUN pip install -r requirements.txt
EXPOSE 3000
CMD python ./cnd.py
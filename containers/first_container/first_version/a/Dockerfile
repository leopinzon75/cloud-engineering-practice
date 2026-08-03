FROM python:3.11-slim
RUN pip install boto3 moto
WORKDIR /usr/src/myapp
COPY app.py .
CMD ["python", "app.py"]

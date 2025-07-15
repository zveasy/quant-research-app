FROM python:3.12-slim
WORKDIR /app
COPY cost_alert.py .
RUN pip install requests
CMD ["python", "cost_alert.py"]

FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn

EXPOSE 5000

CMD ["gunicorn", "-c", "app/gunicorn.conf.py", "--bind", "0.0.0.0:5000", "main:app", "--workers=1", "--threads=3"]
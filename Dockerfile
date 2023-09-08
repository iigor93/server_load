FROM python:3.10

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . /app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
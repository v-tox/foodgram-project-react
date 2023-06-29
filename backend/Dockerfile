# почитала треды в пачке,
# советуют прописать версию slim для экономии места.
# не уверена насколько это жизнеспособно, буду признательна за совет
FROM python:3.9
WORKDIR /app
RUN pip install gunicorn==20.1.0
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "foodgram.wsgi:application"]
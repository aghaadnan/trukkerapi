FROM python:3.6.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./main.py /code/

CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8000"]


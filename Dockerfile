FROM python:3.10 as base

WORKDIR /app

COPY config.py config.py
COPY main.py main.py
COPY Implementation.py Implementation.py

FROM base as build
COPY . .
RUN pip install poetry
RUN poetry export --without-hashes -o /requirements.txt

FROM base as production
COPY --from=build /requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

CMD ["python","main.py"]

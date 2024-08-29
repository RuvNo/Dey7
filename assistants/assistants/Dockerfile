FROM python:3.11.5-slim

WORKDIR /app

ENV OPENAPI_KEY /'no_key_provided'

COPY requirements.txt .
COPY assistants_solution.py .
COPY ./source_files ./source_files

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "assistants_solution.py"]

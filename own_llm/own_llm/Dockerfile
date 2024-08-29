FROM python:3.11.5-slim

WORKDIR /app

COPY requirements.txt .
COPY own_llm_solution.py .
COPY ./source_files ./source_files

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "./own_llm_solution.py"]

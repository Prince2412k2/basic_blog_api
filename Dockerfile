FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

#--------------------------------------------------------------------#

FROM python:3.12-slim AS runtime 

RUN useradd -m appuser 
WORKDIR /app

COPY --from=builder /install /usr/local

COPY blog_crud ./blog_crud

EXPOSE 8000

USER appuser 

CMD ["uvicorn", "blog_crud.main:app", "--host", "0.0.0.0", "--port", "8000"]

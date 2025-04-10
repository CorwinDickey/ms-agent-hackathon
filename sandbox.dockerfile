FROM python:latest

RUN apt-get update && \
  apt-get install -y build-essential && \
  rm -rf /var/lib/apt/lists/*

RUN useradd -m sandboxuser
USER sandboxuser
WORKDIR /home/sandboxuser

COPY sandbox_requirements.txt .
RUN pip install --no-cache-dir -r sandbox_requirements.txt

CMD [ "python", "--version" ]
FROM python:3.12-slim-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt update && apt install -y \
    libpq-dev \
    gcc \
    && apt clean
RUN useradd -ms /bin/bash quant


USER quant
RUN mkdir /home/quant/code

WORKDIR /home/quant/code
ENV PATH="/home/quant/.local/bin:${PATH}"

COPY --chown=quant:quant EmporIO/requirements.txt .
RUN pip install --user -r requirements.txt

COPY --chown=quant:quant ../DataManager DataManager
RUN pip install --user -e DataManager

COPY --chown=quant:quant ../Quantify Quantify
RUN pip install --user -e Quantify

COPY --chown=quant:quant EmporIO .

WORKDIR /home/quant/code/EmporIO

CMD ["python", "main.py"]

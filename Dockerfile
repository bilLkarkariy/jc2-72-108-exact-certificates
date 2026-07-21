FROM python:3.14.6-slim-bookworm@sha256:86f975aca15cf04a40b399eebede9aea7c82eae084d1f1a0a6ef6bcaae871a30

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        libdigest-sha-perl \
        unzip \
    && apt-get clean \
    && find /var/lib/apt/lists -mindepth 1 -delete

WORKDIR /audit
COPY requirements-lock.txt /audit/requirements-lock.txt
RUN python -m pip install --no-cache-dir --require-hashes -r requirements-lock.txt

COPY scripts /audit/scripts
COPY tests /audit/tests

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["/audit/scripts/clean_room_replay.sh"]

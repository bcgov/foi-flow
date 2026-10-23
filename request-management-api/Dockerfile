# For more information, please refer to https://aka.ms/vscode-docker-python
# FROM python:3.8

# Necessary to pull images from bcgov and not hit Dockerhub quotas.
FROM python:3.13.17-bookworm@sha256:a3799099b64fd333f262768c7a64733f6e4edb7bc569813710a100214bdcf278
EXPOSE 6402
RUN set -eux; apt-get update; apt-get install -y --no-install-recommends ca-certificates curl netbase wget libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 fonts-dejavu-core libexpat1 libexpat1-dev; rm -rf /var/lib/apt/lists/*

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.txt
COPY ./ /app

# Creates a non-root user and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN useradd appuser && chown -R appuser /app
#USER appuser

RUN chmod u+x /app/entrypoint.sh
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]

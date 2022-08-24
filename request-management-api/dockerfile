# For more information, please refer to https://aka.ms/vscode-docker-python
# FROM python:3.8

# Necessary to pull images from bcgov and not hit Dockerhub quotas.
FROM artifacts.developer.gov.bc.ca/docker-remote/python:3.8.5-buster
EXPOSE 6402

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

COPY ./ /app
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt

# Creates a non-root user and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN useradd appuser && chown -R appuser /app
#USER appuser

RUN chmod u+x /app/entrypoint.sh
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
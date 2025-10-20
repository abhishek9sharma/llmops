# Use an official Python runtime as a parent image
FROM python:3.10
#FROM public.ecr.aws/docker/library/python:3.12-slim
EXPOSE 8001
ARG GR_TOKEN
#RUN echo "The guardrails token is: $GR_TOKEN"
ENV GR_TOKEN=${GR_TOKEN}
RUN apt-get update && apt-get install -y git
WORKDIR /grserver
COPY . /grserver
RUN ls -lah

RUN python -m pip install uv
#RUN python -m uv pip install --no-cache-dir -r requirements.txt
RUN python -m uv pip install -e . --prerelease=allow
RUN  python -m uv pip install --upgrade cryptography  pyopenssl==22.1.0
#ENV NLTK_DATA=/opt/nltk_data
#RUN python -m nltk.downloader -d /opt/nltk_data punkt

EXPOSE 8001
RUN guardrails configure --disable-metrics --enable-remote-inferencing --token ${GR_TOKEN}
#RUN guardrails hub install hub://guardrails/llamaguard_7b
#RUN guardrails hub install hub://guardrails/guardrails_pii|true
RUN guardrails hub install hub://guardrails/toxic_language
RUN guardrails hub install hub://guardrails/guardrails_pii
CMD ["uvicorn", "grserver.restapi.rootsvc:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
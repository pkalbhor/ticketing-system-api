# docker build -f docker/Dockerfile -t my_app .
# docker run -it -p 8080:8080 my_app

FROM pkalbhor/ubuntu-with-python:latest
USER root
RUN apt-get update -y
RUN apt-get upgrade -y

USER pritam
COPY . ${HOME}
RUN pip install -r requirements.txt
RUN mkdir -p data

EXPOSE 8080
ENTRYPOINT ["tini", "-g", "--"]
CMD [ "waitress-serve", "--port=8080", "run:app"]
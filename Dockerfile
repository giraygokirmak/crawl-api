FROM arm64v8/ubuntu:focal
RUN apt update 
RUN DEBIAN_FRONTEND=noninteractive TZ=Europe/Istanbul apt-get install -yq tzdata python3 python3-dev libmysqlclient-dev python3-pip&& \
    ln -fs /usr/share/zoneinfo/Europe/Istanbul /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata
ADD src /src
RUN python3 -m pip install -r /src/requirements.txt
WORKDIR /src
ENTRYPOINT [ "python3","app.py"]

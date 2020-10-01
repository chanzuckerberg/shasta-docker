FROM ubuntu:20.04
MAINTAINER Bhal Agashe, bagashe@chanzuckerberg.com

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=US/Los_Angeles
RUN apt-get update && \
    apt-get install -y git curl python3 python3-pip sudo && \
    apt-get clean && \
    apt-get purge && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Download Shasta releases.
WORKDIR /opt
RUN curl -O -L https://github.com/chanzuckerberg/shasta/releases/download/0.5.1/shasta-Linux-0.5.1
RUN chmod ugo+x shasta-Linux-0.5.1
RUN curl -O -L https://github.com/chanzuckerberg/shasta/releases/download/0.5.0/shasta-Linux-0.5.0
RUN chmod ugo+x shasta-Linux-0.5.0

# Download & install prereqs. Every time a new pre-requisite is added, a new Docker image needs to be created.
RUN curl -O -L https://raw.githubusercontent.com/chanzuckerberg/shasta/master/scripts/InstallPrerequisites-Ubuntu.sh
RUN chmod ugo+x InstallPrerequisites-Ubuntu.sh
RUN ./InstallPrerequisites-Ubuntu.sh
RUN apt-get clean && apt-get purge

# setup entrypoint
COPY wrapper.py /opt/wrapper.py

WORKDIR /data
ENTRYPOINT ["python3", "/opt/wrapper.py"]

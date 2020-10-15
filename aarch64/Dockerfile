FROM arm64v8/ubuntu:20.04
MAINTAINER Bhal Agashe, bagashe@chanzuckerberg.com

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=US/Los_Angeles
RUN apt-get update && \
    apt-get install -y bash tzdata git curl python3 sudo && \
    apt-get clean && \
    apt-get purge && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


# Download Shasta releases.
WORKDIR /opt
COPY downloadReleases.sh /opt/downloadReleases.sh
RUN bash -e /opt/downloadReleases.sh

# setup entrypoint
COPY wrapper.py /opt/wrapper.py

WORKDIR /output
ENTRYPOINT ["python3", "/opt/wrapper.py"]

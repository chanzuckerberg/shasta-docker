FROM arm64v8/ubuntu:20.04
LABEL org.opencontainers.image.authors="bruce@chanzuckerberg.com"
LABEL org.opencontainers.image.source https://github.com/chanzuckerberg/shasta-docker

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=US/Los_Angeles
RUN apt-get update && \
    apt-get install -y bash tzdata git curl python3 sudo && \
    apt-get clean && \
    apt-get purge && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


# Download Shasta releases.
WORKDIR /opt
COPY downloadAndInstall.sh /opt/downloadAndInstall.sh
RUN bash -e /opt/downloadAndInstall.sh

# setup entrypoint
COPY wrapper.py /opt/wrapper.py

WORKDIR /output
ENTRYPOINT ["python3", "/opt/wrapper.py"]


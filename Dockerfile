FROM ubuntu:22.04
LABEL org.opencontainers.image.authors="bruce@chanzuckerberg.com"
LABEL org.opencontainers.image.source https://github.com/chanzuckerberg/shasta-docker

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=US/Los_Angeles

# Build shasta release
ARG BUILD_ID
WORKDIR /opt

RUN apt-get update && apt install -y git
RUN git clone https://github.com/chanzuckerberg/shasta.git
WORKDIR /opt/shasta
RUN if [[ -z "${SHASTA_VERSION}" ]]; then \
      git checkout tags/${BUILD_ID} -b ${BUILD_ID} \
      BUILD_ID="Shasta Release ${SHASTA_VERSION}" ; \
    else \
      BUILD_ID="Shasta Nightly" ; \
    fi
RUN /opt/shasta/scripts/InstallPrerequisites-Ubuntu.sh
RUN mkdir shasta-build
WORKDIR /opt/shasta-build
RUN cmake ../shasta -DBUILD_ID=${BUILD_ID} && \
    make -j 2 all && \
    make install/strip && \
    mv shasta-install /opt/shasta-Ubuntu-22.04
RUN rm -rf /opt/shasta /opt/shasta-build

WORKDIR /opt/shasta-Ubuntu-22.04
ENTRYPOINT ["/opt/shasta-Ubuntu-22.04/bin/shasta"]


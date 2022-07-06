FROM ubuntu:22.04
LABEL org.opencontainers.image.authors="bruce@chanzuckerberg.com"
LABEL org.opencontainers.image.source https://github.com/chanzuckerberg/shasta-docker

ARG DEBIAN_FRONTEND=noninteractive
ARG SHASTA_VERSION

ENV TZ=US/Los_Angeles

# cloned shasta repo to local when building locally, this is done by github action in workflow
WORKDIR /opt
COPY shasta /opt/shasta

# install prerequisite from shasta script to install build tools
RUN /opt/shasta/scripts/InstallPrerequisites-Ubuntu.sh

# build shasta binary
RUN mkdir /opt/shasta-build
WORKDIR /opt/shasta-build
RUN cmake ../shasta -DBUILD_ID="Shasta Release ${SHASTA_VERSION:-Nightly}" && \
    make -j 2 all && \
    make install/strip

# clean up
RUN mv shasta-install /opt/shasta-Ubuntu-22.04
RUN rm -rf /opt/shasta /opt/shasta-build

WORKDIR /opt/shasta-Ubuntu-22.04
ENTRYPOINT ["/opt/shasta-Ubuntu-22.04/bin/shasta"]


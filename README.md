Docker images for doing _de-novo_ assembly using Shasta.

### How to install Docker?
Docker can be installed on most platforms. Detailed instructions available at https://docs.docker.com/engine/install/

### How to manage Docker as a non-root user in Linux?
https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user

### How to use the Shasta Docker images?
```
docker run -v `pwd`:/output \
    ghcr.io/chanzuckerberg/shasta:latest \
    <SHASTA-VERSION-STRING> \
    --input input.fasta

OR

docker run --privileged -v `pwd`:/output \
    ghcr.io/chanzuckerberg/shasta:latest \
    <SHASTA-VERSION-STRING> \
    --input input.fasta --memoryMode filesystem --memoryBacking 2M

Accepted values for SHASTA-VERSION-STRING are:
    0.6.0         : Shasta release 0.6.0
    0.5.1         : Shasta release 0.5.1
    0.5.0         : Shasta release 0.5.0
    0.4.0         : Shasta release 0.4.0
    0.3.0         : Shasta release 0.3.0
    0.2.0         : Shasta release 0.2.0
    0.1.0         : Shasta release 0.1.0
    latest-commit : This will download and build the current main branch of chanzuckerberg/shasta
    <COMMIT-HASH> : This will download and build the main branch of chanzuckerberg/shasta at the given commit
```
The commands listed above assume that the reads are present in the current working directory. If the reads are at a different location, you can use the following variation.

```
docker run -v `pwd`:/output \
    -v /path/to/folder/containing/reads:/reads:ro \
    ghcr.io/chanzuckerberg/shasta:latest \
    <SHASTA-VERSION-STRING> \
    --input /reads/input.fasta
```

Detailed information about running a Shasta assembly can be found at https://chanzuckerberg.github.io/shasta/Running.html. 

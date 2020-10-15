Docker images for doing _de-novo_ assembly using Shasta.

### How to install Docker?
Docker can be installed on most platforms. Detailed instructions available at https://docs.docker.com/engine/install/

### How to manage Docker as a non-root user in Linux?
https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user

### How to use the Shasta Docker images?
Shasta Docker images are available for the x86_64 (amd64) & arm64v8 (aarch64) platforms.
| Platform    | Docker image |
| ----------- | -----------  |
| x86_64      | https://github.com/orgs/chanzuckerberg/packages/container/package/shasta       |
| arm64v8   | https://github.com/orgs/chanzuckerberg/packages/container/package/shasta-arm64v8        |

You can use the following command to see which Shasta releases are available and how to use them.
```
docker run ghcr.io/chanzuckerberg/shasta:latest --help

OR

docker run ghcr.io/chanzuckerberg/shasta-arm64v8:latest --help
```
#### Examples
1. If the reads (fasta/fastq) files are located at `/path/to/folder/containing/reads` and you would like the Assembly Directory be created in the current working directory, then
```
docker run -u `id -u`:`id -g` \
    -v `pwd`:/output \
    -v /path/to/folder/containing/reads:/reads:ro \
    ghcr.io/chanzuckerberg/shasta:latest \
    <SHASTA-VERSION-STRING> \
    --input /reads/input.fasta
```
2. If you would also like to provide a Shasta `conf` file, located in the current working directory, then
```
docker run -u `id -u`:`id -g` \
    -v `pwd`:/output \
    -v /path/to/folder/containing/reads:/reads:ro \
    ghcr.io/chanzuckerberg/shasta:latest \
    <SHASTA-VERSION-STRING> \
    --input /reads/input.fasta \
    --conf Nanopore-Sep2020.conf
```
3. If you would also like to override specific configuration parameters, then
```
docker run -u `id -u`:`id -g` \
    -v `pwd`:/output \
    -v /path/to/folder/containing/reads:/reads:ro \
    ghcr.io/chanzuckerberg/shasta:latest \
    <SHASTA-VERSION-STRING> \
    --input /reads/input.fasta \
    --conf Nanopore-Sep2020.conf \
    --MinHash.minBucketSize 13 \
    --assemblyDirectory ShastaRunInDocker
```

Detailed information about running a Shasta assembly can be found at https://chanzuckerberg.github.io/shasta/Running.html. 

### Note
Optimal Shasta performance can be achieved by using `--memoryMode filesystem --memoryBacking 2M`. However, this requires the `--privileged` flag, as shown below

```
docker run --privileged -u `id -u`:`id -g` \
    -v `pwd`:/output \
    ghcr.io/chanzuckerberg/shasta:latest \
    <SHASTA-VERSION-STRING> \
    --input input.fasta --memoryMode filesystem --memoryBacking 2M
```

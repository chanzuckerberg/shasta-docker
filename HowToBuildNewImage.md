New Docker images need to be created after every Shasta release. 

### Setup
1. Install Docker on the machine that will be used for building these docker images. Detailed instructions available at https://docs.docker.com/engine/install/

2. [Optional, but recommended] Set up Docker to be managed as a non-root user by following instructions at https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user. If you do this step, you won't need to prefix docker commands with `sudo`.

3. Create a Github personal access token using instructions at https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token. The personal access token must have necessary permissions granted to it, specificially `delete:packages`, `write:packages`, `repo` & `workflow`. The token also needs to be authorized for accessing `chanzuckerberg` org in Github.

4. Ensure that you have `Write` permission granted at https://github.com/orgs/chanzuckerberg/packages/container/shasta/settings 

### Prepare to create new images
1. Clone the repository by running `git clone https://github.com/chanzuckerberg/shasta-docker`

2. Edit `shasta-docker/x86_64/wrapper.py` & `shasta-docker/aarch64/wrapper.py` to add the new Shasta release version number (at two places in each file).

3. Edit `shasta-docker/x86_64/Makefile` & `shasta-docker/aarch64/Makefile` to bump the `shasta_version` to the next integer. This is the docker image/package version and is unrelated to the Shasta version.

4. Commit the changes and push them upstream.

### How to create a x86_64 image?
The following needs to be done on an x86_64 machine.
1. Log in ghcr.io by running `echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin`
2. Run `git clone https://github.com/chanzuckerberg/shasta-docker && cd shasta-docker/x86_64`
3. Build a new Docker image by running `make build`
4. Test if the new image has the latest Shasta release by running `docker run ghcr.io/chanzuckerberg/shasta:latest --help`
5. Publish the new Docker image by running `make push`
6. Verify that the new image shows up on https://github.com/orgs/chanzuckerberg/packages/container/package/shasta

### How to create an arm64v8 image?
The following needs to be done on an arm64v8 machine. E.g. Graviton2 ec2 instances.
1. Log in ghcr.io by running `echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin`
2. Run `git clone https://github.com/chanzuckerberg/shasta-docker && cd shasta-docker/aarch64`
3. Build a new Docker image by running `make build`
4. Test if the new image has the latest Shasta release by running `docker run ghcr.io/chanzuckerberg/shasta-arm64v8:latest --help`
5. Publish the new Docker image by running `make push`
6. Verify that the new image shows up on https://github.com/orgs/chanzuckerberg/packages/container/package/shasta-arm64v8


### Commands to cleanup local Docker state on your ec2 instance (while building an image)
Docker keeps around intermediate layers/images and if your machine doesn't have enough memory, you might run into issues. You can blow away these cached layers/images by running the following commands.

```
docker system prune
docker rm -f $(docker ps -aq)
docker rmi -f $(docker images -q)

```

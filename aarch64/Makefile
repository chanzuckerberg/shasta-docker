image_name = chanzuckerberg/shasta-arm64v8
shasta_version = 9
tag = ${shasta_version}

# Steps
build:
	# do the docker build
	docker build -t ${image_name}:${tag} .
	docker tag ${image_name}:${tag} ghcr.io/${image_name}:${tag}
	docker tag ${image_name}:${tag} ghcr.io/${image_name}:latest

push:
	# You need to authenticate first using the following command.
	# echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin
	docker push ghcr.io/${image_name}:${tag}
	docker push ghcr.io/${image_name}:latest


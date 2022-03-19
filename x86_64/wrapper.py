#!/usr/bin/python3

import sys
import os
import os.path
import subprocess
import time
import re

# Platform specific binary name prefix
shastaBinaryPrefix = "shasta-Linux-"

helpMessage = """
Usage:
    docker run -u `id -u`:`id -g` \\
        -v `pwd`:/output \\
        <DOCKER-IMAGE> \\
        <SHASTA-VERSION-STRING> \\
        --input input.fasta \\
        --config <CONFIG>

    OR

    docker run --privileged \\
        -v `pwd`:/output \\
        <DOCKER-IMAGE> \\
        <SHASTA-VERSION-STRING> \\
        --input input.fasta \\
        --config <CONFIG> \\
        --memoryMode filesystem --memoryBacking 2M

    Accepted values for SHASTA-VERSION-STRING are:
        <RELEASE-TAG> : This will run a specified release, eg, 0.9.0.
        latest-commit : This will download and build the current main branch of chanzuckerberg/shasta
        <COMMIT-HASH> : This will download and build the main branch of chanzuckerberg/shasta at the given commit

    The available Shasta releases can be found at https://github.com/chanzuckerberg/shasta/releases.
    This image contains cached executables for the following <RELEASE-TAG> values:
{}

Shasta documentation can be found at https://chanzuckerberg.github.io/shasta/
"""


def usage():
    tags = sorted(
        [tag for tag in get_locally_available_releases().keys()],
        key=lambda t: tuple(map(int, (t.split(".")))),
        reverse=True,
    )
    msg = "       {:<14s} : Shasta release {:s}"
    available_versions = "\n".join([msg.format(tag, tag) for tag in tags])
    print(helpMessage.format(available_versions), flush=True)
    return


def clone():
    try:
        subprocess.check_call(
            ["git", "clone", "https://github.com/chanzuckerberg/shasta.git"]
        )
    except subprocess.CalledProcessError as err:
        print(err, flush=True)
        sys.exit(2)


def pullLatest():
    try:
        subprocess.check_call(["git", "pull", "--rebase"])
    except subprocess.CalledProcessError:
        print(
            '"git pull --rebase" command failed. Docker needs Internet access.',
            flush=True,
        )
        sys.exit(2)


def getValidCommitHash(commitHash):
    if commitHash == "latest-commit":
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode("utf-8")
            .rstrip()
        )

    try:
        subprocess.check_call(["git", "cat-file", "-t", commitHash])
    except subprocess.CalledProcessError:
        print(f"{commitHash} is not a valid git commit hash.", flush=True)
        usage()
        sys.exit(2)
    return commitHash


def releaseTagIsValid(releaseTag):
    # Shasta uses semantic versioning. Weak test for something that looks like a semver.
    return re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", releaseTag) is not None


def build(shastaVersion):
    cwd = os.getcwd()

    # shastaVersion could be a commit-hash or 'latest-commit'
    print("Downloading and building Shasta code at the requested commit.", flush=True)
    os.chdir("/tmp")
    clone()
    os.chdir("/tmp/shasta")

    pullLatest()

    shastaVersion = getValidCommitHash(shastaVersion)
    print(f"Building Shasta at commit - {shastaVersion}")

    subprocess.run(["git", "checkout", shastaVersion], check=True)

    subprocess.run(["mkdir", "-p", "/tmp/shasta-build"])
    os.chdir("/tmp/shasta-build")

    print("Configuring & Building Shasta ...", flush=True)
    subprocess.run(
        [
            "cmake",
            "../shasta",
            "-DBUILD_DYNAMIC_LIBRARY=OFF",
            "-DBUILD_DYNAMIC_EXECUTABLE=OFF",
            "-DBUILD_WITH_HTTP_SERVER=OFF",
        ],
        check=True,
    )

    subprocess.run(["make", "install/strip", "-j"], check=True)

    print("Done building Shasta", flush=True)

    shastaBinary = "/tmp/shasta-build/shasta-install/bin/shasta"

    # Go back to the original working directory.
    os.chdir(cwd)

    return shastaBinary


def get_locally_available_releases():
    """Return the Shasta releases available in this image."""
    install_dir = "/opt/"
    binary_prefix = f"/opt/{shastaBinaryPrefix}"
    shasta_executables = [
        full_path
        for p in os.listdir(install_dir)
        if (full_path := os.path.join(install_dir, p))
        and p.startswith(shastaBinaryPrefix)
        and os.path.isfile(full_path)
        and os.access(full_path, os.X_OK)
    ]
    # { tag_name: full_path }
    return {
        full_path[len(binary_prefix) :]: full_path for full_path in shasta_executables
    }


def download_gh_release(tag_name):
    """
    Attempt to download the given release tag.  Return None if the tag_name is not a release.
    Return the binary file location if successful.
    """
    shastaBinary = f"/tmp/{shastaBinaryPrefix}{tag_name}"
    downloadURL = f"https://github.com/chanzuckerberg/shasta/releases/download/{tag_name}/{shastaBinaryPrefix}{tag_name}"
    try:
        res = subprocess.run(
            ["curl", "--fail", "--silent", "-L", "--output", shastaBinary, downloadURL]
        )
        if res.returncode == 0:
            return shastaBinary
        if res.returncode == 22:
            # curl indicating a HTTP response 400 or above, ie, typically means the tag is not a release.
            return None
        # otherwise, an unexpected error
        res.check_returncode()
    except subprocess.CalledProcessError as err:
        print(err, flush=True)
        sys.exit(2)


def main(argv):
    if len(argv) == 0 or "help" in argv or "--help" in argv:
        usage()
        sys.exit(1)

    shastaVersion = argv[0]
    shastaArgs = argv[1:]

    print(f"Shasta Version : {shastaVersion}", flush=True)

    local_releases = get_locally_available_releases()
    if shastaVersion in local_releases:
        shastaBinary = local_releases[shastaVersion]
    elif not (shastaBinary := download_gh_release(shastaVersion)):
        if releaseTagIsValid(shastaVersion):
            # Unavailable release tag was specified. shastaVersion is not latest-commit or a valid commit hash.
            print(
                f"Shasta version {shastaVersion} is not available on this platform. Run the command with `--help` to see available options."
            )
            sys.exit(2)
        # Otherwise, attempt to build it
        shastaBinary = build(shastaVersion)

    time.sleep(2)

    # Run the right version of Shasta.
    print(f"\n\nUsing {shastaBinary} Shasta executable.", flush=True)
    print(
        "\nRunning Shasta assembly. You can follow along by running `tail -f shasta_assembly.log` in the output directory.\n...\n",
        flush=True,
    )
    shastaLogFile = open("shasta_assembly.log", "w")
    shastaCmdArr = [shastaBinary] + shastaArgs
    shastaReturncode = subprocess.run(
        shastaCmdArr, stdout=shastaLogFile, stderr=subprocess.STDOUT
    ).returncode
    shastaLogFile.close()

    shastaAssemblyDirectory = "ShastaRun"
    if "--assemblyDirectory" in shastaArgs:
        idx = shastaArgs.index("--assemblyDirectory")
        shastaAssemblyDirectory = shastaArgs[idx + 1]

    subprocess.run(["cp", "shasta_assembly.log", shastaAssemblyDirectory])

    print("\n\nDone. Check the assembly directory for results.", flush=True)
    return shastaReturncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

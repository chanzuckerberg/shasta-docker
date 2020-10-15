#!/usr/bin/python3

import sys
import os
import subprocess
import time

helpMessage = """
Usage:
    docker run -u `id -u`:`id -g` \\
        -v `pwd`:/output \\
        <DOCKER-IMAGE> \\
        <SHASTA-VERSION-STRING> \\
        --input input.fasta

    OR

    docker run --privileged \\
        -v `pwd`:/output \\
        <DOCKER-IMAGE> \\
        <SHASTA-VERSION-STRING> \\
        --input input.fasta --memoryMode filesystem --memoryBacking 2M

    Accepted values for SHASTA-VERSION-STRING are:
        0.6.0         : Shasta release 0.6.0
        latest-commit : This will download and build the current main branch of chanzuckerberg/shasta
        <COMMIT-HASH> : This will download and build the main branch of chanzuckerberg/shasta at the given commit
    
"""

def usage():
    print(helpMessage, flush=True)
    return

def clone():
    try:
        subprocess.check_call(['git', 'clone', 'https://github.com/chanzuckerberg/shasta.git'])
    except subprocess.CalledProcessError as err:
        print(err, flush=True)
        sys.exit(2)
    

def pullLatest():
    try:
        subprocess.check_call(['git', 'pull', '--rebase'])
    except subprocess.CalledProcessError:
        print('"git pull --rebase" command failed. Docker needs Internet access.', flush=True)
        sys.exit(2)  
    

def getValidCommitHash(commitHash):
    if commitHash == 'latest-commit':
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').rstrip()
        
    try:
        subprocess.check_call(['git', 'cat-file', '-t', commitHash])
    except subprocess.CalledProcessError:
        print('{} is not a valid git commit hash.'.format(commitHash, flush=True))
        usage()
        sys.exit(2)
    return commitHash


def releaseTagIsValid(releaseTag):
    # Shasta uses semantic versioning.
    return 2 == releaseTag.count('.')


def main(argv):
    if 'help' in argv or '--help' in argv:
        usage()
        sys.exit(1)

    availableShastaReleases = ['0.6.0']
    shastaVersion = argv[0]
    shastaArgs = argv[1:]
    
    print("Shasta Version : {}".format(shastaVersion), flush=True)
    shastaBinary = "/opt/shasta-Linux-{}".format(shastaVersion)
    
    if shastaVersion not in availableShastaReleases:
        if releaseTagIsValid(shastaVersion):
            # Unavailable release tag was specified. shastaVersion is not latest-commit or a valid commit hash.
            print("Shasta version {} is not available on this platform. Run the command with `--help` to see available options.".format(shastaVersion))
            sys.exit(2)

        cwd = os.getcwd()

        # shastaVersion could be a commit-hash or 'latest-commit'
        print("Downloading and building Shasta code at the requested commit.", flush=True)
        os.chdir('/tmp')
        clone()
        os.chdir('/tmp/shasta')
        
        pullLatest()

        shastaVersion = getValidCommitHash(shastaVersion)
        print('Building Shasta at commit - {}'.format(shastaVersion))
        
        subprocess.check_call(['git', 'checkout', shastaVersion])
    
        subprocess.run(['mkdir', '-p', '/tmp/shasta-build'])
        os.chdir('/tmp/shasta-build')
        
        print('Configuring & Building Shasta ...', flush=True)
        cmakeCmd = subprocess.run(
            ['cmake', '../shasta', '-DBUILD_DYNAMIC_LIBRARY=OFF', '-DBUILD_DYNAMIC_EXECUTABLE=OFF', '-DBUILD_WITH_HTTP_SERVER=OFF'],
        )
        
        makeCmd = subprocess.run(['make', 'install/strip', '-j'])
        
        print('Done building Shasta', flush=True)

        shastaBinary = "/tmp/shasta-build/shasta-install/bin/shasta"
        
        # Go back to the original working directory.
        os.chdir(cwd)

    time.sleep(2)

    # Run the right version of Shasta.
    print("\n\nUsing {} Shasta executable.".format(shastaBinary), flush=True)
    print("\nRunning Shasta assembly. You can follow along by running `tail -f shasta_assembly.log` in the output directory.\n...\n", flush=True)
    shastaLogFile = open('shasta_assembly.log', 'w')
    shastaCmdArr = [shastaBinary] + shastaArgs
    subprocess.run(
        shastaCmdArr,
        stdout=shastaLogFile,
        stderr=subprocess.STDOUT
    )
    shastaLogFile.close()
    
    shastaAssemblyDirectory = "ShastaRun"
    if "--assemblyDirectory" in shastaArgs:
        idx = shastaArgs.index("--assemblyDirectory")
        shastaAssemblyDirectory = shastaArgs[idx + 1]

    subprocess.run(['cp', 'shasta_assembly.log', shastaAssemblyDirectory])

    print("\n\nDone. Check the assembly directory for results.", flush=True)
    return


if __name__ == '__main__':
    main(sys.argv[1:])    

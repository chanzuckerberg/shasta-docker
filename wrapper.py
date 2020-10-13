#!/usr/bin/python3

import sys
import os
import subprocess
import time

helpMessage = """
Usage:
    docker run -v `pwd`:/data <DOCKER-IMAGE> <SHASTA-VERSION-STRING> \\
        --input input.fasta

    OR

    docker run --privileged -v `pwd`:/data <DOCKER-IMAGE> <SHASTA-VERSION-STRING> \\
        --input input.fasta --memoryMode filesystem --memoryBacking 2M

    Accepted values for SHASTA-VERSION-STRING are:
        0.6.0         : Shasta release v0.6.0
        0.5.1         : Shasta release v0.5.1
        0.5.0         : Shasta release v0.5.0
        0.4.0         : Shasta release v0.4.0
        0.3.0         : Shasta release v0.3.0
        0.2.0         : Shasta release v0.2.0
        0.1.0         : Shasta release v0.1.0
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


def main(argv):
    if 'help' in argv or '--help' in argv:
        usage()
        sys.exit(1)

    availableShastaReleases = ['0.6.0', '0.5.1', '0.5.0', '0.4.0', '0.3.0', '0.2.0', '0.1.0']
    shastaVersion = argv[0]
    shastaArgs = argv[1:]

    print("Shasta Version : {}".format(shastaVersion), flush=True)
    shastaBinary = "/opt/shasta-Linux-{}".format(shastaVersion)
    
    if shastaVersion not in availableShastaReleases:
        cwd = os.getcwd()

        # shastaVersion could be a commit-hash or 'latest-commit'
        print("Downloading and building Shasta code at the requested commit.", flush=True)
        os.chdir('/opt')
        clone()
        os.chdir('/opt/shasta')
        
        # Install pre-requisites
        print('Installing pre-requisites ...', flush=True)
        logfile = open('Prerequisites-installation.log', 'w')
        subprocess.run(
            ['./scripts/InstallPrerequisites-Ubuntu.sh', '--minimal'],
            stdout=logfile,
            stderr=subprocess.STDOUT
        )
        logfile.close()
        print('Done installing pre-requisites. Check Prequisites-installation.log file for details.', flush=True)

        pullLatest()

        shastaVersion = getValidCommitHash(shastaVersion)
        print('Building Shasta at commit - {}'.format(shastaVersion))
        
        subprocess.check_call(['git', 'checkout', shastaVersion])
    
        subprocess.run(['mkdir', '-p', '/opt/shasta-build'])
        os.chdir('/opt/shasta-build')
        
        print('Configuring & Building Shasta ...', flush=True)
        cmakeCmd = subprocess.run(
            ['cmake', '../shasta', '-DBUILD_DYNAMIC_LIBRARY=OFF', '-DBUILD_DYNAMIC_EXECUTABLE=OFF', '-DBUILD_WITH_HTTP_SERVER=OFF'],
        )
        
        makeCmd = subprocess.run(['make', 'install/strip', '-j'])
        
        print('Done building Shasta', flush=True)

        subprocess.run(['cp', './shasta-install/bin/shasta', shastaBinary])
        
        # Go back to the original working directory.
        os.chdir(cwd)

    time.sleep(2)

    # Run the right version of Shasta.
    print("\n\nUsing {} Shasta executable.".format(shastaBinary), flush=True)
    shastaCmdArr = [shastaBinary] + shastaArgs
    subprocess.run(shastaCmdArr)
    
    print("\n\nAssembly is complete. Check the assembly directory for results.", flush=True)
    return


if __name__ == '__main__':
    main(sys.argv[1:])    

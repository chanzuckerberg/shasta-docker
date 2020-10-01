#!/usr/bin/python3

import sys
import os
import subprocess

helpMessage = """
Usage:
    docker run -v `pwd`:/data <DOCKER-IMAGE> <SHASTA-VERSION-STRING> \
        --input input.fasta

    OR

    docker run --privileged -v `pwd`:/data <DOCKER-IMAGE> <SHASTA-VERSION-STRING> \
        --input input.fasta --memoryMode filesystem --memoryBacking 2M

    Accepted values for SHASTA-VERSION-STRING are:
    1. latest : This will download and build the current main branch of chanzuckerberg/shasta
    2. 0.6.0 : Shasta release v0.6.0
    3. 0.5.1 : Shasta release v0.5.1
    4: 0.5.0 : Shasta release v0.5.0

"""

def usage():
    print(helpMessage)
    return

def main(argv):
    supportedShastaVersions = ['latest', '0.6.0', '0.5.1', '0.5.0']
    shastaVersion = argv[0]
    
    if shastaVersion not in supportedShastaVersions:
        usage()
        exit(2)

    print("Shasta Version : {}".format(shastaVersion))

    shastaArgs = argv[1:]

    if shastaVersion == 'latest':
        cwd = os.getcwd()

        print("Downloading and building the latest Shasta code")
        os.chdir('/opt')

        try:
            pullCmd = subprocess.run(
                ['git', 'clone', 'https://github.com/chanzuckerberg/shasta.git'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if (pullCmd.stderr):
                print(pullCmd.stderr.decode('utf-8'))

            os.chdir('/opt/shasta')

            newHeadHash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').rstrip()
            print("Git HEAD at: {}".format(newHeadHash), flush=True)
        
            subprocess.run(['mkdir', '-p', '/opt/shasta-build'])
            os.chdir('/opt/shasta-build')
            
            print('Configuring & Building Shasta ...', flush=True)
            cmakeCmd = subprocess.run(['cmake', '../shasta'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if (cmakeCmd.stderr):
                print(cmakeCmd.stderr.decode('utf-8'))

            makeCmd = subprocess.run(['make', 'install/strip', '-j'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if (makeCmd.stderr):
                print()
                print("-----------------------------------------------------")
                print("Warnings & Errors encountered during building Shasta:")
                print("-----------------------------------------------------")
                print(makeCmd.stderr.decode('utf-8'))
                print("-----------------------------------------------------")
                print()

            print('Done building Shasta', flush=True)

            subprocess.run(['cp', './shasta-install/bin/shasta', '/opt/shasta-Linux-latest'])
        
        except subprocess.CalledProcessError as err:
            print(err)
        
        os.chdir(cwd)

    shastaBinary = "/opt/shasta-Linux-{}".format(shastaVersion)
    
    # Run the right version of Shasta.
    shastaCmdArr = [shastaBinary] + shastaArgs
    shastaCmd = subprocess.run(shastaCmdArr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    with open('shasta_stdout.log', 'w') as stdoutFile:
        stdoutFile.write(shastaCmd.stdout.decode('utf-8'))
    
    with open('shasta_stderr.log', 'w') as stderrFile:
        stderrFile.write(shastaCmd.stderr.decode('utf-8'))

    return


if __name__ == '__main__':
    main(sys.argv[1:])    

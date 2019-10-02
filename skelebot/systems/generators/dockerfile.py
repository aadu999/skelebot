"""Dockerfile Generator"""

import os
from ..execution import commandBuilder

FILE_PATH = "{path}/Dockerfile"

PY_INSTALL = "RUN [\"pip\", \"install\", \"{dep}\"]\n"
R_INSTALL = "RUN [\"Rscript\", \"-e\", \"install.packages('{dep}', repo='https://cloud.r-project.org'); library({dep})\"]\n"
R_INSTALL_VERSION = "RUN [\"Rscript\", \"-e\", \"library(devtools); install_version('{depName}', version='{version}', repos='http://cran.us.r-project.org'); library({depName})\"]\n"
R_INSTALL_GITHUB = "RUN [\"Rscript\", \"-e\", \"library(devtools); install_github('{depPath}'); library({depName})\"]\n"
R_INSTALL_FILE = "COPY {depPath} {depPath}\n"
R_INSTALL_FILE += "RUN [\"Rscript\", \"-e\", \"install.packages('/app/{depPath}', repos=NULL, type='source'); library({depName})\"]\n"

DOCKERFILE = """
# This Dockerfile was generated by Skelebot
# Editing this file manually is not advised as all changes will be overwritten by Skelebot

"""

def buildDockerfile(config):
    """Generates the Dockerfile based on values from the Config object"""

    # Setup the basics of all dockerfiless
    docker = DOCKERFILE
    docker += "FROM {baseImage}\n".format(baseImage=config.getBaseImage())
    docker += "MAINTAINER {maintainer} <{contact}>\n".format(maintainer=config.maintainer, contact=config.contact)
    docker += "WORKDIR /app\n"

    # Add language dependencies
    if (config.language == "Python"):
        for dep in config.dependencies:
            docker += PY_INSTALL.format(dep=dep)
    if (config.language == "R"):
        for dep in config.dependencies:
            depSplit = dep.split(":")
            if ("github:" in dep):
                docker += R_INSTALL_GITHUB.format(depPath=depSplit[1], depName=depSplit[2])
            elif ("file:" in dep):
                docker += R_INSTALL_FILE.format(depPath=depSplit[1], depName=depSplit[2])
            elif ("=" in dep):
                verSplit = dep.split("=")
                docker += R_INSTALL_VERSION.format(depName=verSplit[0], version=verSplit[1])
            else:
                docker += R_INSTALL.format(dep=dep)

    # Run any custom global commands
    for command in config.commands:
        docker += "RUN {command}\n".format(command=command)

    # Copy the project into the /app folder of the Docker Image
    # Ignores anything in the .dockerignore file of the project
    docker += "COPY . /app\n"

    # Pull in any additional dockerfile updates from the components
    for component in config.components:
        docker += component.appendDockerfile()

    # Set the CMD to execute the primary job by default (if there is one)
    for job in config.jobs:
        if config.primaryJob == job.name:
            docker += "CMD /bin/bash -c \"{command}\"\n"
            docker = docker.format(command=commandBuilder.build(config, job, None))

    dockerfile = open(FILE_PATH.format(path=os.getcwd()), "w")
    dockerfile.write(docker)
    dockerfile.close()

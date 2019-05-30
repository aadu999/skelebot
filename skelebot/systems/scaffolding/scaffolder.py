from ...objects.config import Config
from ...components.componentFactory import ComponentFactory
from ...systems.generators import dockerfile, dockerignore, readme, yaml
from ...common import VERSION, LANGUAGE_DEPENDENCIES
from .prompt import promptUser

import sys
import os

def scaffold(existing=False):
    # Prompt for basic project information
    print("Scaffolding Skelebot Project")
    print("--:-" * 5, "-:--" * 5)
    name = promptUser("Enter a PROJECT NAME")
    description = promptUser("Enter a PROJECT DESCRIPTION")
    maintainer = promptUser("Enter a MAINTAINER NAME")
    contact = promptUser("Enter a CONTACT EMAIL")
    language = promptUser("Enter a LANGUAGE", options=list(LANGUAGE_DEPENDENCIES.keys()))

    # Iterate over components for additional prompts and add any non-None components that are scaffolded
    components = []
    componentFactory = ComponentFactory()
    for component in componentFactory.buildComponents():
        component = component.scaffold()
        if (component is not None):
            if (isinstance(component, list)):
                components += component
            else:
                components.append(component)

    # Build the config object based on the user inputs
    config = Config(name, description, "0.1.0", VERSION, maintainer, contact, language,
                    None, False, LANGUAGE_DEPENDENCIES[language], components=components)

    # Confirm user input - allow them to back out before generating files
    print("--:-" * 5, "-:--" * 5)
    print("Setting up the", name, "Skelebot project in the current directory")
    print("(", os.getcwd(), ")")
    if (promptUser("Confirm Skelebot Setup", boolean=True) == False):
        raise Exception("Aborting Scaffolding Process")

    print("--:-" * 5, "-:--" * 5)
    if (existing == False):
        # Setting up the folder structure for the project
        print("Wiring up the skele-bones...")
        os.makedirs("config/", exist_ok=True)
        os.makedirs("data/", exist_ok=True)
        os.makedirs("models/", exist_ok=True)
        os.makedirs("notebooks/", exist_ok=True)
        os.makedirs("output/", exist_ok=True)
        os.makedirs("queries/", exist_ok=True)
        os.makedirs("src/jobs/", exist_ok=True)

        # Creating the files for the project
        print("Soldering the micro-computer to the skele-skull...")
        dockerfile.buildDockerfile(config)
        dockerignore.buildDockerignore(config)
        readme.buildREADME(config)

    # For existing projects only the skelebot.yaml file is generated
    yaml.saveConfig(config)
    print("Your Skelebot project is ready to go!")

# Button

A one file AWS DevOps tool.

Sometimes, all that you need is CloudFormation, but the official AWS command-line tool is surprisingly awkward to use. Drop *button.py* into any project that has CloudFormation templates to make life better.

## Usage

1) Copy the file *button.py* into your project
2) Create a directory for the AWS CloudFormation template file that has the same name as the environment, such as *staging*
3) Run *button.py*

For example, to create the CloudFormation stack for the staging environment:

    ./button.py create staging

Button always validates the CloudFormation template before it runs any other command. It uses the online validation service that is provided by AWS.

For more details, use the *help* option:

    ./button.py help

Button requires Python 2 or above, and the official AWS command-line utility.

## Expectations

This tool is very opinionated, and assumes that:

* The AWS CloudFormation stack should have the name *project-environment*
* Your CloudFormation template is in a directory that has the same name as the environment name
* Your CloudFormation template is in YAML format
* Your CloudFormation template file has the name *template.yaml*
* Template parameters are in a file called *parameters.json*, in the same directory as the template file
* Template tags are in a file called *tags.json*, in the same directory as the template file

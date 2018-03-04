# Button

[![Stability: Active](https://masterminds.github.io/stability/active.svg)](https://masterminds.github.io/stability/active.html)

Just drop *button.py* into any project that has CloudFormation templates. You can then manage your application environments without either a stand-alone DevOps tool, or the awkwardness of interacting with the AWS command-line utility.

## Usage

1) Copy the file *button.py* into your project
2) Put the AWS CloudFormation files in a directory with a sensible name, such as *./aws/staging*
3) Run *button.py*

For example, to create the CloudFormation stack from the files in the directory *aws/staging*, run this command:

    ./button.py create aws/staging

Button can also *update* and *delete* CloudFormation stacks:

    ./button.py update aws/staging
    ./button.py delete aws/staging

Button always validates the CloudFormation template before it runs any other command. It uses the online validation service that is provided by AWS. Use the *validate* command to check a template without actually running it:

     ./button.py validate aws/staging

For more details, use the *--help* option:

    ./button.py --help

Button requires your computer to have Python 2 or above, and [the official AWS command-line utility](https://aws.amazon.com/cli/).

## Expectations

This tool is deliberately very simple and very opinionated. It assumes that:

* You have a CloudFormation template file in YAML format. By default, it looks for a file called *template.yaml*.
* The tags for the template are in a separate JSON file, called  *tags.json*
* If your template uses parameters, these are in a JSON file. By default this file will be called *parameters.json*.
* All of these files are in the same directory

You can specify different names for these files as options if you need to.

To automatically decide the name of the CloudFormation stack, Button  looks for tags called *Project*, *Environment* and *Tier*. The AWS CloudFormation stack is assumed to have the name *project-environment-tier*, which match these tags. If this is not what you want, use the *-s* option to specify the name of the stack.

The *examples* directory contains a working set of files to show how this works.

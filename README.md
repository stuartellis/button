# Button

Sometimes, all that you need is CloudFormation, but the official AWS command-line tool is surprisingly awkward to use.

Drop *button.py* into any project that has CloudFormation templates to make life better.

## Usage

1) Copy the file *button.py* into your project
2) Put the AWS CloudFormation files in a directory with a sensible name, such as *./aws/staging*
3) Run *button.py*

For example, to create the CloudFormation stack from the files in the directory *./aws/staging*, run this command:

    ./button.py create ./aws/staging

Button always validates the CloudFormation template before it runs any other command. It uses the online validation service that is provided by AWS.

For more details, use the *--help* option:

    ./button.py --help

Button requires Python 2 or above, and [the official AWS command-line utility](https://aws.amazon.com/cli/).

## Expectations

This tool is very opinionated, and assumes that:

* You already have a CloudFormation template file
* The tags for the template are in a separate JSON file
* The parameters for the template are in a separate JSON file
* All of these files are in the same directory

It expects that your CloudFormation template file has the name *template.yaml*, 
that the parameters files is called *parameters.json*, and that the tags file is called *tags.json*. You can specify other names as options if you need to.

To automatically decide the name of the CloudFormation stack, it looks for tags called *Project* and *Environment*. The AWS CloudFormation stack is assumed to have the name *project-environment*, which match the *Project* and *Environment* tags. If this is not what you want, use the *-s* option to specify the name of the stack.

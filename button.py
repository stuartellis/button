#!/usr/bin/env python

"""

Button provides a convenient way to run an AWS CloudFormation template.

Get the latest version from: https://www.gitlab.com/stuart-ellis/button

This tool assumes that:

* You have a CloudFormation template file in YAML format. By default, it looks for a file called *template.yaml*.
* The tags for the template are in a separate JSON file, called  *tags.json*
* If your template uses parameters, these are in a JSON file. By default this file will be called *parameters.json*.
* All of these files are in the same directory

You can specify different names for these files as options if you need to.

To automatically decide the name of the CloudFormation stack,
it looks for tags called 'Project', 'Environment' and 'Tier'.
The AWS CloudFormation stack is assumed to have the name *project-environment-tier*,
to match these tags.
If this is not what you want,
use the *-s* option to specify the name of the stack.

The MIT License (MIT)

Copyright (c) 2018 Stuart Ellis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import argparse
import json
import subprocess
import sys
from os import linesep, path


VERSION = '0.6.3'

"""Map Button subcommands to AWS command-line CloudFormation subcommands"""
CF_CMD_MAPPINGS = {
    'create': 'create-stack',
    'delete': 'delete-stack',
    'update': 'update-stack',
    'validate': 'validate-template',
}

STACK_NAME_TAGS = ('Project', 'Environment', 'Tier',)


def main(mappings, stack_name_tags, version):
    """Main function for running Button from the command-line"""
    parser = build_arg_parser(set(mappings), version)
    args = vars(parser.parse_args())
    config = build_config(args, stack_name_tags)
    cmd_list = build_cmd_list(args['subcommand'], mappings)

    if config['debug']:
        print_debug_info(config)

    run_cmds(cmd_list, config)


def build_arg_parser(subcommands, version):
    """Creates the parser for the command-line arguments"""
    parser = argparse.ArgumentParser(
        description='CloudFormation made easy.')
    parser.add_argument(
        'subcommand', choices=subcommands,
        help='subcommand to run: create, update, delete or validate')
    parser.add_argument(
        'directory', help='location of the directory for CloudFormation files')
    parser.add_argument(
        '--debug',
        help='output the generated commands',
        action='store_true')
    parser.add_argument(
        '-i', '--iam',
        help='allow IAM changes in the CloudFormation template',
        action='store_true')
    parser.add_argument(
        '-j', '--json',
        help='output the results from AWS as JSON, rather than text',
        action='store_true')
    parser.add_argument(
        '-p', '--parameters',
        help='the name of the CloudFormation parameters file. Default: parameters.json',
        action='store', default='parameters.json')
    parser.add_argument(
        '-s', '--stack',
        help='the name of the CloudFormation stack. Default: reads Project, Environment and Tier tags',
        action='store')
    parser.add_argument(
        '-t', '--template',
        help='the name of the CloudFormation template file. Default: template.yaml',
        action='store', default='template.yaml')
    parser.add_argument(
        '-v', '--version',
        help='show the version of this script and exit',
        action='version', version="%(prog)s " + version)
    parser.add_argument(
        '-z', '--tags',
        help='the name of the CloudFormation tags file. Default: tags.json', action='store_true', default='tags.json')
    return parser


def build_config(args, stack_name_tags):
    """Creates a configuration from the command-line arguments"""
    config = {}

    if path.isabs(args['directory']):
        dir_path = args['directory']
    else:
        dir_path = path.abspath(args['directory'])

    if path.exists(dir_path) and path.isdir(dir_path):
        config['directory'] = dir_path
    else:
        raise IOError(
            '{0} does not exist, or is not a directory'.format(dir_path))

    cf_elements = ('parameters', 'template', 'tags')
    for cf_element in cf_elements:
        file_path = path.sep.join((dir_path, args[cf_element]))
        if path.exists(file_path) and path.isfile(file_path):
            config[cf_element] = 'file://{0}'.format(file_path)
        else:
            if cf_element == 'parameters':
                config[cf_element] = None
            else:
                raise IOError(
                    '{0} does not exist, or is not a file'.format(file_path))

    if args['stack']:
        config['stack_name'] = args['stack']
    else:
        if config['tags']:
            config['stack_name'] = get_stack_name(
                config['tags'].split('://')[1], stack_name_tags)
        else:
            raise KeyError('No tags file specified')

    if args['json']:
        config['format'] = 'json'
    else:
        config['format'] = 'text'

    if args['iam']:
        config['iam'] = True
    else:
        config['iam'] = False

    if args['debug']:
        config['debug'] = True
    else:
        config['debug'] = False

    return config


def get_stack_name(tags_file, stack_name_tags):
    """Determines the CloudFormation stack name"""
    with open(tags_file, "r") as f:
        tags = json.load(f)
        selections = {}
        for tag in tags:
            for n in stack_name_tags:
                for varient in (n, n.upper(), n.lower, n.title()):
                    if tag['Key'] == varient:
                        selections[n] = tag['Value']
    for t in stack_name_tags:
        if t not in selections:
            raise KeyError(
                'There is no "{0}" tag in {1}'.format(t, tags_file))

    return '-'.join((selections[t] for t in stack_name_tags))


def build_cf_cmd(subcommand, config):
    """Builds an AWS CLI command for CloudFormation"""
    cmd_with_options = ['aws cloudformation {0}'.format(subcommand)]

    if config['format'] == 'text':
        cmd_with_options.append('--output text')

    if subcommand != 'validate-template':
        cmd_with_options.append(
            '--stack-name {0}'.format(config['stack_name']))

    if subcommand != 'delete-stack':
        if config['template'] is not None:
            cmd_with_options.append(
                '--template-body {0}'.format(config['template']))

    if subcommand == 'create-stack' or subcommand == 'update-stack':
        if config['parameters'] is not None:
            cmd_with_options.append(
                '--parameters {0}'.format(config['parameters']))
        if config['tags'] is not None:
            cmd_with_options.append('--tags {0}'.format(config['tags']))
        if config['iam'] is True:
            cmd_with_options.append('--capabilities CAPABILITY_NAMED_IAM')

    return ' '.join(cmd_with_options)


def build_cmd_list(subcommand, mappings):
    """Builds a list of commands"""
    if subcommand in mappings:
        cmd_list = [mappings['validate']]
        if subcommand != 'validate':
            cmd_list.append(mappings[subcommand])
        return cmd_list
    else:
        raise KeyError('Invalid subcommand')


def print_debug_info(config):
    """Prints debugging information to the console"""
    print('Source Files:{0}'.format(linesep))
    print('Parameters file: {0}{1}'.format(config['parameters'], linesep))
    print('Tags file: {0}{1}'.format(config['tags'], linesep))
    print('Template file: {0}{1}'.format(config['template'], linesep))
    print('Configuration:{0}'.format(linesep))
    print(json.dumps(config, indent=4))


def run_cmds(cmd_list, config):
    """Runs the required AWS commands"""
    for subcommand in cmd_list:
        command = build_cf_cmd(subcommand, config)

        if config['debug']:
            print('{0}Command:{0}{1}{0}'.format(linesep, command))

        result = subprocess.call(command, shell=True)
        if result != 0:
            raise Exception(result)


"""Runs the main() function when this file is executed"""
if __name__ == '__main__':
    main(CF_CMD_MAPPINGS, STACK_NAME_TAGS, VERSION)

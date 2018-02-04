#!/usr/bin/env python

'''

Button provides a convenient way to run an AWS CloudFormation template.

Get the latest version from: https://www.github.com/stuartellis/button

This tool assumes that:

* You have a CloudFormation template file
* Template tags are in a separate JSON file
* Template parameters are in a separate JSON file
* All of these files are in the same directory

It expects that your CloudFormation template file has the name *template.yaml*, 
that the parameters files is called *parameters.json*, 
and that the tags file is called *tags.json*.
You can specify other names as options if you need to.

To automatically decide the name of the CloudFormation stack, 
it looks for tags called 'Project' and 'Environment'.
The AWS CloudFormation stack is then assumed to have the name *project-environment*, 
which match the 'Project' and 'Environment' tags.
If this is not what you want, use the *-s* option to specify the name of the stack.

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

'''

import argparse
import json
import subprocess
import sys
from os import path


''' Maps Button subcommands to AWS command-line CloudFormation subcommands '''
CF_CMD_MAPPINGS = {
    'create': 'create-stack',
    'delete': 'delete-stack',
    'update': 'update-stack',
    'validate': 'validate-template'
}


def main():
    ''' Main function '''

    parser = argparse.ArgumentParser(description='CloudFormation made easy.')
    parser.add_argument(
        'subcommand',
        help='subcommand to run: create, update, or delete')
    parser.add_argument(
        'directory', help='location of the directory for CloudFormation files')
    parser.add_argument(
        '-i', '--iam',
        help='allow IAM changes in the CloudFormation template',
        action='store_true')
    parser.add_argument(
        '-p', '--parameters',
        help='the name of the CloudFormation parameters file. Default: parameters.json',
        action='store_true', default='parameters.json')
    parser.add_argument(
        '-s', '--stack',
        help='the name of the CloudFormation stack. Default: reads Project and Environment tags',
        action='store_true')
    parser.add_argument(
        '-t', '--template',
        help='the name of the CloudFormation template file. Default: template.yaml',
        action='store_true', default='template.yaml')
    parser.add_argument(
        '-z', '--tags',
        help='the name of the CloudFormation tags file. Default: tags.json', action='store_true', default='tags.json')
    args = vars(parser.parse_args())
    try:
        config = build_config(args)
        run(config)
    except Exception as e:
        print('Error: {0}'.format(e))
        exit(1)


def build_cf_cmd(subcommand, stack_name,
                 template_file_uri, parameters_file_uri, tags_file_uri,
                 iam):
    ''' Builds an AWS CLI command for CloudFormation as a string '''

    command = 'aws cloudformation {0}'.format(CF_CMD_MAPPINGS[subcommand])
    cmd_with_options = [command]

    if subcommand != 'validate':
        cmd_with_options.append('--stack-name {0}'.format(stack_name))

    if subcommand != 'delete':
        if template_file_uri is not None:
            cmd_with_options.append(
                '--template-body {0}'.format(template_file_uri))

    if subcommand == 'create' or subcommand == 'update':
        if parameters_file_uri is not None:
            cmd_with_options.append(
                '--parameters {0}'.format(parameters_file_uri))
        if tags_file_uri is not None:
            cmd_with_options.append('--tags {0}'.format(tags_file_uri))
        if iam is True:
            cmd_with_options.append('--capabilities CAPABILITY_NAMED_IAM')

    print(' '.join(cmd_with_options))
    return ' '.join(cmd_with_options)


def build_config(args):
    ''' Creates a configuration from the command-line arguments '''

    config = {}
    if args['subcommand'] in CF_CMD_MAPPINGS:
        config['subcommands'] = ['validate']
        if args['subcommand'] != 'validate':
            config['subcommands'].append(args['subcommand'])
    else:
        raise KeyError('Invalid subcommand')

    if path.isabs(args['directory']):
        dir_path = args['directory']
    else:
        dir_path = path.abspath(args['directory'])

    if path.exists(dir_path) and path.isdir(dir_path):
        config['directory'] = dir_path
    else:
        raise IOError(
            "{0} does not exist, or is not a directory".format(dir_path))

    cf_elements = ('parameters', 'template', 'tags')
    for cf_element in cf_elements:
        file_path = path.sep.join((dir_path, args[cf_element]))
        if path.exists(file_path) and path.isfile(file_path):
            config[cf_element] = 'file://{0}'.format(file_path)
        else:
            raise IOError(
                "{0} does not exist, or is not a file".format(file_path))

    if args['stack']:
        config['stack_name'] = args['stack']
    else:
        if config['tags']:
            config['stack_name'] = get_stack_name(
                config['tags'].split(':/')[1])
        else:
            raise KeyError('No tags file specified')

    if args['iam']:
        config['iam'] = True
    else:
        config["iam"] = False

    return config


def get_stack_name(tags_file):
    ''' Determines the CloudFormation stack name '''

    with open(tags_file, "r") as f:
        tags = json.load(f)
        for tag in tags:
            if tag['Key'] == 'environment' or tag['Key'] == 'Environment':
                environment = tag["Value"]
            if tag["Key"] == 'project' or tag["Key"] == 'Project':
                project = tag["Value"]
    stack_name = '-'.join((environment.lower(), project.lower()))
    return stack_name


def run(config):
    ''' Run the required commands '''

    for subcommand in config['subcommands']:
        command = build_cf_cmd(subcommand,
                               config['stack_name'],
                               config['template'],
                               config['parameters'],
                               config['tags'],
                               config['iam'])
        result = subprocess.call(command, shell=True)
        if result != 0:
            raise Exception(result)


'''
Run the main() function
'''
main()

#!/usr/bin/env python
# build_cloud_formation_file.py
__version__ = 0, 0, 1

import argparse
import re

from jinja2 import Environment, FileSystemLoader

from shared import acs


def main(root_folder, template_folder):
    acs.validate_configuration_folder_structure(root_folder)
    file_path_list = list()
    acs.walk_file_tree(root_folder, acs.add_to_file_list, file_path_list)
    applications = acs.create_applications_list(len(re.findall(r'/', root_folder)), file_path_list)

    context = {
        'applications': applications
    }

    environment = Environment(loader=FileSystemLoader('cicd_app/jinja2_templates/'))
    template = environment.get_template('cloud_formation_master_in.yaml')

    with open(f'{template_folder}/template.yaml', mode='w', encoding='utf-8') as output_file:
        output_file.write(template.render(context))


if __name__ == '__main__':
    parser = argparse.ArgumentParser("build_cloud_formation_file.py")
    parser.add_argument("root_folder", help="The root folder for the application configurations, e.g. application-configuration-store", type=str)
    parser.add_argument("template_folder", help="The folder where the template.yaml file needs to be created", type=str)
    args = parser.parse_args()

    main(args.root_folder, args.template_folder)

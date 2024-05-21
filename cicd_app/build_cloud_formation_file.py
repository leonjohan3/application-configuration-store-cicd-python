#!/usr/bin/env python
# build_cloud_formation_file.py
"""
Builds an AWS Cloudformation file (based on the `root_folder`) that will be used to deploy the initial AppConfig resources
example root_folder:
├── README.md
├── retail
│ ├── prod
│ │   └── application.yaml
│ └── test
│     └── application.yaml
└── sales_api-ms
    ├── pre-prod_new
    │   └── application.yaml
    └── prod
        └── application.yaml

level one (retail and sales_api-ms) represent the applications, level two (prod, test and pre-prod_new) represent the environments
"""
__version__ = 0, 0, 1

import argparse
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from shared import acs
import json
# from snowflake.snowpark.session import Session
# import snowflake.snowpark.functions as F


def main(root_folder: str, template_folder: str) -> None:
    # account = 'svc123'
    #
    # if account.startswith('svc'):
    #     asc.use_svc()
    # else:
    #     acs.use_other()

    acs.validate_configuration_folder_structure(root_folder)
    file_path_list = list()
    acs.walk_file_tree(root_folder, acs.add_to_file_list, file_path_list)
    applications = acs.create_applications_list(len(Path(root_folder).parts), file_path_list)

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
    root_folder_head, root_folder_tail = os.path.split(args.root_folder)
    template_folder_head, template_folder_tail = os.path.split(args.template_folder)

    with open(args.filename, 'r') as f:
        data = json.load(f)
    # x = json.load()

    main(root_folder_head if not root_folder_tail else os.path.join(root_folder_head, root_folder_tail),
         template_folder_head if not template_folder_tail else os.path.join(template_folder_head, template_folder_tail))

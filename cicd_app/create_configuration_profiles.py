#!/usr/bin/env python
# create_configuration_profiles.py
import argparse
import re

import boto3

from shared import acs

__version__ = 0, 0, 1

client = boto3.client('appconfig')


def get_latest_configuration_version(configuration_profile):
    configuration_versions = client.list_hosted_configuration_versions(ApplicationId=configuration_profile['ApplicationId'],
                                                                       ConfigurationProfileId=configuration_profile['Id'])
    latest_configuration_version = None

    for configuration_version in configuration_versions['Items']:
        latest_configuration_version = configuration_version
        break

    return latest_configuration_version


def append_configuration_version(configuration_profile, application_name, current_configuration_version, new_content):
    response = client.create_hosted_configuration_version(ApplicationId=configuration_profile['ApplicationId'], ConfigurationProfileId=configuration_profile['Id'],
                                                          Description=f'Configuration that will be deployed to the `{application_name}` environment of the '
                                                                      + f"`{configuration_profile['Name']}` application",
                                                          Content=new_content, ContentType='text/plain')

    if response_has_error(response) or response['VersionNumber'] <= current_configuration_version:
        raise Exception(
            f"ERROR, something is wrong, unable to create new configuration version, the `{application_name}` application, the "
            + f" `{configuration_profile['Name']}` environment")

    print(f"successfully updated configuration profile `{configuration_profile['Name']}` environment of the `{application_name}` application on AWS AppConfig")


def response_has_error(response):
    return response['ResponseMetadata']['HTTPStatusCode'] >= 300


def get_content_from_file_path(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def get_new_content(latest_configuration_version, file_path):
    configuration_version = client.get_hosted_configuration_version(ApplicationId=latest_configuration_version['ApplicationId'],
                                                                    ConfigurationProfileId=latest_configuration_version['ConfigurationProfileId'],
                                                                    VersionNumber=latest_configuration_version['VersionNumber'])
    content_from_app_config = configuration_version['Content'].read().decode('utf-8')
    content_from_file = get_content_from_file_path(file_path)
    new_content = None

    if content_from_file != content_from_app_config:
        new_content = content_from_file

    return new_content


def remove_old_configuration_versions(configuration_profile, application_name):
    configuration_versions = client.list_hosted_configuration_versions(ApplicationId=configuration_profile['ApplicationId'],
                                                                       ConfigurationProfileId=configuration_profile['Id'])
    old_configuration_versions = list()
    counter = 0

    for configuration_version in configuration_versions['Items']:
        counter = counter + 1

        if counter > 2:
            old_configuration_versions.append(configuration_version)

    if len(old_configuration_versions) > 0:
        for old_configuration_version in old_configuration_versions:
            response = client.delete_hosted_configuration_version(ApplicationId=configuration_profile['ApplicationId'],
                                                                  ConfigurationProfileId=configuration_profile['Id'],
                                                                  VersionNumber=old_configuration_version['VersionNumber'])
            if response_has_error(response):
                raise Exception(
                    f"ERROR, something is wrong, unable to remove old configuration version, the `{application_name}` application, the "
                    + f" `{configuration_profile['Name']}` environment, version: {old_configuration_version['VersionNumber']}")


def process_configuration_profile(configuration_profile, application_name, file_path):
    latest_configuration_version = get_latest_configuration_version(configuration_profile)

    if latest_configuration_version is None:
        append_configuration_version(configuration_profile, application_name, 0, get_content_from_file_path(file_path))
    else:
        new_content = get_new_content(latest_configuration_version, file_path)

        if new_content is not None:
            append_configuration_version(configuration_profile, application_name, latest_configuration_version['VersionNumber'], new_content)

    remove_old_configuration_versions(configuration_profile, application_name)


def process_application(application, environments):
    configuration_profiles = client.list_configuration_profiles(ApplicationId=application['Id'])

    for configuration_profile in configuration_profiles['Items']:
        process_configuration_profile(configuration_profile, application['Description'], environments[configuration_profile['Name']])


def main(root_folder):
    acs.validate_configuration_folder_structure(root_folder)
    file_path_list = list()
    acs.walk_file_tree(root_folder, acs.add_to_file_list, file_path_list)
    applications_dict = acs.create_applications_dict(file_path_list)

    applications = client.list_applications()

    for application in applications['Items']:
        if re.match(r'^acs/', application['Name']) is not None:
            process_application(application, applications_dict[application['Description']])


if __name__ == '__main__':
    parser = argparse.ArgumentParser("create_configuration_profiles.py")
    parser.add_argument("root_folder", help="The root folder for the application configurations, e.g. application-configuration-store", type=str)
    args = parser.parse_args()

    main(args.root_folder)

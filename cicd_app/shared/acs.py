# acs.py
import os
import re
from pathlib import Path
from stat import S_ISDIR, S_ISREG


# the root folder may contain folders and files (e.g. a README.md file)
# all the 1st level folders (applications) should have one or more sub-folders (environments) - raise ex when empty or contain anything else than folders
# all the 2nd level folders (environments) should contain only a single configuration file - raise ex when empty or contain anything else
def validate_configuration_folder_structure(root_folder):
    application_folder_count = 0

    for f in os.listdir(root_folder):
        pathname = os.path.join(root_folder, f)
        mode = os.lstat(pathname).st_mode

        if S_ISDIR(mode):
            validate_application_folder(pathname)
            application_folder_count = application_folder_count + 1

    if application_folder_count < 1:
        raise Exception(f"ERROR, something is wrong, configuration folder `{root_folder}` does not have any applications defined")


def validate_application_folder(application_folder):
    environment_folder_count = 0

    for f in os.listdir(application_folder):
        pathname = os.path.join(application_folder, f)
        mode = os.lstat(pathname).st_mode

        if not S_ISDIR(mode):
            raise Exception(f"ERROR, something is wrong, application folder `{application_folder}` should only contain folders, one for each environment")

        configuration_file_count = validate_environment_folder(pathname)

        if configuration_file_count != 1:
            raise Exception(f"ERROR, something is wrong, environment folder `{pathname}` should contain a configuration file")

        environment_folder_count = environment_folder_count + 1

    if environment_folder_count < 1:
        raise Exception(f"ERROR, something is wrong, application folder `{application_folder}` does not have any environments defined, maybe delete this folder")


def validate_environment_folder(environment_folder):
    configuration_file_count = 0

    for f in os.listdir(environment_folder):
        pathname = os.path.join(environment_folder, f)
        mode = os.lstat(pathname).st_mode

        if not S_ISREG(mode) or configuration_file_count > 0:
            raise Exception(f"ERROR, something is wrong, environment folder `{environment_folder}` should contain only a single configuration file")

        configuration_file_count = configuration_file_count + 1

    return configuration_file_count


def walk_file_tree(root_folder, callback, file_list):
    for f in os.listdir(root_folder):
        pathname = os.path.join(root_folder, f)
        mode = os.lstat(pathname).st_mode

        if S_ISDIR(mode):
            # It's a directory, recurse into it
            walk_file_tree(pathname, callback, file_list)
        elif S_ISREG(mode):
            # It's a file, call the callback function
            callback(pathname, file_list)


def add_to_file_list(file, file_list):
    file_list.append(file)


def validate_application_or_environment_name(name):
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_\-]{1,59}$', name):
        raise Exception(f"ERROR, something is wrong, invalid name: `{name}`, only alphanumeric values with"
                        + " underscores and dashes are allowed, starting with an alphanumeric, and a maximum of 64 characters")


def parse_file_path_to_get_application_and_environment(file_path):
    file_path_parts = Path(file_path).parts
    # return application, environment
    return file_path_parts[-3], file_path_parts[-2]


def is_config_path(root_folder_part_count, file_path):
    return len(Path(file_path).parts) - root_folder_part_count == 3


def create_applications_list(root_folder_part_count, file_path_list):
    translation_table = dict.fromkeys(map(ord, '_-'), None)
    sorted_file_path = file_path_list
    sorted_file_path.sort()
    applications = list()
    current_application = None
    environments = None

    for file_path in sorted_file_path:

        if not is_config_path(root_folder_part_count, file_path):
            continue

        application, environment = parse_file_path_to_get_application_and_environment(file_path)
        validate_application_or_environment_name(application)
        validate_application_or_environment_name(environment)

        if current_application != application:

            if environments is not None:
                applications.append(dict(name=current_application, cf_name=current_application.translate(translation_table), environments=environments))

            current_application = application
            environments = list()

        environments.append(dict(name=environment, cf_name=environment.translate(translation_table), file_path=file_path))

    applications.append(dict(name=current_application, cf_name=current_application.translate(translation_table), environments=environments))
    return applications


def create_applications_dict(root_folder_part_count, file_path_list):
    sorted_file_path = file_path_list
    sorted_file_path.sort()
    applications = dict()
    current_application = None
    environments = None

    for file_path in sorted_file_path:

        if not is_config_path(root_folder_part_count, file_path):
            continue

        application, environment = parse_file_path_to_get_application_and_environment(file_path)
        validate_application_or_environment_name(application)
        validate_application_or_environment_name(environment)

        if current_application != application:

            if environments is not None:
                applications[current_application] = environments

            current_application = application
            environments = dict()

        environments[environment] = file_path

    applications[current_application] = environments
    return applications


def get_next_batch_of_applications(client, next_token):
    if next_token is None:
        applications = client.list_applications()
    else:
        applications = client.list_applications(NextToken=next_token)

    return applications

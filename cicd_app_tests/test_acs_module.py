# test_acs_module.py
import pytest

from cicd_app.shared import acs


@pytest.mark.parametrize("file_path, expected_application, expected_environment", [
    ('cicd_app_tests/provided_input/sales/test/application.yaml', 'sales', 'test'),
    ('root/cicd_app_tests/provided_input/sales_sales/test_test/application.yaml', 'sales_sales', 'test_test'),
    ('/project/root/cicd_app_tests/provided_input/sals/tst/application.yaml', 'sals', 'tst'),
    ('saless/ttest/application.yaml', 'saless', 'ttest'),
])
def test_parse_file_path(file_path, expected_application, expected_environment):
    application, environment = acs.parse_file_path(file_path)
    assert application == expected_application
    assert environment == expected_environment


@pytest.mark.parametrize("file_path_list, root_folder_count, expected_applications", [
    (['cicd_app_tests/provided_input/sales/test/application.yaml', 'cicd_app_tests/provided_input/sales/prod/application.yaml'], 1,
     [{'name': 'sales', 'cf_name': 'sales', 'environments': [
         {'name': 'prod', 'cf_name': 'prod', 'file_path': 'cicd_app_tests/provided_input/sales/prod/application.yaml'},
         {'name': 'test', 'cf_name': 'test', 'file_path': 'cicd_app_tests/provided_input/sales/test/application.yaml'},
     ]}]
     ),
    (['cicd_app_tests/sales/test/application.yaml'], 0,
     [{'name': 'sales', 'cf_name': 'sales', 'environments': [
         {'name': 'test', 'cf_name': 'test', 'file_path': 'cicd_app_tests/sales/test/application.yaml'},
     ]}]
     ),
    (['cicd_app_tests/sales_backend/pre-prod/application.yaml'], 0,
     [{'name': 'sales_backend', 'cf_name': 'salesbackend', 'environments': [
         {'name': 'pre-prod', 'cf_name': 'preprod', 'file_path': 'cicd_app_tests/sales_backend/pre-prod/application.yaml'},
     ]}]
     ),
    (['cicd_app_tests/provided_input/sales/test/application.yaml', 'cicd_app_tests/provided_input/retail/prod/application.yaml'], 1,
     [{'name': 'retail', 'cf_name': 'retail', 'environments': [
         {'name': 'prod', 'cf_name': 'prod', 'file_path': 'cicd_app_tests/provided_input/retail/prod/application.yaml'},
     ]},
      {'name': 'sales', 'cf_name': 'sales', 'environments': [
          {'name': 'test', 'cf_name': 'test', 'file_path': 'cicd_app_tests/provided_input/sales/test/application.yaml'},
      ]}
      ]
     ),
])
def test_create_applications_list(file_path_list, root_folder_count, expected_applications):
    applications = acs.create_applications_list(root_folder_count, file_path_list)
    assert applications == expected_applications


@pytest.mark.parametrize("file_path_list, root_folder_count, expected_applications", [
    (['cicd_app_tests/provided_input/sales/test/application.yaml', 'cicd_app_tests/provided_input/sales/prod/application.yaml',
      'cicd_app_tests/provided_input/application.yaml'], 1,
     {'sales': {'prod': 'cicd_app_tests/provided_input/sales/prod/application.yaml', 'test': 'cicd_app_tests/provided_input/sales/test/application.yaml'}}
     ),
    (['cicd_app_tests/sales/test/application.yaml'], 0,
     {'sales': {'test': 'cicd_app_tests/sales/test/application.yaml'}}
     ),
    (['cicd_app_tests/sales_backend/pre-prod/application.yaml'], 0,
     {'sales_backend': {'pre-prod': 'cicd_app_tests/sales_backend/pre-prod/application.yaml'}}
     ),
    (['cicd_app_tests/provided_input/sales/test/application.yaml', 'cicd_app_tests/provided_input/retail/prod/application.yaml'], 1,
     {'retail': {'prod': 'cicd_app_tests/provided_input/retail/prod/application.yaml'},
      'sales': {'test': 'cicd_app_tests/provided_input/sales/test/application.yaml'}}
     ),
])
def test_create_applications_dict(file_path_list, root_folder_count, expected_applications):
    applications = acs.create_applications_dict(root_folder_count, file_path_list)
    assert applications == expected_applications


@pytest.mark.parametrize("root_folder, expected_exception_message", [
    ('cicd_app_tests/invalid_config_folder_structures/without_any_applications',
     'configuration folder `cicd_app_tests/invalid_config_folder_structures/without_any_applications` does not have any applications defined'),
    ('cicd_app_tests/invalid_config_folder_structures/with_file_in_environments_folder',
     'application folder `cicd_app_tests/invalid_config_folder_structures/with_file_in_environments_folder/my_application` should only contain folders, '
     + 'one for each environment'),
    ('cicd_app_tests/invalid_config_folder_structures/without_any_environment_folders',
     'application folder `cicd_app_tests/invalid_config_folder_structures/without_any_environment_folders/my_application` does not have any environments '
     + 'defined, maybe delete this folder'),
    ('cicd_app_tests/invalid_config_folder_structures/with_folder_in_place_of_a_configuration_file',
     'environment folder `cicd_app_tests/invalid_config_folder_structures/with_folder_in_place_of_a_configuration_file/my_application/my_environment` should '
     + 'contain only a single configuration file'),
    ('cicd_app_tests/invalid_config_folder_structures/with_multiple_configuration_files',
     'environment folder `cicd_app_tests/invalid_config_folder_structures/with_multiple_configuration_files/my_application/my_environment` should contain '
     + 'only a single configuration file'),
    ('cicd_app_tests/invalid_config_folder_structures/without_a_configuration_file',
     'environment folder `cicd_app_tests/invalid_config_folder_structures/without_a_configuration_file/my_application/my_environment` should contain a '
     + 'configuration file'),
])
def test_validate_configuration_folder_structure_with_invalid_folder_structure(root_folder, expected_exception_message):
    with pytest.raises(Exception) as exc_info:
        # when : method to be checked invocation / act
        acs.validate_configuration_folder_structure(root_folder)

    # then : checks and assertions / assert
    assert str(exc_info.value) == f'ERROR, something is wrong, {expected_exception_message}'


def test_validate_configuration_folder_structure_with_valid_folder_structure():
    acs.validate_configuration_folder_structure('cicd_app_tests/provided_input')


@pytest.mark.parametrize("name, expected_exception_message", [
    ('1more-than-64-characters-56789-123456789-123456789-123456789_1234',
     'invalid name: `1more-than-64-characters-56789-123456789-123456789-123456789_1234`, only alphanumeric values with underscores and dashes are '
     + 'allowed, starting with an alphanumeric, and a maximum of 64 characters'),
    ('-starting-with-a-dash',
     'invalid name: `-starting-with-a-dash`, only alphanumeric values with underscores and dashes are '
     + 'allowed, starting with an alphanumeric, and a maximum of 64 characters'),
    ('_starting-with-an-underscore',
     'invalid name: `_starting-with-an-underscore`, only alphanumeric values with underscores and dashes are '
     + 'allowed, starting with an alphanumeric, and a maximum of 64 characters'),
    ('with_@_being-invalid',
     'invalid name: `with_@_being-invalid`, only alphanumeric values with underscores and dashes are '
     + 'allowed, starting with an alphanumeric, and a maximum of 64 characters'),
    ('with some spaces',
     'invalid name: `with some spaces`, only alphanumeric values with underscores and dashes are '
     + 'allowed, starting with an alphanumeric, and a maximum of 64 characters'),
])
def test_validate_application_or_environment_name(name, expected_exception_message):
    with pytest.raises(Exception) as exc_info:
        # when : method to be checked invocation / act
        acs.validate_application_or_environment_name(name)

    # then : checks and assertions / assert
    assert str(exc_info.value) == f'ERROR, something is wrong, {expected_exception_message}'


@pytest.mark.parametrize("file_path_list, root_folder_count, expected_exception_message", [
    (['cicd_app_tests/provided_input/sales/prod/application.yaml', 'cicd_app_tests/provided_input/sales_and_$s/test/application.yaml'], 1,
     'invalid name: `sales_and_$s`, only alphanumeric values with underscores and dashes are '
     + 'allowed, starting with an alphanumeric, and a maximum of 64 characters'),
    (['cicd_app_tests/provided_input/sales/test_with_a_#tag/application.yaml', 'cicd_app_tests/provided_input/sales/prod/application.yaml'], 1,
     'invalid name: `test_with_a_#tag`, only alphanumeric values with underscores and dashes are '
     + 'allowed, starting with an alphanumeric, and a maximum of 64 characters'),
])
def test_create_applications_list_with_invalid_name(file_path_list, root_folder_count, expected_exception_message):
    with pytest.raises(Exception) as exc_info:
        # when : method to be checked invocation / act
        acs.create_applications_list(root_folder_count, file_path_list)

    # then : checks and assertions / assert
    assert str(exc_info.value) == f'ERROR, something is wrong, {expected_exception_message}'


@pytest.mark.parametrize("file_path_list, root_folder_count, expected_exception_message", [
    (['cicd_app_tests/provided_input/sales_and=s/test/application.yaml', 'cicd_app_tests/provided_input/sales/prod/application.yaml'], 1,
     'invalid name: `sales_and=s`, only alphanumeric values with underscores and dashes are '
     + 'allowed, starting with an alphanumeric, and a maximum of 64 characters'),
    (['cicd_app_tests/provided_input/sales/prod/application.yaml', 'cicd_app_tests/provided_input/sales/test_with_a_*/application.yaml'], 1,
     'invalid name: `test_with_a_*`, only alphanumeric values with underscores and dashes are '
     + 'allowed, starting with an alphanumeric, and a maximum of 64 characters'),
])
def test_create_applications_dict_with_invalid_name(file_path_list, root_folder_count, expected_exception_message):
    with pytest.raises(Exception) as exc_info:
        # when : method to be checked invocation / act
        acs.create_applications_dict(root_folder_count, file_path_list)

    # then : checks and assertions / assert
    assert str(exc_info.value) == f'ERROR, something is wrong, {expected_exception_message}'

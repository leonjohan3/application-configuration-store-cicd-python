# test_cicd_app.py
import filecmp

from cicd_app import build_cloud_formation_file


def test_build_cloud_formation_file():
    # given: all data (test fixture) preparation / arrange
    cloud_formation_file = 'cloud_formation_master.yaml'

    # when : method to be checked invocation / act
    build_cloud_formation_file.main('cicd_app_tests/provided_input', 'build')
    # build_cloud_formation_file.main('../application-configuration-store')

    # then : checks and assertions / assert
    assert filecmp.cmp(f'cicd_app_tests/expected_output/{cloud_formation_file}', f'build/template.yaml', False)

# def test_create_configuration_profiles():
# given: all data (test fixture) preparation / arrange
# cloud_formation_file = 'cloud_formation_master.yaml'

# when : method to be checked invocation / act
# build_cloud_formation_file.main('cicd_app_tests/provided_input')
# create_configuration_profiles.main('cicd_app_tests/provided_input')
# create_configuration_profiles.main('../application-configuration-store')

# then : checks and assertions / assert
# assert filecmp.cmp(f'cicd_app_tests/expected_output/{cloud_formation_file}', f'build/{cloud_formation_file}', False)

#!/usr/bin/env python
# deploy_configuration_profiles.py
import re

import boto3

__version__ = 0, 0, 1

client = boto3.client('appconfig')


def get_deployment_strategy_id():
    deployment_strategies = client.list_deployment_strategies()
    deployment_strategy_of_interest = None

    for deployment_strategy in deployment_strategies['Items']:
        if re.match(r'^acs-', deployment_strategy['Name']) is not None:
            deployment_strategy_of_interest = deployment_strategy
            break

    if deployment_strategy_of_interest is None:
        raise Exception(f"ERROR, something is wrong, the acs deployment_strategy is missing")

    return deployment_strategy_of_interest['Id']


deployment_strategy_id = get_deployment_strategy_id()


def deploy_latest_configuration_version(configuration_version, application_name, environment):
    result = client.start_deployment(ApplicationId=configuration_version['ApplicationId'], EnvironmentId=environment['Id'],
                                     DeploymentStrategyId=deployment_strategy_id,
                                     ConfigurationProfileId=configuration_version['ConfigurationProfileId'],
                                     ConfigurationVersion=str(configuration_version['VersionNumber']))

    if result['State'] != 'COMPLETE':
        raise Exception(f"ERROR, failure deploying `{environment['Name']}` environment for the `{application_name}` application")

    print(f"successfully deployed `{environment['Name']}` environment of the `{application_name}` application to AWS AppConfig"
          + " - application likely requires a re-start to pickup the newly deployed configuration")


def process_configuration_version(configuration_version, application_name, environment):
    deployments = client.list_deployments(ApplicationId=configuration_version['ApplicationId'], EnvironmentId=environment['Id'])
    last_deployed_deployment = None

    for deployment in deployments['Items']:
        last_deployed_deployment = deployment
        break

    # check if latest configuration is deployed
    if last_deployed_deployment is None or configuration_version['VersionNumber'] > int(last_deployed_deployment['ConfigurationVersion']):
        deploy_latest_configuration_version(configuration_version, application_name, environment)


def process_configuration_profile(configuration_profile, application_name):
    environments = client.list_environments(ApplicationId=configuration_profile['ApplicationId'])
    environment = None

    for environment in environments['Items']:
        if environment['Name'] == configuration_profile['Name']:

            if environment['State'] != 'ReadyForDeployment':
                raise Exception(
                    f"ERROR, something is wrong, the `{environment['Name']}` environment from the `{application_name}` application is not ready for deployment")

            environment = environment
            break

    if environment is None:
        raise Exception(
            f"ERROR, something is wrong, configuration_profile `{configuration_profile['Name']}` for application `{application_name}`" +
            " does not have a corresponding environment")

    configuration_versions = client.list_hosted_configuration_versions(ApplicationId=configuration_profile['ApplicationId'],
                                                                       ConfigurationProfileId=configuration_profile['Id'])

    for configuration_version in configuration_versions['Items']:
        process_configuration_version(configuration_version, application_name, environment)


def parse_application_name(application_name):
    return re.split('/', application_name)[1]


def process_application(application):
    configuration_profiles = client.list_configuration_profiles(ApplicationId=application['Id'])

    for configuration_profile in configuration_profiles['Items']:
        process_configuration_profile(configuration_profile, parse_application_name(application['Name']))


def main():
    applications = client.list_applications()

    for application in applications['Items']:
        if re.match(r'^acs/', application['Name']) is not None:
            process_application(application)


if __name__ == '__main__':
    main()

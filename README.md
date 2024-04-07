# Overview
This Git repo contains the CI/CD scripts to deploy changes that are made to the `application configuration store` Git repo, to AWS AppConfig.
Also see the README.md in the `application configuration store` Git repo.

# Required dependencies
- Python
- AWS cli
- SAM

# Resources
- [AWS AppConfig](<https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html>)
- [AWS AppConfig configuration store quotas and limitations](<https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-free-form-configurations-creating.html#appconfig-creating-configuration-and-profile-quotas>)
- [](<>)
- [](<https://docs.python.org/3/library/venv.html>)
- [](<https://realpython.com/primer-on-jinja-templating/>)
- [](<https://realpython.com/pytest-python-testing/>)
- [](<https://github.com/github/gitignore>)
- [](<https://choosealicense.com>)
- [](<https://dbader.org/blog/write-a-great-readme-for-your-github-project>)
- [](<>)
- [](<>)
- [](<>)
- [](<>)

# Notes
- python -m venv .venv --clear --prompt venv --upgrade-deps
- source .venv/bin/activate
- pip freeze -r requirements.txt > requirements-frozen.txt
- pip install -r requirements.txt
- pip install -r tests/requirements.txt
- python -m pytest tests -v
- python -m tabnanny -v cicd_app*

# Todo
- freeze
- pylint
- pytest-cov
- add license
- look at using git submodules
- look at mypy
- figure out what characters are allowed for application and environment names and implement validation '^[a-zA-Z0-9][a-zA-Z0-9_\-]{1,63}$' [done]
- do a perf test with 250 folders with 3 environments each and include max app and env name lengths (to make sure we do not exceed e.g. description lengths that
  uses folder names)
- decide what to parameterize using env variables, e.g. tags, region, etc.
- write integration tests:
  - CFormation deploy, create configuration profiles and deploy configuration profiles, use AWS cli to get config from AppConfig and then compare with files 
  - update 2 config files, add a new project, delete an old project, add a new environment, delete an old environment, and do above

# Other

  Deployment{{ application.name|capitalize }}{{ environment.name|capitalize }}:
    Type: AWS::AppConfig::Deployment
    Properties:
      ApplicationId: !Ref Application{{ application.name|capitalize }}
      ConfigurationProfileId: !Ref ConfigurationProfile{{ application.name|capitalize }}
      ConfigurationVersion: 1
      DeploymentStrategyId: !Ref DeploymentStrategy
      EnvironmentId: !Ref Environment{{ application.name|capitalize }}{{ environment.name|capitalize }}


  ConfigurationVersion{{ application.name|capitalize }}{{ environment.name|capitalize }}:
    Type: AWS::AppConfig::HostedConfigurationVersion
    Properties:
      ApplicationId: !Ref Application{{ application.name|capitalize }}
      ConfigurationProfileId: !Ref ConfigurationProfile{{ application.name|capitalize }}{{ environment.name|capitalize }}
      Content: '{{ environment.file_path }}'
      ContentType: text/plain
      Description: Configuration that will be deployed to the `{{ environment.name }}` environment of the `{{ application.name }}` application

def is_valid_config_path(file_path):
    return len(re.findall(r'/', file_path))  > 2

# Algorithm
- create CFormation file(s) from data from the application configuration store Git repo
- run script to create configuration profiles from the application configuration store Git repo
- run script to deploy configuration profiles from the artifacts that had been created in AppConfig

# CI/CD buildscript
- checkout from GitHub application-configuration-store-cicd repo
- cd to folder application-configuration-store-cicd
- create python venv: python -m venv .venv --clear --prompt venv --upgrade-deps
- activate: source .venv/bin/activate
- install test dependencies: pip install -r cicd_app_tests/requirements.txt
- create build folder, and
- mkdir -p cicd_app_tests/invalid_config_folder_structures/with_folder_in_place_of_a_configuration_file/my_application/my_environment/misplaced_folder/
- mkdir -p cicd_app_tests/invalid_config_folder_structures/without_a_configuration_file/my_application/my_environment/
- mkdir -p cicd_app_tests/invalid_config_folder_structures/without_any_environment_folders/my_application/
- run tests: python -m pytest cicd_app_tests
- install app dependencies: pip install -r cicd_app/requirements.txt
- create CFormation file, template.yaml in sam folder, run: cicd_app/build_cloud_formation_file.py ../application-configuration-store sam
- cd sam folder, run make
- cd back
- run: cicd_app/create_configuration_profiles.py ../application-configuration-store
- run: cicd_app/deploy_configuration_profiles.py 

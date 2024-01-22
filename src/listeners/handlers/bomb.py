from subprocess import Popen, PIPE, STDOUT
import boto3
import os

def handler(respond, body):
  sts = boto3.client('sts')

  STACK_NAME = os.getenv('STACK_NAME')
  OAUTH_STATE_S3_BUCKET_NAME = os.getenv('OAUTH_STATE_S3_BUCKET_NAME')
  INSTALLATION_S3_BUCKET_NAME = os.getenv('INSTALLATION_S3_BUCKET_NAME')
  SLACK_APP_FUNCTION_NAME = f'{STACK_NAME}-AwsBombSlackAppFunction-'
  SLACK_APP_FUNCTION_ROLE_NAME = 'AwsBombSlackAppFunctionRole'

  region = body['text']
  
  if not (region is None or len(region) == 0):
    aws_account_id = sts.get_caller_identity().get("Account")

    config_file = 'regions:\n'
    config_file += f'- \"{region}\"\n'
    config_file += 'account-blocklist:\n'
    config_file += '- \"999999999999\"\n'
    config_file += 'resource-types:\n'
    config_file += '  excludes:\n'
    config_file += '  - OSPackage\n'
    config_file += 'accounts:\n'
    config_file += f'  \"{aws_account_id}\":\n'
    config_file += '    filters:\n'
    config_file += '      IAMRole:\n'
    config_file += '      - type: contains\n'
    config_file += f'        value: {SLACK_APP_FUNCTION_ROLE_NAME}\n'
    config_file += '      CloudFormationStack:\n'
    config_file += '      - type: contains\n'
    config_file += f'        value: {STACK_NAME}\n'
    config_file += '      - aws-sam-cli-managed-default\n'
    config_file += '      LambdaFunction:\n'
    config_file += '      - type: contains\n'
    config_file += f'        value: {SLACK_APP_FUNCTION_NAME}\n'
    config_file += '      APIGatewayRestAPI:\n'
    config_file += '      - property: Name\n'
    config_file += f'        value: {STACK_NAME}\n'
    config_file += '      S3Bucket:\n'
    config_file += f'      - s3://{OAUTH_STATE_S3_BUCKET_NAME}\n'
    config_file += f'      - s3://{INSTALLATION_S3_BUCKET_NAME}\n'
    config_file += '      - type: regex\n'
    config_file += '        value: s3://aws-sam-cli-managed-default-samclisourcebucket-.*\n'
    config_file += '      S3Object:\n'
    config_file += '      - type: regex\n'
    config_file += f'        value: s3://{OAUTH_STATE_S3_BUCKET_NAME}/.*\n'
    config_file += '      - type: regex\n'
    config_file += f'        value: s3://{INSTALLATION_S3_BUCKET_NAME}/.*\n'
    config_file += '      - type: regex\n'
    config_file += '        value: s3://aws-sam-cli-managed-default-samclisourcebucket-.*\n'
    config_file += '      ECRRepository:\n'
    config_file += '      - type: contains\n'
    config_file += f'        value: /awsbombslackappfunction'

    write_config_file = Popen(f'echo -e "{config_file}" > /tmp/config.yaml', stdout=PIPE, stderr=STDOUT, shell=True, text=True).stdout.read()
    print(write_config_file)
    read_config_file = Popen(f'cat /tmp/config.yaml', stdout=PIPE, stderr=STDOUT, shell=True, text=True).stdout.read()
    print(read_config_file)

    execute_aws_nuke = Popen('/opt/aws-nuke --config /tmp/config.yaml --force --force-sleep 3 --no-dry-run', stdout=PIPE, stderr=STDOUT, shell=True, text=True).stdout.read()

    iteration = len(execute_aws_nuke) // 10000
    for i in range(iteration+1):
      if i == iteration:
        respond(f'```{execute_aws_nuke[10000*i:]}```')
      else:
        respond(f'```{execute_aws_nuke[10000*i:10000*(i+1)]}```')
from subprocess import Popen, PIPE, STDOUT
import boto3

def handler(respond, body):
  sts = boto3.client('sts')

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
    config_file += f'  \"{aws_account_id}\"'
    config_file += ': {}'

    write_config_file = Popen(f'echo -e "{config_file}" > /tmp/config.yaml', stdout=PIPE, stderr=STDOUT, shell=True, text=True).stdout.read()
    print(write_config_file)
    read_config_file = Popen(f'cat /tmp/config.yaml', stdout=PIPE, stderr=STDOUT, shell=True, text=True).stdout.read()
    print(read_config_file)

    execute_aws_nuke = Popen('/opt/aws-nuke --config /tmp/config.yaml --force --force-sleep 3 --no-dry-run', stdout=PIPE, stderr=STDOUT, shell=True, text=True).stdout.read()

    iteration = len(execute_aws_nuke) // 100000
    for i in range(iteration+1):
      if i == iteration:
        respond(f'```{execute_aws_nuke[100000*i:]}```')
      else:
        respond(f'```{execute_aws_nuke[100000*i:100000*(i+1)]}```')
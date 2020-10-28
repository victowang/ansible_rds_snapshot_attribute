DOCUMENTATION = '''
---
module: rds_snapshot_attributes
version_added: "2.8"
short_description: Manage RDS snapshot attributes
description:
    - Read, add and delete RDS snapshot attributes.

requirements:
    - botocore
    - boto3 >= 2.49.0
'''

EXAMPLES = '''
- name: Get snapshot attributes
  rds_snapshot_attributes:
    db_snapshot_identifier: "{{snapshot_identifier}}"

- name: Modify snapshot attributes
  rds_snapshot_attributes:
    db_snapshot_identifier: "{{snapshot_identifier}}"
    attribute_name: "restore"
    values_to_add:
      - 123456789012
    values_to_remove:
      - 987654321012
'''

RETURN = '''
{
    "DBSnapshotAttributes": [
        {
            "AttributeName": "restore",
            "AttributeValues": ["123456789012"]
        }
    ],
    "DBSnapshotIdentifier": "snapshot_name",
    "changed": true,
    "failed": false
}
'''

from ansible.module_utils.aws.core import AnsibleAWSModule


def is_describe(module):
    if module.params.get('attribute_name') \
            or module.params.get('values_to_add') \
            or module.params.get('values_to_remove'):
        return False
    return True


def describe_attributes(client, module):
    snapshot_name = module.params.get('db_snapshot_identifier')
    response = client.describe_db_snapshot_attributes(
        DBSnapshotIdentifier=snapshot_name
    )
    return response["DBSnapshotAttributesResult"]

def reformat_arg(values):
    ret = values.replace('[', "").replace(']', "").replace('"', "").replace("'", "").split(", ")
    return ret

def modify_attribute(client, module):
    changed = False
    snapshot_name = module.params.get('db_snapshot_identifier')
    attribute_name = module.params.get('attribute_name')
    values_to_add = module.params.get('values_to_add')
    values_to_remove = module.params.get('values_to_remove')
    res = describe_attributes(client, module)
    args = {
        'DBSnapshotIdentifier': snapshot_name,
        'AttributeName': attribute_name,
    }
    if values_to_add:
        args['ValuesToAdd'] = reformat_arg(values_to_add)
    if values_to_remove:
        args['ValuesToRemove'] = reformat_arg(values_to_remove)
    response = client.modify_db_snapshot_attribute(**args)
    if res != describe_attributes(client, module):
        changed = True
    return changed, response['DBSnapshotAttributesResult']


def main():
    argument_spec = dict(
        db_snapshot_identifier=dict(aliases=['snapshot_name']),
        attribute_name=dict(),
        values_to_add=dict(),
        values_to_remove=dict(),
    )
    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['db_snapshot_identifier']]
    )
    changed = False
    client = module.client('rds')
    if is_describe(module):
        results = describe_attributes(client, module)
    else:
        changed, results = modify_attribute(client, module)
    module.exit_json(changed=changed, **results)


if __name__ == '__main__':
    main()


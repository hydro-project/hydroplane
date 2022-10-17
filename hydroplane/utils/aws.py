from uuid import uuid4

import boto3

from ..models.aws import AWSCredentials
from ..secret_stores.secret_store import SecretStore


def boto3_client_from_creds(
        service_name: str,
        region: str,
        credentials: AWSCredentials,
        secret_store: SecretStore
):
    creds = credentials

    # By default, we'll use the access key and secret access key to authenticate
    access_key = secret_store.get_secret(creds.access_key.access_key_id)
    secret_key = secret_store.get_secret(creds.access_key.secret_access_key)
    session_token = None

    if creds.assume_role is not None:
        # If we should be assuming a role instead, use those base creds to assume that role
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

        assume_role_response = sts_client.assume_role(
            RoleArn=creds.assume_role.role_arn,
            ExternalId=creds.assume_role.external_id,
            RoleSessionName=creds.assume_role.session_name or f'hydroplane-launch-{uuid4()}',
            DurationSeconds=creds.assume_role.session_duration_seconds
        )

        access_key = assume_role_response['Credentials']['AccessKeyId']
        secret_key = assume_role_response['Credentials']['SecretAccessKey']
        session_token = assume_role_response['Credentials']['SessionToken']

    # Now that we have credentials, create and return the client
    return boto3.client(
        service_name,
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token
    )

from datetime import datetime
from time import time
from uuid import uuid4

import boto3
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session
import pytz

from ..models.aws import AWSCredentials
from ..secret_stores.secret_store import SecretStore

# If we don't get temporary credentials with a timeout, assume creds expire every 15 minutes
DEFAULT_SESSION_TTL_SECONDS = 900


def boto3_session_from_creds(
        credentials: AWSCredentials,
        secret_store: SecretStore
) -> boto3.Session:
    def get_session_credentials():
        creds = credentials

        # By default, we'll use the access key and secret access key to authenticate
        access_key = secret_store.get_secret(creds.access_key.access_key_id)
        secret_key = secret_store.get_secret(creds.access_key.secret_access_key)
        session_token = None
        expiry_time = pytz.utc.localize(
            datetime.utcfromtimestamp(time() + DEFAULT_SESSION_TTL_SECONDS)
        ).isoformat()

        if creds.assume_role is not None:
            # If we should be assuming a role instead, use those base creds to assume that role
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )

            assume_role_params = {
                'RoleArn': creds.assume_role.role_arn,
                'RoleSessionName': creds.assume_role.session_name or f'hydroplane-launch-{uuid4()}',
                'DurationSeconds': creds.assume_role.session_duration_seconds
            }

            if creds.assume_role.external_id is not None:
                assume_role_params['ExternalId'] = creds.assume_role.external_id

            assume_role_response = sts_client.assume_role(**assume_role_params)

            access_key = assume_role_response['Credentials']['AccessKeyId']
            secret_key = assume_role_response['Credentials']['SecretAccessKey']
            session_token = assume_role_response['Credentials']['SessionToken']
            expiry_time = assume_role_response['Credentials']['Expiration'].isoformat()

        return {
            'access_key': access_key,
            'secret_key': secret_key,
            'token': session_token,
            'expiry_time': expiry_time
        }

    refreshable_credentials = RefreshableCredentials.create_from_metadata(
        metadata=get_session_credentials(),
        refresh_using=get_session_credentials,
        method='sts-assume-role'
    )

    session = get_session()
    session._credentials = refreshable_credentials

    autorefresh_session = boto3.Session(botocore_session=session)

    return autorefresh_session

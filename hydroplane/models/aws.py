from typing import Optional

from pydantic import BaseModel, Field, conint

from .secret import HydroplaneSecret


class AWSAccessKey(BaseModel):
    """
    An AWS access key/secret key pair, used to authenticate with AWS.
    """
    access_key_id: HydroplaneSecret
    secret_access_key: HydroplaneSecret


class AWSAssumeRole(BaseModel):
    """
    Information necessary for an AWS principal to temporarily assume a role (with associated
    temporary credentials).
    """
    role_arn: str = Field(description='the fully-qualified ARN of the role to assume')

    external_id: Optional[HydroplaneSecret] = Field(
        description='if needed, the external ID used to validate access to the role')

    session_name: Optional[str] = Field(
        None,
        description='the name of the temporary session created by the role assumption'
    )

    session_duration_seconds: Optional[conint(ge=15 * 60, le=12 * 60 * 60)] = Field(
        15 * 60,
        description='the duration of the temporary session, in seconds'
    )


class AWSCredentials(BaseModel):
    """
    Credentials used to authenticate with AWS.
    """

    access_key: AWSAccessKey
    assume_role: Optional[AWSAssumeRole] = Field(
        None,
        description='the role that Hydroplane will assume when communicating with AWS'
    )

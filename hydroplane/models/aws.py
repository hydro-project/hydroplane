from typing import Optional

from pydantic import BaseModel, Field, conint

from .secret import SecretValue


class AWSAccessKey(BaseModel):
    """An AWS access key/secret key pair, used to authenticate with AWS
    """
    access_key_id: SecretValue
    secret_access_key: SecretValue


class AWSAssumeRole(BaseModel):
    """Information necessary for an AWS principal to assume a role (with associated temporary
    credentials)"""
    role_arn: str
    external_id: SecretValue
    session_name: Optional[str] = Field(None)
    session_duration_seconds: Optional[conint(ge=15 * 60, le=12 * 60 * 60)] = Field(15 * 60)


class AWSCredentials(BaseModel):
    access_key: AWSAccessKey
    assume_role: Optional[AWSAssumeRole] = Field(
        None,
        description='the role that Hydroplane will assume when communicating with AWS'
    )

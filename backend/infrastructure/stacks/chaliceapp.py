import os

from aws_cdk import (
    aws_dynamodb as dynamodb,
    core as cdk,
    aws_cognito as cognito,
    aws_secretsmanager as secrets,
)
from chalice.cdk import Chalice


RUNTIME_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), os.pardir, "runtime"
)


class ChaliceApp(cdk.Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.profile_table = self._create_profile_table_with_inverted()
        self.user_pool = self._create_cognito_user_pool()
        self.spotify_client_secret = secrets.Secret.from_secret_arn(
            self,
            "SpotifyClientSecret",
            "arn:aws:secretsmanager:ap-southeast-2:837315506606:secret:SpotifyMusicMateClientSecret-eFGs9E",
        )
        self.chalice = Chalice(
            self,
            "ChaliceApp",
            source_dir=RUNTIME_SOURCE_DIR,
            stage_config={
                "environment_variables": {
                    "APP_TABLE_NAME": self.profile_table.table_name,
                    "USER_POOL_ARN": self.user_pool.user_pool_arn,
                    "SPOTIFY_CLIENT_ID": "bebb2a733b624a089d75b4a3d2240112",
                }
            },
        )
        self.spotify_client_secret.grant_read(self.chalice.get_role("DefaultRole"))
        self.profile_table.grant_read_write_data(self.chalice.get_role("DefaultRole"))

    def _create_profile_table_with_inverted(self):
        profile_table = dynamodb.Table(
            self,
            "ProfileTable",
            partition_key=dynamodb.Attribute(
                name="PK", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        profile_table.add_global_secondary_index(
            index_name="inverted-index",
            partition_key=dynamodb.Attribute(
                name="SK", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
        )
        cdk.CfnOutput(self, "ProfileTableName", value=profile_table.table_name)
        return profile_table

    def _create_cognito_user_pool(self):
        userpool = cognito.UserPool(
            self,
            "AppUserPool",
            self_sign_up_enabled=True,
            user_verification={
                "email_subject": "Verify your email for our awesome app!",
                "email_body": "Thanks for signing up to our awesome app! Your verification code is {####}",
                "email_style": cognito.VerificationEmailStyle.CODE,
                "sms_message": "Thanks for signing up to our awesome app! Your verification code is {####}",
            },
            sign_in_aliases={"phone": True},
        )
        cdk.CfnOutput(self, "UserPoolID", value=userpool.user_pool_id)
        cdk.CfnOutput(self, "UserPoolARN", value=userpool.user_pool_arn)

        client = userpool.add_client(
            "CognitoClient", auth_flows={"user_password": True, "user_srp": True}
        )
        cdk.CfnOutput(self, "CognitoClientID", value=client.user_pool_client_id)

        return userpool

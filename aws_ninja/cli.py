import botocore
import click

from aws_ninja.commands.recommendations import recommend
from aws_ninja.utils.aws import get_session_for_profile


@click.group()
@click.option("--profile", type=str, required=False, help="AWS Profile")
@click.option("--region", type=str, required=False, default="eu-west-2")
@click.pass_context
def aws_ninja(ctx, profile, region):
    """AWS Ninja

    Collection of command line tools for working with AWS.
    """
    ctx.ensure_object(dict)
    ctx.obj['AWS_PROFILE'] = profile
    ctx.obj['AWS_REGION'] = region
    ctx.obj['AWS_DEFAULT_REGION'] = region
    try:
        ctx.obj['AWS_SESSION'] = get_session_for_profile(profile, region)
        ctx.obj['AWS_SESSION_GLOBAL'] = get_session_for_profile(profile, 'us-east-1')
    except botocore.exceptions.UnauthorizedSSOTokenError:
        click.secho(
            f"Cannot authenticate to AWS using the profile {profile}, "
            f"have you logged in? (try aws sso login --profile {profile})",
            fg="red",
        )
        exit(1)


aws_ninja.add_command(recommend)

if __name__ == '__main__':
    aws_ninja()

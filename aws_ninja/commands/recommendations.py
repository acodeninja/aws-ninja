import click
import jsonpickle
import os

from datetime import datetime
from jinja2 import Environment
from jinja2 import FileSystemLoader
from pathlib import Path

from aws_ninja.utils.aws import EnumHandler
from aws_ninja.utils.aws import compute_optimizer
from aws_ninja.utils.aws import recommendation_finding_to_human
from aws_ninja.utils.aws.compute_optimizer import RecommendationCategory
from aws_ninja.utils.aws.compute_optimizer import RecommendationFinding
from aws_ninja.utils.aws.compute_optimizer import RecommendationResourceType
from aws_ninja.utils.aws.compute_optimizer.ecs import get_ecs_recommendations
from aws_ninja.utils.aws.compute_optimizer.rds import get_rds_recommendations
from aws_ninja.utils.aws.trusted_advisor import TrustedAdvisorPillar
from aws_ninja.utils.aws.trusted_advisor import get_trusted_advisor_recommendations


@click.command("recommend")
@click.pass_context
@click.option("--format",
              default="html",
              help="Output format",
              type=click.Choice(["html", "json"]))
def recommend(ctx, format):
    """Generate a recommendation report

    The recommendation report will show recommendations from Compute Optimiser
    and Trusted Advisor.
    """
    if not compute_optimizer.is_enrolled(ctx.obj["AWS_SESSION"]):
        click.secho(f"[Optimise] The targeted account ({ctx.obj['AWS_PROFILE']}) is not enrolled",
                    fg="red")
        exit(1)

    click.secho("[Optimise][ECS] Fetching recommendations", fg="blue")
    recommendations_ecs = get_ecs_recommendations(ctx.obj["AWS_SESSION"])
    non_optimal_ecs = [
        r for r in get_ecs_recommendations(ctx.obj["AWS_SESSION"])
        if r.recommendation.finding != RecommendationFinding.OPTIMIZED
    ]
    recommendations_ecs.sort(key=lambda x: x.recommendation.finding.value, reverse=True)
    click.secho(f"[Optimise][ECS] Found {len(non_optimal_ecs)} recommendation(s)",
                fg="green")

    click.secho("[Optimise][RDS] Fetching recommendations", fg="blue")
    recommendations_rds = get_rds_recommendations(ctx.obj["AWS_SESSION"])
    non_optimal_rds = [
        r for r in get_rds_recommendations(ctx.obj["AWS_SESSION"])
        if r.storage_finding != RecommendationFinding.OPTIMIZED
           or r.instance_finding != RecommendationFinding.OPTIMIZED
    ]
    recommendations_rds.sort(key=lambda x: x.storage_finding.value, reverse=True)
    recommendations_rds.sort(key=lambda x: x.instance_finding.value, reverse=True)
    click.secho(f"[Optimise][RDS] Found {len(non_optimal_rds)} recommendation(s)",
                fg="green")

    click.secho("[Optimise][TrustedAdvisor] Fetching recommendations", fg="blue")
    recommendations_trusted_advisor = get_trusted_advisor_recommendations(
        ctx.obj["AWS_SESSION_GLOBAL"],
        ['error'],
    )
    click.secho(
        f"[Optimise][TrustedAdvisor] Found {len(recommendations_trusted_advisor)} recommendation(s)",
        fg="green")

    click.secho("[Optimise][Report] Writing recommendation report", fg="blue")

    report_file = Path(f"recommendations-{ctx.obj["AWS_PROFILE"]}.{format}")

    if format == "json":
        jsonpickle.handlers.registry.register(RecommendationFinding, EnumHandler)
        jsonpickle.handlers.registry.register(RecommendationResourceType, EnumHandler)
        jsonpickle.handlers.registry.register(RecommendationCategory, EnumHandler)
        jsonpickle.handlers.registry.register(TrustedAdvisorPillar, EnumHandler)

        report_file.write_text(jsonpickle.encode({
            'ecs': recommendations_ecs,
            'rds': recommendations_rds,
            'trusted_advisor': recommendations_trusted_advisor,
        }, indent=4, make_refs=False, unpicklable=False))

    if format == "html":
        act_on_ecs = Path(os.getcwd(), 'acting_on_ecs.html')
        act_on_rds = Path(os.getcwd(), 'acting_on_rds.html')

        environment = Environment(loader=FileSystemLoader("aws_ninja/templates/"))
        environment.filters['to_human'] = recommendation_finding_to_human
        template = environment.get_template("recommendations/recommendations.html.jinja")

        output = template.render(
            date=datetime.now().strftime("%Y-%m-%d"),
            user=os.getenv("USER"),
            profile=ctx.obj["AWS_PROFILE"],
            recommendations_ecs=recommendations_ecs,
            recommendations_rds=recommendations_rds,
            recommendations_trusted_advisor=recommendations_trusted_advisor,
            act_on_ecs=act_on_ecs.read_text() if act_on_ecs.exists() else None,
            act_on_rds=act_on_rds.read_text() if act_on_rds.exists() else None,
        )

        report_file.write_text(output)

    click.secho(
        "[Optimise][Report] Wrote recommendation report to {}".format(report_file.absolute()),
        fg="green",
    )

# aws-ninja

A collection of tools to use when reviewing AWS accounts and their setup.

Install with `pip install aws-ninja`.

## aws-ninja recommend

Generate a recommendation report using the following sources:

- AWS Compute Optimiser: ECS, RDS
- AWS Trusted Advisor

### Usage

```shell
aws-ninja --profile <aws profile> recommend --format <html|json>
```

If you wish to include additional information on how to act on the recommendations run the command
in a directory with the following files:

- `acting_on_ecs.html`
- `acting_on_rds.html`

These HTML files will be embedded into the body of the report when it is generated.

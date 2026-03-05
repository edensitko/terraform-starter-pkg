"""CLI entry point for tf-starter."""

from __future__ import annotations

import argparse
import sys

import questionary
from questionary import Style

from tf_starter.generator import ProjectGenerator

SUPPORTED_PROVIDERS = ["aws", "gcp", "azure"]

# ---------------------------------------------------------------------------
# AWS service categories — each maps to sub-modules inside a category folder.
# "networking" and "security" are always included.
# ---------------------------------------------------------------------------

AWS_SERVICE_CATEGORIES = {
    "compute": {
        "label": "Compute     (EC2, ALB, Auto Scaling)",
    },
    "lambda": {
        "label": "Lambda      (Serverless Functions)",
    },
    "apigateway": {
        "label": "API Gateway (REST API + Lambda Integration)",
    },
    "database": {
        "label": "Database    (RDS PostgreSQL)",
    },
    "kubernetes": {
        "label": "Kubernetes  (EKS)",
    },
    "monitoring": {
        "label": "Monitoring  (CloudWatch, SNS)",
    },
    "messaging": {
        "label": "Messaging   (SQS)",
    },
    "storage": {
        "label": "Storage     (S3)",
    },
}

DEFAULT_REGIONS = {
    "aws": [
        "us-east-1",
        "us-east-2",
        "us-west-1",
        "us-west-2",
        "eu-west-1",
        "eu-west-2",
        "eu-central-1",
        "ap-southeast-1",
        "ap-northeast-1",
    ],
    "gcp": [
        "us-central1",
        "us-east1",
        "us-west1",
        "europe-west1",
        "europe-west3",
        "asia-east1",
        "asia-southeast1",
    ],
    "azure": [
        "eastus",
        "eastus2",
        "westus",
        "westus2",
        "westeurope",
        "northeurope",
        "southeastasia",
        "japaneast",
    ],
}

CUSTOM_STYLE = Style(
    [
        ("qmark", "fg:#00d7ff bold"),
        ("question", "fg:#ffffff bold"),
        ("answer", "fg:#00ff87 bold"),
        ("pointer", "fg:#00d7ff bold"),
        ("highlighted", "fg:#00d7ff bold"),
        ("selected", "fg:#00ff87"),
        ("separator", "fg:#6c6c6c"),
        ("instruction", "fg:#6c6c6c"),
    ]
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="tf-starter",
        description="Enterprise-grade Terraform Infrastructure-as-Code project generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tf-starter --provider aws --project-name myapp
  tf-starter --provider gcp --project-name my-gcp-infra
  tf-starter --provider azure --project-name azure-platform
        """,
    )

    parser.add_argument(
        "--provider",
        type=str,
        required=True,
        choices=SUPPORTED_PROVIDERS,
        help="Cloud provider (aws, gcp, azure)",
    )

    parser.add_argument(
        "--project-name",
        type=str,
        required=True,
        help="Name of the project to generate",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Output directory (default: current directory)",
    )

    return parser.parse_args()


def validate_project_name(name: str) -> bool:
    """Validate project name contains only safe characters."""
    import re

    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name))


def ask_environments() -> list[str]:
    """Interactively ask which environments to create."""
    env_choices = [
        questionary.Choice("dev", checked=True),
        questionary.Choice("staging"),
        questionary.Choice("prod"),
        questionary.Choice("custom"),
    ]

    selected = questionary.checkbox(
        "Select environments to create:",
        choices=env_choices,
        style=CUSTOM_STYLE,
        validate=lambda x: len(x) > 0 or "You must select at least one environment",
    ).ask()

    if selected is None:
        print("\nAborted.")
        sys.exit(1)

    environments = []
    for env in selected:
        if env == "custom":
            custom_name = questionary.text(
                "Enter custom environment name:",
                style=CUSTOM_STYLE,
                validate=lambda x: (
                    len(x) > 0 and x.isalnum() or "Must be alphanumeric"
                ),
            ).ask()
            if custom_name is None:
                print("\nAborted.")
                sys.exit(1)
            environments.append(custom_name.lower())
        else:
            environments.append(env)

    return environments


def ask_services(provider: str) -> list[str]:
    """Interactively ask which service categories to enable.

    For AWS the user picks from real AWS service groups.
    networking + security are always included automatically.
    """
    if provider == "aws":
        print("\n  ℹ  Network (VPC, Subnets, IGW, NAT) — always included\n")

        service_choices = [
            questionary.Choice(
                title=meta["label"],
                value=key,
                checked=(key == "compute"),
            )
            for key, meta in AWS_SERVICE_CATEGORIES.items()
        ]
    elif provider == "gcp":
        service_choices = [
            questionary.Choice("compute", checked=True),
            questionary.Choice("cloud_functions"),
            questionary.Choice("apigateway"),
            questionary.Choice("database"),
            questionary.Choice("kubernetes"),
            questionary.Choice("monitoring"),
            questionary.Choice("messaging"),
            questionary.Choice("storage"),
        ]
    else:
        # Azure
        service_choices = [
            questionary.Choice("compute", checked=True),
            questionary.Choice("functions"),
            questionary.Choice("apigateway"),
            questionary.Choice("database"),
            questionary.Choice("kubernetes"),
            questionary.Choice("monitoring"),
            questionary.Choice("messaging"),
            questionary.Choice("storage"),
        ]

    selected = questionary.checkbox(
        "Select service categories to enable:",
        choices=service_choices,
        style=CUSTOM_STYLE,
        validate=lambda x: len(x) > 0 or "You must select at least one service",
    ).ask()

    if selected is None:
        print("\nAborted.")
        sys.exit(1)

    # Enforce dependency: kubernetes (EKS) requires compute
    if "kubernetes" in selected and "compute" not in selected:
        print("  ℹ  Kubernetes requires compute — auto-enabling compute (EC2, ALB, ASG).")
        selected.append("compute")

    # Enforce dependency: apigateway requires serverless functions
    if "apigateway" in selected:
        if provider == "aws" and "lambda" not in selected:
            print("  ℹ  API Gateway requires Lambda — auto-enabling Lambda.")
            selected.append("lambda")
        elif provider == "gcp" and "cloud_functions" not in selected:
            print("  ℹ  API Gateway requires Cloud Functions — auto-enabling Cloud Functions.")
            selected.append("cloud_functions")
        elif provider == "azure" and "functions" not in selected:
            print("  ℹ  API Gateway requires Azure Functions — auto-enabling Azure Functions.")
            selected.append("functions")

    # Always include network module
    if "network" not in selected:
        selected.insert(0, "network")

    return selected


def ask_region(provider: str) -> str:
    """Interactively ask for the target region."""
    regions = DEFAULT_REGIONS.get(provider, [])

    region = questionary.select(
        f"Select {provider.upper()} region:",
        choices=regions + ["Other (type manually)"],
        style=CUSTOM_STYLE,
    ).ask()

    if region is None:
        print("\nAborted.")
        sys.exit(1)

    if region == "Other (type manually)":
        region = questionary.text(
            "Enter region:",
            style=CUSTOM_STYLE,
            validate=lambda x: len(x) > 0 or "Region cannot be empty",
        ).ask()
        if region is None:
            print("\nAborted.")
            sys.exit(1)

    return region


def ask_remote_backend() -> bool:
    """Ask whether to enable remote state backend."""
    result = questionary.confirm(
        "Enable remote backend (recommended for teams)?",
        default=True,
        style=CUSTOM_STYLE,
    ).ask()

    if result is None:
        print("\nAborted.")
        sys.exit(1)

    return result


def print_banner() -> None:
    """Print the tf-starter banner."""
    banner = r"""
  _    __             _              _
 | |  / _|       ___| |_ __ _ _ __| |_ ___ _ __
 | __| |_ _____ / __| __/ _` | '__| __/ _ \ '__|
 | |_|  _|_____|\__ \ || (_| | |  | ||  __/ |
  \__|_|        |___/\__\__,_|_|   \__\___|_|

  Enterprise Terraform Project Generator v1.0.0
"""
    print(banner)


def print_summary(
    provider: str,
    project_name: str,
    environments: list[str],
    services: list[str],
    region: str,
    enable_backend: bool,
) -> None:
    """Print generation summary."""
    print("\n" + "=" * 55)
    print("  ✔  Project created successfully!")
    print("=" * 55)
    print(f"  ✔  Project:      {project_name}")
    print(f"  ✔  Provider:     {provider.upper()}")
    print(f"  ✔  Region:       {region}")
    print(f"  ✔  Environments: {', '.join(environments)}")
    print(f"  ✔  Services:     {', '.join(services)}")
    print(f"  ✔  Backend:      {'Remote (S3 + DynamoDB)' if enable_backend else 'Local'}")
    print("=" * 55)
    print()

    print("  Generated modules:")
    for svc in services:
        print(f"    ✔  {svc}/")
    print()

    print(f"  Next steps:")
    print(f"    cd {project_name}")
    print(f"    make init")
    print(f"    make plan")
    print(f"    make apply")
    print()


def main() -> None:
    """Main entry point for tf-starter CLI."""
    print_banner()

    args = parse_args()

    if not validate_project_name(args.project_name):
        print(
            "Error: Project name must start with a letter and contain only "
            "letters, digits, hyphens, or underscores."
        )
        sys.exit(1)

    provider = args.provider.lower()
    project_name = args.project_name

    print(f"\n  Provider:     {provider.upper()}")
    print(f"  Project name: {project_name}\n")

    # Interactive questions
    environments = ask_environments()
    services = ask_services(provider)
    region = ask_region(provider)
    enable_backend = ask_remote_backend()

    # Build context for templates
    context = {
        "project_name": project_name,
        "provider": provider,
        "region": region,
        "environments": environments,
        "services": services,
        "enable_backend": enable_backend,
    }

    # Generate project
    try:
        generator = ProjectGenerator(
            project_name=project_name,
            output_dir=args.output_dir,
            context=context,
        )
        generator.generate()
    except Exception as e:
        print(f"\n  ✘  Error generating project: {e}")
        sys.exit(1)

    print_summary(provider, project_name, environments, services, region, enable_backend)


if __name__ == "__main__":
    main()

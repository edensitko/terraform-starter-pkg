"""Project generator — orchestrates template rendering and file creation."""

from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Any

from tf_starter.template_engine import TemplateEngine


class ProjectGenerator:
    """Generates a complete Terraform project from templates."""

    def __init__(
        self,
        project_name: str,
        output_dir: str,
        context: dict[str, Any],
    ) -> None:
        self.project_name = project_name
        self.output_dir = Path(output_dir).resolve()
        self.project_dir = self.output_dir / project_name
        self.context = context
        self.provider = context["provider"]
        self.engine = TemplateEngine(provider=self.provider, context=context)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def generate(self) -> Path:
        """Generate the full project. Returns the project directory path."""
        if self.project_dir.exists():
            raise FileExistsError(
                f"Directory '{self.project_dir}' already exists. "
                "Remove it first or choose a different project name."
            )

        self._create_directory_tree()
        self._generate_root_files()
        self._generate_modules()
        self._generate_environments()
        self._generate_github_workflow()
        self._generate_misc_files()

        return self.project_dir

    # ------------------------------------------------------------------
    # Directory tree
    # ------------------------------------------------------------------

    def _create_directory_tree(self) -> None:
        """Create the base directory structure."""
        self.project_dir.mkdir(parents=True)

        # modules/<service>/
        for service in self.context["services"]:
            (self.project_dir / "modules" / service).mkdir(parents=True)

        # environments/<env>/
        for env in self.context["environments"]:
            (self.project_dir / "environments" / env).mkdir(parents=True)

        # .github/workflows/
        (self.project_dir / ".github" / "workflows").mkdir(parents=True)

    # ------------------------------------------------------------------
    # Root-level Terraform files
    # ------------------------------------------------------------------

    def _generate_root_files(self) -> None:
        root_templates = [
            ("root/main.tf.j2", "main.tf"),
            ("root/providers.tf.j2", "providers.tf"),
            ("root/variables.tf.j2", "variables.tf"),
            ("root/outputs.tf.j2", "outputs.tf"),
            ("root/versions.tf.j2", "versions.tf"),
        ]

        for template_name, output_name in root_templates:
            content = self.engine.render(template_name)
            self._write(output_name, content)

        # backend.tf only when remote backend enabled
        if self.context["enable_backend"]:
            content = self.engine.render("root/backend.tf.j2")
            self._write("backend.tf", content)

    # ------------------------------------------------------------------
    # Module files
    # ------------------------------------------------------------------

    def _generate_modules(self) -> None:
        """Render each selected module's .tf files."""
        for service in self.context["services"]:
            module_template_dir = f"modules/{service}"

            # Each module has main.tf, variables.tf, outputs.tf
            for tf_file in ["main.tf", "variables.tf", "outputs.tf"]:
                template_path = f"{module_template_dir}/{tf_file}.j2"
                if self.engine.template_exists(template_path):
                    content = self.engine.render(template_path)
                    self._write(f"modules/{service}/{tf_file}", content)

    # ------------------------------------------------------------------
    # Environment files
    # ------------------------------------------------------------------

    def _generate_environments(self) -> None:
        """Render per-environment files."""
        for env in self.context["environments"]:
            extra = {
                "environment": env,
                "is_prod": env == "prod",
            }

            env_templates = [
                ("environments/main.tf.j2", f"environments/{env}/main.tf"),
                ("environments/variables.tf.j2", f"environments/{env}/variables.tf"),
                ("environments/terraform.tfvars.j2", f"environments/{env}/terraform.tfvars"),
            ]

            if self.context["enable_backend"]:
                env_templates.append(
                    ("environments/backend.tf.j2", f"environments/{env}/backend.tf")
                )

            for template_name, output_name in env_templates:
                content = self.engine.render(template_name, extra_context=extra)
                self._write(output_name, content)

    # ------------------------------------------------------------------
    # GitHub Actions
    # ------------------------------------------------------------------

    def _generate_github_workflow(self) -> None:
        content = self.engine.render("github/terraform.yml.j2")
        self._write(".github/workflows/terraform.yml", content)

    # ------------------------------------------------------------------
    # Makefile, init.sh, README, pre-commit
    # ------------------------------------------------------------------

    def _generate_misc_files(self) -> None:
        misc_templates = [
            ("misc/Makefile.j2", "Makefile"),
            ("misc/init.sh.j2", "init.sh"),
            ("misc/README.md.j2", "README.md"),
            ("misc/pre-commit-config.yaml.j2", ".pre-commit-config.yaml"),
        ]

        for template_name, output_name in misc_templates:
            content = self.engine.render(template_name)
            self._write(output_name, content)

        # Make init.sh executable
        init_path = self.project_dir / "init.sh"
        if init_path.exists():
            init_path.chmod(init_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _write(self, relative_path: str, content: str) -> None:
        """Write rendered content to a file inside the project directory."""
        dest = self.project_dir / relative_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
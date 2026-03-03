"""Jinja2 template engine for rendering Terraform files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined


TEMPLATES_DIR = Path(__file__).parent / "templates"


class TemplateEngine:
    """Renders Jinja2 templates with the given context."""

    def __init__(self, provider: str, context: dict[str, Any]) -> None:
        self.provider = provider
        self.context = context
        self.template_dir = TEMPLATES_DIR / provider

        if not self.template_dir.exists():
            raise FileNotFoundError(
                f"Template directory not found for provider '{provider}': "
                f"{self.template_dir}"
            )

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters
        self.env.filters["tf_bool"] = self._tf_bool
        self.env.filters["tf_list"] = self._tf_list

    @staticmethod
    def _tf_bool(value: bool) -> str:
        """Convert Python bool to Terraform bool."""
        return "true" if value else "false"

    @staticmethod
    def _tf_list(values: list[str]) -> str:
        """Convert Python list to Terraform list literal."""
        items = ", ".join(f'"{v}"' for v in values)
        return f"[{items}]"

    def render(self, template_path: str, extra_context: dict[str, Any] | None = None) -> str:
        """Render a template with context.

        Args:
            template_path: Relative path within the provider template dir.
            extra_context: Additional context merged on top of base context.

        Returns:
            Rendered template string.
        """
        ctx = {**self.context}
        if extra_context:
            ctx.update(extra_context)

        template = self.env.get_template(template_path)
        return template.render(**ctx)

    def render_string(self, template_str: str, extra_context: dict[str, Any] | None = None) -> str:
        """Render a raw template string with context."""
        ctx = {**self.context}
        if extra_context:
            ctx.update(extra_context)

        template = self.env.from_string(template_str)
        return template.render(**ctx)

    def template_exists(self, template_path: str) -> bool:
        """Check if a template file exists."""
        full_path = self.template_dir / template_path
        return full_path.exists()
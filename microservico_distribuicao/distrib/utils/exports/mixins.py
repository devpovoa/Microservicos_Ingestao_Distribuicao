# distrib/utils/exports/mixins.py
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html, format_html_join


class ExportActionsMixin:
    export_csv_url_name: str | None = None
    export_pdf_url_name: str | None = None

    def build_actions_html(self):
        querystring = self.request.GET.urlencode()
        parts = []

        def _href(name: str) -> str:
            url = reverse(name)
            return f'{url}{"?" + querystring if querystring else ""}'

        if self.export_csv_url_name:
            try:
                parts.append(format_html(
                    '<a class="btn btn-outline-secondary btn-sm" href="{}">'
                    '<i class="fa fa-file-export me-1"></i> Exportar CSV</a>',
                    _href(self.export_csv_url_name)
                ))
            except NoReverseMatch:
                pass

        if self.export_pdf_url_name:
            try:
                parts.append(format_html(
                    '<a class="btn btn-outline-secondary btn-sm" href="{}">'
                    '<i class="fa fa-file-pdf me-1"></i> PDF</a>',
                    _href(self.export_pdf_url_name)
                ))
            except NoReverseMatch:
                pass

        return format_html_join(" ", "{}", ((p,) for p in parts)) if parts else ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        actions = self.build_actions_html()
        if actions:
            ctx["actions"] = actions
        return ctx

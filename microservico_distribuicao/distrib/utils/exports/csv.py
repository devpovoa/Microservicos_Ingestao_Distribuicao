import csv
from typing import Iterable, Sequence

from django.http import StreamingHttpResponse

BOM_UTF8 = "\ufeff"


class Echo:
    def write(self, value):
        return value


def stream_csv(filename: str, headers: Sequence[str], rows: Iterable[Sequence], delimiter: str = ";"):
    writer = csv.writer(Echo(), delimiter=delimiter, lineterminator="\n")

    def row_iter():
        # BOM + cabeçalho
        yield BOM_UTF8 + writer.writerow(headers)
        for row in rows:
            yield writer.writerow(row)

    resp = StreamingHttpResponse(
        row_iter(), content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp

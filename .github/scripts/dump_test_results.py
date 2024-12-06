import argparse
import datetime
import json
import os
import shutil
from collections import defaultdict

HTML_BASE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    {style}
</head>
<body>
    {tables}
</body>
</html>"""

HTML_STYLE = """
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #ffffff;
        }
    </style>
"""

HTML_URL = """<a href="{}">{}</a>"""

def build_table(h2: str, headers: list[str], data: list[list[str]]) -> str:
    output = []
    # assert len(headers) == len(data[0])
    header_len = len(headers)
    # test state
    output.append(f"<h2>{h2}</h2>")
    # open table
    output.append("<table>")
    # table header
    output.append("<tr>")
    for header in headers:
        output.append(f"<th>{header}</th>")
    output.append("</tr>")
    # table data
    for row in data:
        output.append("<tr>")
        for value in row[:header_len]:
            output.append(f"<th>{value}</th>")
        output.append("</tr>")
    # close table
    output.append("</table>")
    return "\n".join(output)


def load_results(report_path: str) -> dict:
    with open(os.path.join(report_path, "results-report.json"), "rb") as file:
        return json.load(file)


def collect_tests(results):
    statistics = defaultdict(int)
    tests = defaultdict(list)
    for result in results:
        test_type = result["type"]
        if test_type != "test":
            continue
        status = result["status"]
        name = result["name"]
        subtest_name = result.get("subtest_name", "")
        duration = result.get("duration", 0)
        duration = str(round(duration, 2)) + " sec" if duration != 0 else ""
        log_path = result.get("links", {}).get("log", [""])[0]
        statistics[status] += 1
        tests[status].append([name, subtest_name, duration, log_path])
    return statistics, tests


def patch_display_path(path: str) -> str:
    basename = os.path.basename(path)
    return HTML_URL.format(f"logs/{basename}", "link") if path else ""

def dump_html_file(statistics: dict[str, int], tests: dict[str, tuple[str, str]], dump_to_dir: str) -> None:
    tables: list[str] = []

    status_tests = []
    for status, number in statistics.items():
        status_tests.append((status, number))
    tables.append(build_table("STATUS", ("Status", "Number"), status_tests))

    failed_tests = tests["FAILED"]
    failed_tests.sort()
    for i in range(len(failed_tests)):
        failed_tests[i][3] = patch_display_path(failed_tests[i][3])
    tables.append(build_table("FAILED", ("Name", "Subtest name", "Duration", "Logs"), failed_tests))

    ok_tests = tests["OK"]
    ok_tests.sort()
    tables.append(build_table("PASSED", ("Name", "Subtest name", "Duration"), ok_tests))

    skipped_tests = tests["SKIPPED"]
    skipped_tests.sort()
    tables.append(build_table("SKIPPED", ("Name", "Subtest name", "Duration"), skipped_tests))

    with open(os.path.join(dump_to_dir, "statistics.html"), "w") as statistics_writer:
        statistics_writer.write(
            HTML_BASE.format(page_title="Test results", style=HTML_STYLE, tables="\n".join(tables))
        )

def dump_failed_logs(tests, dump_to_dir):
    dump_logs_dir = os.path.join(dump_to_dir, "logs")
    if os.path.exists(dump_logs_dir):
        shutil.rmtree(dump_logs_dir)
    os.mkdir(dump_logs_dir)
    for failed_test in tests["FAILED"]:
        src = failed_test[3]
        dst = os.path.join(dump_logs_dir, os.path.basename(src))
        if src == "":
            continue
        if not os.path.exists(src):
            failed_test[3] = ""
            continue
        shutil.copy(src, dst)


def make_index_html(directory, current_depth=1):
    if current_depth > 10:
        return
    files = os.listdir(directory)
    files.sort(key=lambda x: (os.path.isfile(os.path.join(directory, x)), x))

    table = []

    if current_depth != 1:
        table.append((HTML_URL.format("../index.html", ".."), "-", "-"))

    for file in files:
        if file == "index.html":
            continue
        abs_file_path = os.path.join(directory, file)
        modification_time_timestamp = os.path.getmtime(abs_file_path)
        modification_time_obj = datetime.datetime.fromtimestamp(modification_time_timestamp)
        modification_time_str = modification_time_obj.strftime("%Y-%m-%d %H:%M:%S")

        url = file+"/index.html" if os.path.isdir(abs_file_path) else file

        table.append((
            HTML_URL.format(url, file),
            str(os.path.getsize(abs_file_path))+" bytes" if os.path.isfile(abs_file_path) else "-",
            modification_time_str
        ))
        if os.path.isdir(abs_file_path):
            make_index_html(abs_file_path, current_depth=current_depth+1)

    table = build_table(os.path.basename(directory), ("Filename", "Filesize", "Modification time"), table)

    index_path = os.path.join(directory, "index.html")
    with open(index_path, "w") as statistics_writer:
        statistics_writer.write(
            HTML_BASE.format(page_title="like mc but better", style=HTML_STYLE, tables=table)
        )


def main(report_path: str, dump_to_dir: str) -> None:
    report = load_results(report_path)
    results = report.get("results", {})
    statistics, tests = collect_tests(results)
    dump_failed_logs(tests, dump_to_dir)
    dump_html_file(statistics, tests, dump_to_dir)
    make_index_html(dump_to_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--report-path", help="Path to output folder from `ya make --output <report-path>`", required=True
    )
    parser.add_argument(
        "-o", "--dump-to-dir", help="Where to dump folder (it can be rewriten)", required=True
    )

    args = parser.parse_args()

    report_path = args.report_path
    dump_to_dir = args.dump_to_dir

    main(report_path, dump_to_dir)

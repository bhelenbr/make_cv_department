#!/usr/bin/env python3

from pathlib import Path
import argparse

TEMPLATE_NAME = "make_cv/PersonalData/ContactInfo.tex"


def parse_name(dirname):
    """
    Parse a directory name of the form

        LastName, FirstName
    """
    try:
        last, first = [x.strip() for x in dirname.split(",", 1)]
    except ValueError:
        raise ValueError(
            f'"{dirname}" is not in the format "LastName, FirstName".'
        )

    return first, last


def build_replacements(first, last):
    first_initial = first[0]
    last8 = last[0:8] if len(last) > 8 else last
    return {
        "FirstInitialLastName8": f"{first_initial}{last8}",
        "FirstName": first,
        "LastName": last,
        "FirstInitial": first_initial,
    }

def fill_template(template, replacements):
    for old, new in replacements.items():
        template = template.replace(old, new)
    return template


def process_directory(directory, template_text):
    directory = Path(directory)

    if not directory.is_dir():
        print(f"Skipping {directory}: not a directory")
        return

    first, last = parse_name(directory.name)

    replacements = build_replacements(first, last)

    output = fill_template(template_text, replacements)

    outfile = directory / TEMPLATE_NAME
    outfile.write_text(output, encoding="utf-8")

    print(f"Wrote {outfile}")


def main():

    parser = argparse.ArgumentParser(
        description="Fill ContactInfo.tex template."
    )

    parser.add_argument(
        "directories",
        nargs="+",
        help="Directories named 'LastName, FirstName'",
    )

    parser.add_argument(
        "-t",
        "--template",
        required=True,
        help="Path to ContactInfo.tex template",
    )

    args = parser.parse_args()

    template = Path(args.template).read_text(encoding="utf-8")

    for d in args.directories:
        process_directory(d, template)


if __name__ == "__main__":
    main()
from collections import namedtuple
from datetime import date

import click

from regparser import eregs_index
from regparser.history import annual
from regparser.tree import xml_parser


LastVersionInYear = namedtuple('LastVersionInYear', ['version_id', 'year'])


def last_versions(cfr_title, cfr_part):
    """Run through all known versions of this regulation and pull out versions
    which are the last to be included before an annual edition"""
    have_annual_edition = {}
    path = eregs_index.VersionPath(cfr_title, cfr_part)
    if len(path) == 0:
        raise click.UsageError("No versions found. Run `versions`?")
    for version in path:
        pub_date = annual.date_of_annual_after(cfr_title, version.effective)
        if pub_date < date.today():
            have_annual_edition[pub_date.year] = version.identifier
    for year in sorted(have_annual_edition.keys()):
        yield LastVersionInYear(have_annual_edition[year], year)


def process(last_version, input_path, tree_path):
    """Parse the XML into a JSON tree; write it to disk"""
    xml = input_path.read_xml(last_version.year)
    tree = xml_parser.reg_text.build_tree(xml)
    tree_path.write(last_version.version_id, tree)


def process_if_needed(cfr_title, cfr_part, last_versions):
    """Calculate dependencies between input and output files for these annual
    editions. If an output is missing or out of date, process it"""
    annual_path = eregs_index.Path("annual", cfr_title, cfr_part)
    tree_path = eregs_index.TreePath(cfr_title, cfr_part)
    deps = eregs_index.DependencyGraph()

    for last_version in last_versions:
        deps.add(('tree', cfr_title, cfr_part, last_version.version_id),
                 ('version', cfr_title, cfr_part, last_version.version_id))
        deps.add(('tree', cfr_title, cfr_part, last_version.version_id),
                 ('annual', cfr_title, cfr_part, last_version.year))

    for last_version in last_versions:
        deps.validate_for('tree', cfr_title, cfr_part, last_version.version_id)
        if deps.is_stale('tree', cfr_title, cfr_part, last_version.version_id):
            process(last_version, annual_path, tree_path)


@click.command()
@click.argument('cfr_title', type=int)
@click.argument('cfr_part', type=int)
def annual_editions(cfr_title, cfr_part):
    """Parse available annual editions for this reg. Cycles through all known
    versions and parses the annual edition XML when relevant"""
    versions = list(last_versions(cfr_title, cfr_part))
    process_if_needed(cfr_title, cfr_part, versions)
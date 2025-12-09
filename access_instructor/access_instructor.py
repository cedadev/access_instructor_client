import configparser
import os
import sys
from glob import glob
from pathlib import Path
from string import punctuation

import click
import requests

config = configparser.ConfigParser()
config_path = os.environ.get("ACCESS_INSTRUCTOR_CLIENT_CONFIG_FILE")

if not config_path:
    config_path = os.path.join(
        Path(__file__).parent,
        ".access_instructor_client_config.ini",
    )
    os.environ["ACCESS_INSTRUCTOR_CLIENT_CONFIG_FILE"] = config_path

config.read(config_path)

API_URL = config["DEFAULT"]["API_URL"]
TOKEN = config["DEFAULT"]["TOKEN"]


@click.group()
def main():
    """Command line tool for interacting with the access instructor."""
    pass


def display_rules(response, sub=True):
    """Display rules and optionally sub rules in readable format"""
    if "path_rules" in response:

        for path, path_rules in response["path_rules"].items():

            if rules := path_rules["rules"]:
                click.echo(f"Rules for {path}:")
                echo_rules(rules)

            if (sub_rules := path_rules["sub_rules"]) and sub:
                click.echo(f"Sub rules for {path}:")
                echo_rules(sub_rules)

    elif len(response) == 0:
        click.echo("No matching rules")

    else:
        click.echo(f"{len(response)} rules found:")
        click.echo("ID : Path : Type : Group : Licence : Expiry date")
        echo_rules(response)


def echo_rules(rules):
    """Display rules in readable format"""
    for rule in rules:

        group_str = f" : {rule['group']['name']}" if rule["rule_type"] == "G" else ""
        licence_str = f" : {rule['licence']['title']}" if rule["licence"] else ""
        expiry_str = f" [expires: {rule['expiry_date']}]" if rule["expiry_date"] else ""

        click.echo(
            f"{rule['id']} : {rule['path']} : {rule['rule_type']}{group_str}{licence_str}{expiry_str}"
        )


@main.command()
@click.option(
    "--path",
    "-p",
    "path",
    default=None,
    help="Path for directory rule will be applied to.",
)
@click.option(
    "--type",
    "-t",
    "rule_type",
    default=None,
    type=click.Choice(["N", "P", "R", "G"]),
    help='Rule type. Either: No access "N", Public "P", Registered User "R" or Group "G".',
)
@click.option("--group", "-g", default=None, help="Group name to be given access.")
@click.option(
    "--expiry_date",
    "-e",
    default=None,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Date rule will expire on. Format: YYY-MM-DD.",
)
@click.option("--comment", "-c", default="", help="Any comments to help traceability.")
@click.option(
    "--licence",
    "-l",
    "licence_code",
    default=None,
    help="Code for licence associated with this rule.",
)
@click.option(
    "--licence-cat",
    "-k",
    "licence_category",
    default=None,
    multiple=True,
    help="Licence category.",
)
def list_rule(
    path,
    rule_type,
    group,
    expiry_date,
    comment,
    licence_code,
    licence_category,
):
    """List Rules that match given parameters"""

    data = {}

    if rule_type:
        data["rule_type"] = rule_type

    if group:
        data["group"] = group

    if expiry_date:
        data["expiry_date"] = expiry_date.strftime("%Y-%m-%d")

    if comment:
        data["comment"] = comment

    if licence_code:
        data["licence_code"] = licence_code

    if licence_category:
        data["licence_category"] = licence_category

    if path:
        paths = []
        for glob_path in glob(path):
            paths.append(glob_path)

        if not paths:
            paths.append(path)

        data["paths"] = paths

    response = requests.post(f"{API_URL}/rule/find", json=data)

    if response.ok:
        display_rules(response.json())

    else:
        click.echo(
            f"Error. status code: {response.status_code}, reason: {response.reason}"
        )
        click.echo(f"{response.text}")


@main.command()
@click.option(
    "--path",
    "-p",
    "path",
    default=None,
    help="Path to search for rules",
)
@click.option(
    "--allow-sub-rules",
    "-a",
    default=False,
    is_flag=True,
    help="Allow running sub rules as well",
)
@click.option(
    "--force",
    "-f",
    default=False,
    is_flag=True,
    help="Skips the confirmation step",
)
def run_rules(path, allow_sub_rules=False, force=False):
    """Runs a path's rules, triggering the pipeline which updates relevant access in the archive"""

    data = {}

    if path:
        glob_paths = []
        for glob_path in glob(path):
            glob_paths.append(glob_path)

        if not glob_paths:
            glob_paths.append(path)

        data["paths"] = glob_paths

    click.echo(glob_paths)

    response = requests.post(f"{API_URL}/rule/find", json=data)

    if not response.ok:
        click.echo(
            f"Error. status code: {response.status_code}, reason: {response.reason}"
        )
        click.echo(f"{response.text}")

    response_data = response.json()
    rules = []
    sub_rules = []
    if "path_rules" in response_data:

        for _, path_rules in response_data["path_rules"].items():

            if rules := path_rules["rules"]:
                click.echo(f"Rules:")
                echo_rules(rules)

            if (sub_rules := path_rules["sub_rules"]):
                click.echo(f"Sub rules:")
                echo_rules(sub_rules)

    elif len(response_data) == 0:
        click.echo("No matching rules")
        sys.exit()

    if allow_sub_rules:
        rules = rules + sub_rules

    if len(rules) < 1:
        click.echo(f"There are no rules for the provided paths")
        sys.exit()

    if not force:
        click.echo(f"This will run the pipeline for {len(rules)} rules")
        if not click.confirm("Do you want to continue?"):
            sys.exit()

    click.echo(f"Running selected rules...")
    for rule in rules:

        rule_id = rule["id"]
        rule_path = rule["path"]
        click.echo(f"Running {rule_id} ({rule_path})")

        response = requests.post(f"{API_URL}/rule/run", json={"id": rule_id}, headers={"Authorization": f"Token {TOKEN}"})

        if not response.ok:
            click.echo(
                f"Failed to run {rule_id}. status code: {response.status_code}, reason: {response.reason}"
            )
            sys.exit()

    click.echo("Finished")


@main.command()
@click.option(
    "--path",
    "-p",
    "path",
    required=True,
    help="Path for directory rule will be applied to.",
)
@click.option(
    "--type",
    "-t",
    "rule_type",
    required=True,
    type=click.Choice(["N", "P", "R", "G"]),
    help='Rule type. Either: No access "N", Public "P", Registered User "R" or Group "G".',
)
@click.option("--group", "-g", default=None, help="Group name to be given access.")
@click.option(
    "--expiry_date",
    "-e",
    default=None,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Date rule will expire on. Format: YYY-MM-DD.",
)
@click.option("--comment", "-c", default="", help="Any comments to help traceability.")
@click.option(
    "--licence",
    "-l",
    "licence_code",
    default=None,
    help="Code for licence associated with this rule.",
)
@click.option(
    "--check",
    "-c",
    default=False,
    is_flag=True,
    help="Will display existing rules before creation of new rules",
)
def add_rule(path, rule_type, group, expiry_date, comment, licence_code, check):
    """Create Rules with given parameters"""

    data = {
        "paths": [],
        "rule_type": rule_type,
        "group": group,
        "expiry_date": expiry_date.strftime("%Y-%m-%d") if expiry_date else expiry_date,
        "comment": comment,
        "licence_code": licence_code,
    }

    if rule_type == "G" and not group:
        click.echo("Group rules must have a group(-g)")
        sys.exit()

    if any(wildcard in path for wildcard in punctuation.replace("/", "")):
        for glob_path in glob(path):
            data["paths"].append(glob_path)

    else:
        data["paths"].append(path)

    if check:
        response = requests.post(f"{API_URL}/rule/find", json={"paths": data["paths"]})

        if response.ok:
            display_rules(response.json())

        else:
            click.echo(
                f"Error. status code: {response.status_code}, reason: {response.reason}"
            )
            click.echo(f"{response.text}")

    if len(data["paths"]) < 1:
        click.echo(f"There are no paths for {path}")
        sys.exit()

    click.echo(f"This will create {len(data['paths'])} rules")
    if not click.confirm("Do you want to continue?"):
        sys.exit()

    response = requests.post(
        f"{API_URL}/rule/add", json=data, headers={"Authorization": f"Token {TOKEN}"}
    )

    if response.ok:
        click.echo(
            f"Successfully created {len(data['paths'])} rules for {path} : {rule_type}{' : ' + group if rule_type == 'G' else ''}"
        )

    else:
        # If some rules already exist tell user and create the others if needed.
        click.echo(
            f"Error. status code: {response.status_code}, reason: {response.reason}"
        )
        click.echo(f"{response.text}")


@main.command()
@click.option(
    "--rule",
    "-r",
    "rule",
    required=True,
    help="ID of rule to be updated.",
)
@click.option(
    "--path",
    "-p",
    "path",
    required=False,
    help="Path for rule to be applied to.",
)
@click.option(
    "--type",
    "-t",
    "rule_type",
    required=False,
    type=click.Choice(["N", "P", "R", "G"]),
    help='Rule type. Either: No access "N", Public "P", Registered User "R" or Group "G".',
)
@click.option("--group", "-g", default=None, help="Group name to be given access.")
@click.option(
    "--expiry_date",
    "-e",
    default=None,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Date rule will expire on. Format: YYY-MM-DD.",
)
@click.option("--comment", "-c", default="", help="Any comments to help traceability.")
@click.option(
    "--licence",
    "-l",
    "licence_code",
    default=None,
    help="Code for licence associated with this rule.",
)
@click.option(
    "--check",
    "-c",
    default=False,
    is_flag=True,
    help="Will display existing rules before creation of new rules",
)
def update_rule(
    rule, path, rule_type, group, expiry_date, comment, licence_code, check
):
    """Updates a Rule of the given id with given parameters"""

    data = {
        "rule": rule,
        "path": path,
        "rule_type": rule_type,
        "group": group,
        "expiry_date": expiry_date.strftime("%Y-%m-%d") if expiry_date else expiry_date,
        "comment": comment,
        "licence_code": licence_code,
    }

    if rule_type == "G" and not group:
        click.echo("Group rules must have a group(-g)")
        sys.exit()

    elif group:
        click.echo("Only group rules have a specified group(-g)")
        sys.exit()

    if check:
        response = requests.post(f"{API_URL}/rule/find", json={"paths": data["path"]})

        if response.ok:
            display_rules(response.json())

        else:
            click.echo(
                f"Error. status code: {response.status_code}, reason: {response.reason}"
            )
            click.echo(f"{response.text}")

    response = requests.post(
        f"{API_URL}/rule/update",
        json=data,
        headers={"Authorization": f"Token {TOKEN}"},
    )

    if response.ok:
        click.echo(f"Successfully updated rule: {rule}")

    else:
        # If some rules already exist tell user and create the others if needed.
        click.echo(
            f"Error. status code: {response.status_code}, reason: {response.reason}"
        )
        click.echo(f"{response.text}")


@main.command()
@click.option(
    "--path", "-p", "path", help="Path for directory rule will be applied to."
)
@click.option(
    "--type",
    "-t",
    "rule_type",
    type=click.Choice(["N", "P", "R", "G"]),
    help='Rule type. Either: No access "N", Public "P", Registered User "R" or Group "G".',
)
@click.option("--group", "-g", default=None, help="Group name to be given access.")
@click.option(
    "--expiry_date",
    "-e",
    default=None,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Date rule will expire on. Format: YYY-MM-DD.",
)
@click.option("--comment", "-c", default="", help="Any comments to help traceability.")
@click.option(
    "--licence",
    "-l",
    "licence_code",
    default=None,
    help="Code for licence associated with this rule.",
)
@click.option(
    "--check",
    "-c",
    default=False,
    is_flag=True,
    help="Will display existing rules before creation of new rules",
)
def remove_rule(path, rule_type, group, expiry_date, comment, licence_code, check):
    """Remove Rules that match given parameters"""

    data = {
        "paths": [],
        "rule_type": rule_type,
    }

    if group:
        data["group"] = group

    if expiry_date:
        data["expiry_date"] = expiry_date.strftime("%Y-%m-%d")

    if comment:
        data["comment"] = comment

    if licence_code:
        data["licence_code"] = licence_code

    if any(wildcard in path for wildcard in punctuation.replace("/", "")):
        for glob_path in glob(path):
            data["paths"].append(glob_path)

    else:
        data["paths"].append(path)

    if check:
        response = requests.post(f"{API_URL}/rule/find", json=data)

        if response.ok:
            display_rules(response.json(), sub=False)

        else:
            click.echo(
                f"Error. status code: {response.status_code}, reason: {response.reason}"
            )

    if len(data["paths"]) < 1:
        click.echo(f"There are no paths for {path}")
        sys.exit()

    click.echo(f"This will remove all rules for paths [{', '.join(data['paths'])}]")
    if not click.confirm("Do you want to continue?"):
        sys.exit()

    response = requests.post(
        f"{API_URL}/rule/remove", json=data, headers={"Authorization": f"Token {TOKEN}"}
    )

    if response.ok:
        click.echo(f"Deleted: all rules for paths [{', '.join(data['paths'])}]")

    else:
        click.echo(
            f"Error. status code: {response.status_code}, reason: {response.reason}"
        )
        click.echo(f"{response.text}")


def display_licences(licences):
    """display licences in readable format"""
    for licence in licences:
        categories_str = ""
        if "categories" in licence and len(licence["categories"]) > 0:
            categories_str = " ["

            for cat in licence["categories"]:
                categories_str += f"{cat}, "

            categories_str = categories_str.rstrip(" ,")
            categories_str += "]"

        click.echo(
            f"    {licence['code']}{categories_str} : {licence['title']} : {licence['url_link']}"
        )


@main.command()
@click.option("--code", "-c", default=None, help="Code abbreviation of licence.")
@click.option("--title", "-t", default=None, help="Title of licence.")
@click.option("--url", "-u", default=None, help="Text for licence.")
@click.option(
    "--tag",
    "-k",
    "category_tags",
    default=None,
    multiple=True,
    help="Category tag of licence.",
)
def list_licence(code, title, url, category_tags):
    """List Licences that match given parameters"""

    data = {}

    if code:
        data["code"] = code

    if title:
        data["title"] = title

    if url:
        data["url"] = url

    if category_tags:
        data["category_tags"] = category_tags

    response = requests.post(f"{API_URL}/licence/find", json=data)

    if response.ok:
        licences = response.json()

        if len(licences) == 0:
            click.echo("No matching licences")

        else:
            click.echo(f"{len(licences)} licences found:")
            display_licences(licences)

    else:
        click.echo(
            f"Error. status code: {response.status_code}, reason: {response.reason}"
        )
        click.echo(f"{response.text}")


@main.command()
@click.option("--code", "-c", required=True, help="Code abbreviation for licence.")
@click.option("--title", "-t", default="", help="Licence title.")
@click.option("--url", "-u", required=True, help="Text for licence.")
@click.option(
    "--com", "-d", "comment", default="", help="Any comments to help traceability."
)
@click.option(
    "--tag",
    "-k",
    "category_tags",
    default=None,
    multiple=True,
    help="Category tag of licence.",
)
def add_licence(code, title, url, comment, category_tags):
    """Create Licence with given parameters"""

    data = {
        "code": code,
        "title": title,
        "url_link": url,
        "comment": comment,
        "category_tags": category_tags,
    }

    response = requests.post(
        f"{API_URL}/licence/add", json=data, headers={"Authorization": f"Token {TOKEN}"}
    )

    if response.ok:
        click.echo(f"Successfully created licence {code} : {title}")

    else:
        click.echo(
            f"Error. status code: {response.status_code}, reason: {response.reason}"
        )
        click.echo(f"{response.text}")


@main.command()
@click.option("--code", "-c", default=None, help="Code abbreviation for licence.")
@click.option("--title", "-t", default=None, help="Licence title.")
@click.option("--url", "-u", default=None, help="Text for licence.")
@click.option(
    "--com", "-d", "comment", default=None, help="Any comments to help traceability."
)
@click.option(
    "--tag",
    "-k",
    "category_tags",
    default=None,
    multiple=True,
    help="Category tag of licence.",
)
@click.option(
    "--check",
    "-q",
    default=False,
    is_flag=True,
    help="Will display existing rules before creation of new rules",
)
def remove_licence(code, title, url, comment, category_tags, check):
    """Create Licence with given parameters"""

    data = {}

    if code:
        data["code"] = code

    if title:
        data["title"] = title

    if title:
        data["url"] = url

    if title:
        data["comment"] = comment

    if category_tags:
        data["category_tags"] = category_tags

    if check:
        response = requests.post(f"{API_URL}/licence/find", json=data)

        if response.ok:
            licences = response.json()

            click.echo("This will remove licences: ")
            display_licences(licences)

            if not click.confirm("Do you want to continue?"):
                sys.exit()

        else:
            click.echo(
                f"Error. status code: {response.status_code}, reason: {response.reason}"
            )
            click.echo(f"{response.text}")
            sys.exit()

    response = requests.post(f"{API_URL}/licence/remove", json=data)

    if response.ok:
        click.echo(f"Successfully removed licence {code} : {title}")

    else:
        click.echo(
            f"Error. status code: {response.status_code}, reason: {response.reason}"
        )
        click.echo(f"{response.text}")


if __name__ == "__main__":
    main()

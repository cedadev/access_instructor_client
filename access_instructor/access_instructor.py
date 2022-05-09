
import json
import requests
import click
from glob import glob


api_url = "http://127.0.0.1:8000/api/v1"

@click.group()
def main():
   """Command line tool for interacting with the access instructor."""
   pass


@main.command()
@click.option('--path', '-p', 'path_pattern', help='Path for directory rule will be applied to.', type=str)
def add_path(path_pattern):
    """Command for adding paths."""

    data = []

    for path in glob(path_pattern):
      data.append({"path_pattern_str": path})

    if len(data) < 1:
        click.echo(f"There are no paths for {path_pattern}")
        exit()

    # If there are multiple path check the user wants to create them.
    elif len(data) > 1:
        click.echo(f"This will create {len(data)} paths")

        if not click.confirm("Do you want to continue?"):
            exit()

    response = requests.post(f"{api_url}/path/add", json=data)

    if response.ok:
        click.echo(f"Successfully created {len(data)} paths for {path}")

    else:
        # If some paths already exist tell user and create the others if needed.
        try:
            response_text = json.loads(response.text)

            if isinstance(response_text, list):
                exists_paths = []
                n = 0

                for error in response_text:

                    if not error:
                        continue
                    
                    elif error["path_pattern_str"] == ["path pattern with this path pattern str already exists."]:
                        exists_paths.append(data[n])

                    else:
                        raise

                    n += 1

                click.echo(f"{len(exists_paths)} paths already exist:")

                for path in exists_paths:
                    click.echo(f"    {path['path_pattern_str']}")

                if len(data) - len(exists_paths) < 1 or not click.confirm(f"Do you still want to create {len(data) - len(exists_paths)} paths?"):
                    exit()

                new_data = [path for path in data if path not in exists_paths]

                response = requests.post(f"{api_url}/path/add", json=new_data)

                if response.ok:
                    click.echo(f"Successfully created {len(data)} paths for {path}")

                else:
                    raise
                
            else:
                raise

        except SystemExit:
            click.echo(f"Exiting...")

        except:
            click.echo(f"Error. status code: {response.status_code}, reason: {response.reason}")


@main.command()
@click.option('--path', '-p', 'path_pattern', help='Path for directory rule will be applied to.')
@click.option('--type', '-t', 'rule_type', type=click.Choice(['N', 'P', 'R', 'G']), help='Rule type. Either: No access "N", Public "P", Registered User "R" or Group "G".')
@click.option('--group', '-g', default=None, help='Group name to be given access.')
@click.option('--expiry_date', '-e', default=None, help='Date rule will expire on.')
@click.option('--comment', '-c', default='', help='Any comments to help traceability.')
@click.option('--licence', '-l', 'licence_code', default=None, help='Code for licence associated with this rule.')
@click.option('--override', '-o', default=False, is_flag=True, help='Override rule will allow a group access to all subdirectories')
def add_rule(path_pattern, rule_type, group, expiry_date, comment, licence_code, override):
    """Command for adding Rules."""

    data = {
        "path_patterns": [],
        "rule_type": rule_type,
        "group": group,
        "expiry_date": expiry_date,
        "comment": comment,
        "licence_code": licence_code,
        "override": override
    }

    # for path in glob(path_pattern):
    #     data["path_patterns"].append(path)
    
    data["path_patterns"].append(path_pattern)

    if len(data["path_patterns"]) < 1:
        click.echo(f"There are no paths for {path_pattern}")
        exit()

    # If there are multiple paths check the user wants to create them.
    elif len(data["path_patterns"]) > 1:
        click.echo(f"This will create {len(data['path_patterns'])} rules")

        if not click.confirm("Do you want to continue?"):
            exit()

    response = requests.post(f"{api_url}/rule/add", json=data)

    if response.ok:
        click.echo(f"Successfully created {len(data['path_patterns'])} rules for {path_pattern} : {rule_type}{' : ' + group if rule_type == 'G' else ''}")

    else:
        # If some rules already exist tell user and create the others if needed.
        try:
            response_text = json.loads(response.text)

            if isinstance(response_text, list):
                exists_paths = []
                n = 0

                for error in response_text:

                    if not error:
                        continue
                    
                    elif error["path_pattern_str"] == ["path pattern with this path pattern str already exists."]:
                        exists_paths.append(data[n])

                    else:
                        raise

                    n += 1

                click.echo(f"{len(exists_paths)}  already exist:")

                for path in exists_paths:
                    click.echo(f"    {path['path_patterns']} : {rule_type}{' : ' + group if rule_type == 'G' else ''}")

                if len(data["path_patterns"]) - len(exists_paths) < 1 or not click.confirm(f"Do you still want to create {len(data['path_patterns']) - len(exists_paths)} rules?"):
                    exit()

                new_data = data

                new_data["path_patterns"] = [path for path in data["path_patterns"] if path not in exists_paths]

                response = requests.post(f"{api_url}/path/add", json=new_data)

                if response.ok:
                    click.echo(f"Successfully created {len(data)} rules for {path['path_patterns']} : {rule_type}{' : ' + group if rule_type == 'G' else ''}")

                else:
                    raise
                
            else:
                raise

        except SystemExit:
            click.echo(f"Exiting...")

        except:
            click.echo(f"Error. status code: {response.status_code}, reason: {response.reason}")


@main.command()
@click.option('--path', '-p', 'path_pattern', help='Path for directory rule will be applied to.')
@click.option('--type', '-t', 'rule_type', type=click.Choice(['N', 'P', 'R', 'G']), help='Rule type. Either: No access "N", Public "P", Registered User "R" or Group "G".')
@click.option('--group', '-g', default=None, help='Group name to be given access.')
@click.option('--expiry_date', '-e', default=None, help='Date rule will expire on.')
@click.option('--comment', '-c', default='', help='Any comments to help traceability.')
@click.option('--licence', '-l', 'licence_code', default=None, help='Code for licence associated with this rule.')
@click.option('--override', '-o', default=False, is_flag=True, help='Override rule will allow a group access to all subdirectories')
def remove_rule(path_pattern, rule_type, group, expiry_date, comment, licence_code, override):
    """Remove rules with given parameters"""

    data = {
        "path_patterns": [],
        "rule_type": rule_type,
    }

    if group:
        data["group"] = group
    
    if expiry_date:
        data["expiry_date"] = expiry_date

    if comment:
        data["comment"] = comment

    if licence_code:
        data["licence_code"] = licence_code

    if override:
        data["override"] = override

    # for path in glob(path_pattern):
    #     data["path_patterns"].append(path)
    
    data["path_patterns"].append(path_pattern)

    print(data)

    if len(data["path_patterns"]) < 1:
        click.echo(f"There are no paths for {path_pattern}")
        exit()

    response = requests.post(f"{api_url}/rule/find", json=data)

    response_data = response.json()

    if len(response_data) < 1:
        click.echo(f"There are no rules for {path_pattern}")
        exit()

    # If there are multiple paths check the user wants to delete them.
    elif len(response_data) >= 1:
        click.echo(f"This will delete {len(response_data)} rules")
        for rule in response_data:
            click.echo(f"    {rule['path_pattern']} : {rule['rule_type']}{' : ' + rule['group'] if rule['rule_type'] == 'G' else ''}")

        if not click.confirm("Do you want to continue?"):
            exit()

    response = requests.post(f"{api_url}/rule/remove", json=data)

    if response.ok:
        click.echo(f"Deleted: all rules for {path_pattern}, reason: {response.reason}")
    else:
        click.echo(f"Error. status code: {response.status_code}, reason: {response.reason}")
    

@main.command()
@click.option('--code', '-c', help='Code abbreviation for licence.')
@click.option('--title', '-t', default=None, help='Licence title.')
@click.option('--url', '-u', help='Text for licence.')
@click.option('--com', 'comment', default=None, help='Any comments to help traceability.')
@click.option('--cat', 'category', default=None, multiple=True, help='Licence category.')
def add_licence(code, title, url, comment, category):

    licence_data = {
        "code": code,
        "title": title,
        "url_link": url,
        "comment": comment,
        "categories": category
    }
    
    response = requests.post(f"{api_url}/licence/add", json=licence_data)

    if response.ok:
        click.echo(f"Successfully created licence {code} : {title}")

    else:
        click.echo(f"Error. status code: {response.status_code}, reason: {response.reason}")


@main.command()
@click.option('--category', '-cat', default=None, multiple=True, help='Licence category.')
def list_licence(category):

    licence_data = {
        "categories": category
    }
    
    response = requests.post(f"{api_url}/licence/find", json = licence_data)

    if response.ok:
        licences = response.json()

        if len(licences) == 0:
            click.echo("No matching licences")

        else:
            click.echo(f"{len(licences)} licences found:")

            for licence in licences:
                click.echo(f"    {licence}")

    else:    
        click.echo(f"Error. status code: {response.status_code}, reason: {response.reason}")    


if __name__ == '__main__':
    main()

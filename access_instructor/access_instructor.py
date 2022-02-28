
import os
import sys
from docopt import docopt

__doc__ = """
Make add and remove rules to the access instructor system. 

Usage:
  access_instructor -h | --help
  access_instructor --version
  access_instructor add [-e <date>] [(-p|-r|-g <group>)]  <license> <path>...  
  access_instructor remove [(-p|-r|-g <group>)] <path>...
  access_instructor list [-l <license>] [-t <license_tag>] <path>
  access_instructor licenses  
  
Options:
  <license>     short license code
  <path>        Path assoiated with the rule.
  -e <date>        expiry date for the rule.
  -p            add or remove public rule
  -r            add or remove reguser rule 
  -g <group>    add or remove group rule
  -l <license>  list rules for this license
  -t <license_tag>  list rules for this license tag.
  -h --help    Show this message.
  --version    Show version for the client
  
"""

def add(rule_type, group, edate, license_code, paths):
    """Add rules"""
    print("Adding rules")
 
    for path in paths:
        print(f"  + {rule_type} {group} {edate} {license_code} {path}")
        
def remove(rule_type, group, paths):
    """remove rules"""
    print("Remove rules")
    for path in paths:
        print(f"  + {rule_type} {group} {path}")

def listrules(license_code, license_tag, path):
    """List rule"""
    print("List rules")
    print(f" {license_code} {license_tag} {path}")
    
def licenses():
    print("list licenses")



def main():
    arguments = docopt(__doc__, version='0.0.1')
    print(arguments)
    if arguments["add"]: 
        add("type", arguments["-g"], arguments["-e"], arguments["<license>"], arguments["<path>"])
    if arguments["remove"]: 
        remove("type", arguments["-g"], arguments["<path>"])
    if arguments["list"]: 
        listrules(arguments["-l"], arguments["-t"], arguments["<path>"])
    if arguments["licenses"]: 
        licenses()


if __name__ == '__main__':
    main()

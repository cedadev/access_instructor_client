# Access instructor client lib and command line tools


Command line and library functions for the access instructor. Note adding and editing licenses and license catagoies is 
assumesed to be done via the web insterface.

## Add rule

Add a rule with a type, a license and optionaly an expire date.

    add /badc/x/y public OGL
    add -e 2023-01-03 /badc/t reguser OGL
    add /badc/z/c zdata_group mylicense  

## Delete rule

Delete all rules for a path, or a specific rule

    remove /badc/x/y
    remove /badc/x/y my_group
    

## List rules

list all rules in a way that you could use grep.

    list /badc/x
    /badc noaccess unknown 
    /badc/x public OGL
    /badc/x/y mygroup XXX [expires: 2023-04-12]
    /badc/x/a group1 OGL
    /badc/x/a group2 CUNGL

list rules for a license

    list -l OGL /badc/x
    /badc/x public OGL
    /badc/x/a group1 OGL
        
list rules for a license tag

    list -t comm /badc/x
    /badc/x public OGL
    /badc/x/a group1 OGL
    /badc/x/a group2 CUNGL
        
## list licenses

list licences can use grep to filter list

    licenses
    OGL [comm, open] http:/.... Open gov licence
    CUNGL [...
    ...
    
## Problems

A list of problems is reviewed by data scientists so that redundant or problematic rules can be fixed.

TBD

# access_instructor_client

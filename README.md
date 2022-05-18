# Access instructor client lib and command line tools


Command line and library functions for the access instructor.


## add-rule

Create a rule with the given parameters:

### OPTIONS
```
    -p, --path TEXT               Path for directory rule will be applied to. [required]

    -t, --type [N|P|R|G]          Rule type. Either: No access "N", Public "P", Registered User "R" or Group "G". [required]

    -g, --group TEXT              Group name to be given access.

    -e, --expiry_date [%Y-%m-%d]  Date rule will expire on. Format: YYYY-MM-DD.

    -c, --comment TEXT            Any comments to help traceability.

    -l, --licence TEXT            Code for licence associated with this rule.

    -o, --override                Override rule will allow a group access to all subdirectories
```

### EXAMPLES
```
    $ access_instructor add-rule -p /badc/x/y -t P -l OGL
    $ access_instructor add-rule -p /badc/t -t R -e 2023-01-03
    $ access_instructor add-rule -p /badc/z/c -t G -g zdata_group -l mylicense
```


## remove-rule

Delete all rules for the give parameters:

### OPTIONS
```
    -p, --path TEXT               Path for directory rule will be applied to.

    -t, --type [N|P|R|G]          Rule type. Either: No access "N", Public "P", Registered User "R" or Group "G".

    -g, --group TEXT              Group name to be given access.

    -e, --expiry_date [%Y-%m-%d]  Date rule will expire on. Format: YYYY-MM-DD.

    -c, --comment TEXT            Any comments to help traceability.

    -l, --licence TEXT            Code for licence associated with this rule.

    -o, --override                Override rule will allow a group access to all subdirectories
```

### EXAMPLES
```
    $ access_instructor remove-rule -p /badc/x/y
    $ access_instructor add-rule -p /badc/x/y -t G -g my_group
```


## List rules

list all rules for the given parameters:

### OPTIONS
```
    -p, --path TEXT               Path for directory rule will be applied to.

    -t, --type [N|P|R|G]          Rule type. Either: No access "N", Public "P", Registered User "R" or Group "G".

    -g, --group TEXT              Group name to be given access.

    -e, --expiry_date [%Y-%m-%d]  Date rule will expire on. Format: YYYY-MM-DD.

    -c, --comment TEXT            Any comments to help traceability.

    -l, --licence TEXT            Code for licence associated with this rule.

    -o, --override                Override rule will allow a group access to all subdirectories
```

### EXAMPLES

list rules for a path:
```
    $ access_instructor list-rule -p /badc/x

    3 rules found:
        /badc/x : R : tes [expires: 2022-11-12]
        /badc/x/a : R
        /badc/x/b : G : group2
```
list rules for a path and license:
```
    $ access_instructor list-rule -l OGL -p /badc/x

    2 rules found:
        /badc/x : P : OGL 
        /badc/x/a : G : group1 : OGL [expires: 2022-11-12]
```
list rules for a license catagory:
```
    $ access_instructor list-rule -k comm -p /badc/x

    3 rules found:
        /badc/x : P : OGL
        /badc/x/a : G : group1 : OGL
        /badc/x/a : G : group2 : CUNGL
```


## list licenses

list all rules for the given parameters:

### OPTIONS
```
    -cat, --category TEXT         Licence category.
```

### EXAMPLES

list all licences:
```
    $ access_instructor list-licence

    1 licences found:
        OGL [comm, open] http:/.... Open gov licence
```
list licences for a catagory:
```
    $ access_instructor list-licence -c comm

    2 rules found:
        OGL [comm, open] http:/.... Open gov licence
        CUNGL [open] http:/.... Closed-Use Non-Comercial General Licence
```


## Problems

A list of problems is reviewed by data scientists so that redundant or problematic rules can be fixed.

TBD

# access_instructor_client

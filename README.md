A canvas CLI. Use the `-c` flag to run a command for a particular course (using the CU name)

#### Setup 

1. `pip install canvasapi`
    - https://github.com/ucfopen/canvasapi
2. You will need to set up a Canvas access token, and save the access token in an environment variable called CANVAS_TOKEN
3. You will need an .ini file for your course. There are a few ini files in this repo that you can copy and modify.
    - The ini file should be called `<courseno><S|F><year>.ini`. For instance, the ini file for the spring version of the class 2301 in 2021 is 2301S2021.ini.

###### Gspread

This tool uses gspread to integrate with Google sheets. Follow these steps to enable access for a 'service account/bot'. Be sure to share the sheet with the email in the credentials. 
- https://docs.gspread.org/en/latest/oauth2.html#enable-api-access-for-a-project 

#### Make tomorrow's class visible on Canvas 

`$py canvas_cli.py -v -c 2301 -t`

#### Make a quiz for today

`$py canvas_cli.py -quiz -c 2301 -points 3`

- To make a quiz for tomorrow, use the `-t` flag

#### Daily in-class assignment for tomorrow

`$py canvas_cli.py -assignment -c 2301 -points 3 -t`

#### Export

`$py canvas_cli.py --export -c 3402`

#### Initialize local files and canvas files

`$py canvas_cli.py -init -c 3402`

#### Semester naming conventions

S = Spring 
V = Summer (verano)
F = Fall

A canvas CLI. Use the `-c` flag to run a command for a particular course (using the CU name)

#### Make tomorrow's class visible on Canvas 

`$py canvas_cli.py -v -c 2301 -t`

#### Make a quiz for today

`$py canvas_cli.py -quiz -c 2301 -points 3 -t`

#### Daily in-class assignment

`$py canvas_cli.py -assignment -c 2301 -points 3`

#### Export

`$py canvas_cli.py --export -c 3402`

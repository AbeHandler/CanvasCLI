import sys
from jinja2 import Template

### "Show detailed recording info" on Zoom


template = '''
<ul>
<li><a href="{{link}}">{{date}}</a> (PW: {{pw}})</li>
</ul>
'''

template = Template(template)
link = None

for o in list(sys.stdin):
    if "cuboulder" in o:
        link = o.replace("\n", "")
    if "Passcode" in o:
        o = o.replace("Access Passcode", "").replace(":", "")
        pw = o 

    if "Start" in o:
        date = (o.split(":")[1].split(",")[0]).strip()


    if "Date" in o:
        date = (o.split(":")[1].split(",")[0]).strip()

print(template.render(pw=pw, link=link, date=date))

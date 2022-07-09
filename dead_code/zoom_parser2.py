import sys
from jinja2 import Template

### "Show detailed recording info" on Zoom


template = '''<li><a href="{{link}}">recording</a> (PW: {{pw}})</li>'''

template = Template(template)
link = None

c = 0
for o in sys.stdin:
    if c == 4:
        url = o
    if c == 6:
        pw = o.split(" ").pop()
    c += 1

print(template.render(pw=pw, link=url))

import sys
from jinja2 import Template

### "Show detailed recording info" on Zoom


template = '''<li><a href="{{link}}">recording</a> (PW: {{pw}})</li>'''

template = Template(template)
link = None

for o in sys.stdin:
    url, junk, pw = o.split(" ")

print(template.render(pw=pw, link=url))

import re

pattern = re.compile(r'\d{9}',re.M)
a = pattern.search("asdf123123123asdf")


print a.group()

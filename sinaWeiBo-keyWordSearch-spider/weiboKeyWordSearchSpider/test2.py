import re
import codecs

a = u'\u8f9b\u82e6\u4e86\u534a\u5e74\u7ec8\u4e8e\u8fce\u6765\u4e86\u9ad8\u6e29\u5047\U0001f34d\U0001f644\u6e29\u5047'
a = codecs.escape_decode(codecs.unicode_escape_encode(a)[0])[0]
print a
pattern = re.compile(r'\\U.{8}',re.U)
# b = pattern.sub(a,'')
b = re.sub(pattern,'',str(a))

# b = codecs.unicode_escape_decode(b)[0].encode('gbk')
b = codecs.unicode_escape_decode(b)[0]


print b
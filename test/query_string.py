

str = "NfvoId=BJ-NFVO-0&qType=pim&subeType=vimPm,vimCm,vimFm"

list1 = str.split('&')
d = {}
for i in list1:
    print i
    list2 = i.split('=')
    if len(list2) == 2:
        d[list2[0]] = list2[1]    

print d

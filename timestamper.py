
code = ""

year = 2025
month=1
day = input('day:')
for i in range(1):
    rhour = 7
    rminute = input('rminute')
    shour = 16
    sminute = input('sminute')
    code = code + '\n' + f'VALUES ("{year}-{month}-{day} {rhour}:{rminute}:00.000 -0500","{year}-{month}-{day} {shour}:{sminute}:00.000 -0500"),'

print(code)
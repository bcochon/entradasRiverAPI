import re
from datetime import datetime

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
MESES_REGEX = 'enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre'

def get_date(input: str) -> datetime:
    match = re.search(f"[1-3]?[0-9] de ({MESES_REGEX})", input.lower())
    if match:
        return format_date(match.group(), ddmmyyyy=False)
    return None

def format_date(input: str, ddmmyyyy = True) -> datetime:
    if ddmmyyyy:
        match = re.search("[0-3]?[0-9]/[0-1]?[0-9]/[0-9]{1,4}", input)
        if match:
            day, month, year = list(map(lambda s: int(s), match.group().split('/')))
            date = datetime(year, month, day)
            hourMatch = re.search("[0-2]?[0-9]([.:-][0-5][0-9])?$", input.replace(match.group(),''))
            if hourMatch:
                time = list(map(lambda s: int(s), hourMatch.group().replace(':','.').replace('-','.').split('.')))
                if(len(time) > 1):
                    date = datetime(year, month, day, time[0], time[1])
                else:
                    date = datetime(year, month, day, time[0])
            return date
    day_month = input.replace(' ','').split('de')
    if(len(day_month) < 2):
        return None
    day = int(day_month[0])
    month = MESES.index(day_month[1])+1
    year = datetime.now().year
    date = datetime(year, month, day)
    return date

def merge_lists(a: list, b: list) -> list:
    result = []
    i = 0
    while i < len(a) and i < len(b):
        result.append(a[i])
        result.append(b[i])
        i+=1
    if i == len(a):
        return result + b[i:]
    return result + a[i:]

if __name__ == '__main__':
    text = 'Domingo 02/02/2025 - 17.55'
    print(format_date(text))
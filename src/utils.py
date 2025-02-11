def find_date(input: str) -> str:
    ...

def format_date(input: str) -> str:
    ...

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
    ...
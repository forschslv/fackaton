import pandas as pd
from bs4 import BeautifulSoup

def raisee(e: BaseException):
    raise e
def get_data_by_time(tour, time):
    data = pd.DataFrame(columns=['place', 'name', 'from', 'class', '1', '2', '3', '4', 'sum'])

    with open(f"Материалы/{'Первый тур' if tour == 1 else ('Второй тур' if tour == 2 else raisee(ValueError('tour should be 1 or 2')))}/{time}.html") as f:
        text = f.read()
    soup = BeautifulSoup(text, 'html.parser')
    skip = 2
    for i in soup.find_all(name='tr'):
        if skip:
            skip -= 1
            continue
        try:
            name_from_class = i.find(name='td', attrs={'class': "party"}).text
        except Exception as e:
            print('\033[93m' + repr(e) + '\033[0m')
            continue

        name = ' '.join(name_from_class.split()[:3])
        from_ = name_from_class[name_from_class.find('(') + 1: name_from_class.find(',')]
        class_ = name_from_class[name_from_class.find(',') + 1: name_from_class.find('класс')]

        zad = []
        sm = 0
        for j in i.find_all(name='td', attrs={'class': 'ioiprob'}):
            if j.text.strip() == '.':
                zad.append(0)
            else:
                zad.append(int(j.text))
                sm += zad[-1]
        row = {'place': [i.find(name='td', attrs={'class': "rankl"}).text],
               'name': [name],
               'from': [from_],
               'class': [class_],
               '1': [zad[0]],
               '2': [zad[1]],
               '3': [zad[2]],
               '4': [zad[3]],
               'sum': [sm]}
        data = pd.concat([data,
                          pd.DataFrame(row)],
                         axis=0)
    print(data)
    return data

def render_table(tour, time):
    data = get_data_by_time(tour, time)
    table = '<table>'
    head = '<thead><tr>'
    cols = data.columns
    for i in cols:
        head += f"<th>{i}</th>"
    head += '</tr></thead>'

    body = '<tbody>'
    for irow in data.iterrows():
        row_html = '<tr>'
        for col in cols:
            row_html += f'<td>{irow[col]}</td>'
        row_html += '</tr>\n'
        body += row_html
    body += '</tbody>'
    table += head + body + '</table>'
    return table
# print(get_data_by_time(120))
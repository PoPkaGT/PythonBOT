import os

fail = 'results.txt'

if not os.path.exists(fail):
    with open(fail, 'w', encoding='utf-8') as f:
        f.write("Петерс, Ростикс, 10А, 15, 18\n")
        f.write("Шаталов, Артемий, 10А, 20, 14\n")
        f.write("Черномаз, Валера, 9В, 5, 2\n")
        f.write("Пингвинос, Каго, 1Ж, 14, 15\n")
    print(f"Файл '{fail}' создан. Заполните его данными и запустите скрипт снова.")
    exit()

uchastniki = []
with open(fail, encoding='utf-8') as f:
    for stroka in f:
        stroka = stroka.strip()
        if not stroka:
            continue
        dannye = [x.strip() for x in stroka.split(',')]
        if len(dannye) < 5:
            dannye = stroka.split()
        if len(dannye) >= 5:
            uchastniki.append({
                'familiya': dannye[0],
                'imya': dannye[1],
                'klass': dannye[2],
                'algebra': int(dannye[3]),
                'geometriya': int(dannye[4])
            })

if not uchastniki:
    print("Файл пуст. Заполните его данными и запустите снова.")
    exit()

spisok_klassov = list(set(u['klass'] for u in uchastniki))

print("Победители по параллелям (итоговой результат):")
for klass in spisok_klassov:
    klass_uchastniki = [u for u in uchastniki if u['klass'] == klass]
    max_itog = max(u['algebra'] + u['geometriya'] for u in klass_uchastniki)
    pobediteli = [u for u in klass_uchastniki if u['algebra'] + u['geometriya'] == max_itog]
    for pobeditel in pobediteli:
        print(f"Класс {klass}: {pobeditel['familiya']} {pobeditel['imya']} — Итоговый результат: {max_itog}")

max_algebra = max(u['algebra'] for u in uchastniki)
print("\nУчастники с наивысшим баллом по алгебре:")
for u in uchastniki:
    if u['algebra'] == max_algebra:
        print(f"{u['familiya']} {u['imya']}, класс {u['klass']} — Баллы по алгебре: {u['algebra']}")

max_geometriya = max(u['geometriya'] for u in uchastniki)
print("\nУчастники с наивысшим баллом по геометрии:")
for u in uchastniki:
    if u['geometriya'] == max_geometriya:
        print(f"{u['familiya']} {u['imya']}, класс {u['klass']} — Баллы по геометрии: {u['geometriya']}")
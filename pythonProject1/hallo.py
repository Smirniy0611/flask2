from flask import Flask, render_template, request, session, url_for, redirect
import openpyxl

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'  # настраиваем ключ шифрования

choice = ['Нет, не применять', 'Да, применить']


@app.route('/', methods=['POST', 'GET'])
def index():
    k1, k2 = 1, 1
    if request.method == 'POST':
        area = request.form.get('area')
        height = request.form.get('height')
        koef1 = request.form.get('koef_1')
        koef2 = request.form.get('koef_2')
        if koef1 == 'Да, применить':
            k1 = 0.8
        if koef2:
            k2 = 0.6
        results = int(area) * int(height) * k1 * k2
        return render_template('index.html',
                               the_title='Расчет площади',
                               the_area=area,
                               the_height=height,
                               the_results=results,
                               choice=choice,
                               koef_1=koef1,
                               koef_2=koef2, )

    else:
        return render_template('index.html',
                               the_title='Расчет площади',
                               the_area=0,
                               the_height=0,
                               choice=choice)


cat = ['1', '2', '3']


@app.route('/smeta', methods=['POST', 'GET'])
def smeta():
    if request.method == 'POST':
        volume = request.form.get('volume')  # объём
        height = request.form.get('height')  # высота здания
        purpose = request.form.get('purpose')  # гражданское/промышленное k1
        floor = request.form.get('floor')  # этажность (одно-/много-этажное)
        category_1 = request.form.get('category_1')  # категория сложности здания
        category_2 = request.form.get('category_2')  # сложность обмерных работ
        category_3 = request.form.get('category_3')

        k_2 = request.form.get('k_2')  # Шаг колонн и несущих стен менее 6 м. (п.2.1.9) = 1.25
        k_3 = request.form.get('k_3')  # Обмеры и обследование клёпаных конструкций (п.2.1.10) = 1.2
        k_4 = request.form.get('k_4')  # Выполнение обмерных работ с использованием имеющихся чертежей (п.2.1.12) = 0.75
        k_5 = request.form.get('k_5')  # выполнение поверочного расчета строительных конструкций не требуется (п.2.1.13) = 0.8

        k10_1 = request.form.get('k10_1')  # = 1.2
        k10_2 = request.form.get('k10_2')  # = 1.15
        k10_3 = request.form.get('k10_3')  # = 1.2
        k10_4 = request.form.get('k10_4')  # = 1.2
        k10_5 = request.form.get('k10_5')  # = 1.25
        k10_6 = request.form.get('k10_6')  # = 1.15
        k10_7 = request.form.get('k10_7')  # = 1.2
        k10_8 = request.form.get('k10_8')  # = 1.3
        k10_9 = request.form.get('k10_9')  # = 1.4
        k10_10 = request.form.get('k10_10')  # = 1.2
        k10_11 = request.form.get('k10_11')  # = 1.1
        k10_12 = request.form.get('k10_12')  # = 1.2
        k10_13 = request.form.get('k10_13')  # = 1.25
        k10_14 = request.form.get('k10_14')  # = 1.25

        k1 = 0.8 if purpose == '2' else 1  # если промышленное
        k2 = 1.25 if k_2 else 1
        k3 = 1.2 if k_3 else 1
        k4 = 0.75 if k_4 else 1  # Только для обмерных работ!
        k5 = 0.8 if k_5 else 1  # Только для обследовательских работ!

        k_obm = k1 * k2 * k3 * k4  # коэффициент для обмерных работ (без k5)
        k_obs = k1 * k2 * k3 * k5  # коэффициент для обмерных работ (без k4)

        k101 = 1.2 if k10_1 else 1
        k102 = 1.15 if k10_2 else 1
        k103 = 1.2 if k10_3 else 1
        k104 = 1.2 if k10_4 else 1
        k105 = 1.25 if k10_5 else 1
        k106 = 1.15 if k10_6 else 1
        k107 = 1.2 if k10_7 else 1
        k108 = 1.3 if k10_8 else 1
        k109 = 1.4 if k10_9 else 1
        k1010 = 1.2 if k10_10 else 1
        k1011 = 1.1 if k10_11 else 1
        k1012 = 1.2 if k10_12 else 1
        k1013 = 1.25 if k10_13 else 1
        k1014 = 1.25 if k10_14 else 1

        k10 = k101 * k102 * k103 * k104 * k105 * k106 * k107 * k108 * k109 * k1010 * k1011 * k1012 * k1013 * k1014

        book = openpyxl.open('data.xlsx', read_only=True)  # открыли файл только для чтения
        sheet = book.active  # позиционируемся на 1-ом листе
        i = 2

        tab_1 = {(1, 1): 7, (1, 2): 8, (1, 3): 9,
                 (2, 1): 11, (2, 2): 12, (2, 3): 13,
                 (3, 1): 15, (3, 2): 16, (3, 3): 17}

        tab_2 = {(1, 1): 26, (1, 2): 27, (1, 3): 28,
                 (2, 1): 30, (2, 2): 31, (2, 3): 32,
                 (3, 1): 34, (3, 2): 35, (3, 3): 36}

        tab_3 = {(1, 1): 45, (1, 2): 46, (1, 3): 47,
                 (2, 1): 49, (2, 2): 50, (2, 3): 51,
                 (3, 1): 53, (3, 2): 54, (3, 3): 55}

        tab_4 = {(1, 1): 64, (1, 2): 65, (1, 3): 66,
                 (2, 1): 68, (2, 2): 69, (2, 3): 70,
                 (3, 1): 72, (3, 2): 73, (3, 3): 74}

        if floor == '1':
            k = tab_1[int(category_1), int(category_2)]
            j = tab_3[int(category_1), int(category_3)]
        else:
            k = tab_2[int(category_1), int(category_2)]
            j = tab_4[int(category_1), int(category_3)]

        while int(height) != int(sheet[4][i].value):
            i += 1

        cost_obm = sheet[k][i].value
        cost_obsl = sheet[j][i].value

        K_inf = 4.91  # II кв. 2022 (http://www.consultant.ru/document/cons_doc_LAW_39473/)

        results_1 = round(int(volume) * 0.01 * cost_obm * K_inf * k_obm * k10, 2)  # стоимость обмерных работ
        results_2 = round(int(volume) * 0.01 * cost_obsl * K_inf * k_obs * k10, 2)  # стоимость обследовательских работ
        # round и "2" в конце - округляем до второго знака после запятой
        results_3 = round(results_1 + results_2, 2)

        book.close()

        return render_template('smeta_pir.html',
                               the_volume=volume,
                               the_height=height,
                               results_1=results_1,
                               results_2=results_2,
                               results_3=results_3,
                               the_purpose=purpose,
                               the_floor=floor,
                               cat=cat,
                               the_category_1=category_1,
                               the_category_2=category_2,
                               the_category_3=category_3,
                               k_2=k_2, k_3=k_3, k_4=k_4, k_5=k_5,
                               k10_1=k10_1, k10_2=k10_2, k10_3=k10_3, k10_4=k10_4, k10_5=k10_5, k10_6=k10_6,
                               k10_7=k10_7, k10_8=k10_8, k10_9=k10_9, k10_10=k10_10, k10_11=k10_11,
                               k10_12=k10_12, k10_13=k10_13, k10_14=k10_14, )
    else:
        return render_template('smeta_pir.html',
                               the_title='Расчет площади',
                               the_volume=0,
                               the_height=0,
                               cat=cat,
                               the_category_1='2',
                               the_category_2='2',
                               the_category_3='2',
                               results_1=0,
                               results_2=0,
                               results_3=0, )


@app.route('/user/<name>')
def user(name):
    return '<h1> Hello, %s! </h1>' % name


if __name__ == '__main__':
    app.run(debug=True)

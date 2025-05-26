from flask import Flask, render_template, request, session, url_for, redirect
from baza import *

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'  # настраиваем ключ шифрования

choice = ['Нет, не применять', 'Да, применить']
cat = ['1', '2', '3']


@app.route('/', methods=['POST', 'GET'])
def index():
    results = None
    if request.method == 'POST':
        # получаем данные из формы
        area = request.form.get('area')
        height = request.form.get('height')
        koef1 = request.form.get('koef_1')
        koef_2 = request.form.get('koef_2')


        # Сохраняем данные в сессии
        session['form_data'] = {
            'area':area,
            'height':height,
            'koef_1':koef1,
            'koef_2':koef_2,
        }
        # рассчитываем результат
        results = float(area) * float(height) * float(koef1)

        # Применяем коэфф. 0.6, если чекбокс установлен
        if koef_2:
            results *= 0.6

        # сохраняем результат в сессии
        session['results'] = results

        # Перенаправляем на ту же страницу с методом GET
        return redirect(url_for('index'))

    # Загружаем данные из сессии для предварительного заполнения
    form_data = session.get('form_data',{})
    results = session.get('results', 0)

    return render_template('index.html',
                           form_data = form_data,
                           results = results)


@app.route('/R', methods=['POST', 'GET'])
def R():
    if request.method == 'POST':
        grunt = request.form.get('grunt')  # от вида грунта зависит коэффициент Gamma_c1
        Gamma_c2 = request.form.get('Gamma_c2')  # Коэффициент для сооружений с жесткой
        # конструктивной схемой при отношении длины  сооружения или его отсека к высоте L/H
        k = request.form.get('k')  # k - коэффициент, принимаемый равным единице,
        # если прочностные характеристики грунта (фи и С) определены непосредственными испытаниями,
        # и k=1,1, если они приняты по таблицам приложения А
        fi = request.form.get('fi')  # угол внутреннего трения. От него находим My, Mq, Mc
        cII = request.form.get('cII')  # удельное сопротивление грунта, в т/м2
        b = request.form.get('b')  # ширина подошвы фундамента, м.
        yII = request.form.get('yII')  # осредненное расчетное значение удельного веса грунтов,
        # залегающих ниже подошвы фундамента, в т/м3
        y_II = request.form.get('y_II')  # осредненное расчетное значение удельного веса грунтов,
        # залегающих выше подошвы фундамента, в т/м3
        d1 = request.form.get('d1')  # глубина заложения фундамента, в м.
        db = request.form.get('db')  # глубина подвала, в м.

        G_c1 = {'1': 1.4, '2': 1.3, '3': 1.25, '4': 1.1, '5': 1.25, '6': 1.2, '7': 1.1}
        Gamma_c1 = G_c1[grunt]

        My = tab5[int(fi)][0]
        Mq = tab5[int(fi)][1]
        Mc = tab5[int(fi)][2]

        R = (Gamma_c1 * float(Gamma_c2) / float(k)) * (My * float(b) * float(yII) +
            Mq * float(d1) * float(y_II) + (Mq - 1) * float(db) * float(y_II) + Mc * float(cII))
        R = round(R, 2)  # округляем до второго знака после запятой

        return render_template('R.html',
                               the_grunt=grunt,
                               the_Gamma_c2=Gamma_c2,
                               the_k=k,
                               the_fi=fi,
                               the_cII=cII,
                               the_b=b,
                               the_yII=yII,
                               the_y_II=y_II,
                               the_d1=d1,
                               the_db=db,
                               My=My, Mq=Mq, Mc=Mc,
                               R=R,)

    else:
        return render_template('R.html',
                               the_grunt='1',
                               the_Gamma_c2='1',
                               the_k='1',
                               the_fi=0,
                               the_cII=0,
                               the_b=0,
                               the_yII=0,
                               the_y_II=0,
                               the_d1=0,
                               the_db=0,
                               My=0, Mq=0, Mc=0,
                               R=0,)

                # СМЕТА
@app.route('/smeta', methods=['POST', 'GET'])
def smeta():
    if request.method == 'POST':
        volume = request.form.get('volume')  # объём
        height = request.form.get('height')  # высота здания
        purpose = request.form.get('purpose')  # гражданское/промышленное k1
        floor = request.form.get('floor')  # этажность (одно-/много-этажное)
        category_1 = request.form.get('category_1')  # категория сложности здания
        category_2 = request.form.get('category_2')  # сложность обмерных работ
        category_3 = request.form.get('category_3')  # сложность обследовательских работ

        k_2 = request.form.get('k_2')  # Шаг колонн и несущих стен менее 6 м. (п.2.1.9) = 1.25
        k_3 = request.form.get('k_3')  # Обмеры и обследование клёпаных конструкций (п.2.1.10) = 1.2
        k_4 = request.form.get('k_4')  # Выполнение обмерных работ с использованием имеющихся чертежей (п.2.1.12) = 0.75
        k_5 = request.form.get('k_5')
        # Выполнение поверочного расчета строительных конструкций не требуется (п.2.1.13) = 0.8

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
        k2 = 1.25 if k_2 else 1  # Шаг колонн
        k3 = 1.2 if k_3 else 1  # Клёпаные конструкции
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

        if int(height) > 21:
            height = 21

        if floor == '1':
            if int(height) < 4:
                height = 4
            cost_obm = tab1[int(category_1) - 1][int(category_2) - 1][int(height) - 4]
            cost_obsl = tab3[int(category_1) - 1][int(category_3) - 1][int(height) - 4]

        else:
            if int(height) < 6:
                height = 6
            cost_obm = tab2[int(category_1) - 1][int(category_2) - 1][int(height) - 6]
            cost_obsl = tab4[int(category_1) - 1][int(category_3) - 1][int(height) - 6]

        K_inf = 5.96  # II кв. 2024 (https://www.consultant.ru/document/cons_doc_LAW_39473/)

        results_1 = round(int(volume) * 0.01 * cost_obm * K_inf * k_obm * k10, 2)  # стоимость обмерных работ
        results_2 = round(int(volume) * 0.01 * cost_obsl * K_inf * k_obs * k10, 2)  # стоимость обследовательских работ
        # round и "2" в конце - округляем до второго знака после запятой
        results_3 = round(results_1 + results_2, 2)

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

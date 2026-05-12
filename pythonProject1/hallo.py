from flask import Flask, render_template, request, session, url_for, redirect
from baza import *
import math
from smeta_project import main_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'  # настраиваем ключ шифрования

cat = ['1', '2', '3']
G_c1 = {'1': 1.4, '2': 1.3, '3': 1.25, '4': 1.1, '5': 1.25, '6': 1.2, '7': 1.1}
NDS = 1

# Регистрируем роуты в основном приложении (smeta_project)
app.register_blueprint(main_bp)


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


@app.route('/volume', methods=['POST', 'GET'])
def volume():
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
        return redirect(url_for('volume'))

    # Загружаем данные из сессии для предварительного заполнения
    form_data = session.get('form_data',{})
    results = session.get('results', 0)

    return render_template('volume.html',
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

        # Сохраняем данные в сессии
        session['form_data'] = request.form.to_dict()

        Gamma_c1 = G_c1[grunt]

        My = tab5[int(fi)][0]
        Mq = tab5[int(fi)][1]
        Mc = tab5[int(fi)][2]

        R = (Gamma_c1 * float(Gamma_c2) / float(k)) * (My * float(b) * float(yII) +
            Mq * float(d1) * float(y_II) + (Mq - 1) * float(db) * float(y_II) + Mc * float(cII))
        R = round(R, 2)  # округляем до второго знака после запятой

        session['form_data2'] = {
            'Gamma_c1':Gamma_c1,
            'My':My,
            'Mq':Mq,
            'Mc':Mc,
            'R':R,
        }

        # Перенаправляем на ту же страницу с методом GET
        return redirect(url_for('R'))

    # Загружаем данные из сессии для предварительного заполнения
    form_data = session.get('form_data', {})
    form_data2 = session.get('form_data2', {})

    return render_template('R.html',
                           form_data=form_data,
                           form_data2=form_data2,
                           )


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
        k_5 = request.form.get('k_5')  # Выполнение поверочного расчета строительных конструкций не требуется (п.2.1.13) = 0.8

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
        NDS = request.form.get('NDS')

        gvs = request.form.get('gvs')
        otopl = request.form.get('otopl')
        hvs = request.form.get('hvs')
        vent = request.form.get('vent')
        musor = request.form.get('musor')
        gas = request.form.get('gas')
        vodostok = request.form.get('vodostok')
        elektr = request.form.get('elektr')
        koef_1 = request.form.get('koef_1')

        try:
            sqare = float(request.form.get('sqare', '').replace(',', '.'))
        except (ValueError, AttributeError):
            sqare = 0

        # Сохраняем данные в сессии
        session['smeta_data_1'] = request.form.to_dict()

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
        nds = 1.22 if NDS else 1

        k10 = k101 * k102 * k103 * k104 * k105 * k106 * k107 * k108 * k109 * k1010 * k1011 * k1012 * k1013 * k1014

        height = math.ceil(float(height)) # округление в большую сторону
        volume = float(volume)

        if height > 21:
            height = 21

        if floor == '1':
            if height < 4:
                height = 4
            cost_obm = tab1[int(category_1) - 1][int(category_2) - 1][height - 4]
            cost_obsl = tab3[int(category_1) - 1][int(category_3) - 1][height - 4]

        else:
            if int(height) < 6:
                height = 6
            cost_obm = tab2[int(category_1) - 1][int(category_2) - 1][height - 6]
            cost_obsl = tab4[int(category_1) - 1][int(category_3) - 1][height - 6]

        K_inf = 7.07  # II кв. 2026 (https://www.consultant.ru/document/cons_doc_LAW_39473/)

        # коэффициент малого объёма (таблица №11)
        if volume <= 1000.0:
            kob = 4.3
        elif 1000 < volume <= 2000:
            kob = 3.5
        elif 2000 < volume <= 3000:
            kob = 2.2
        elif 3000 < volume <= 4000:
            kob = 1.8
        elif 4000 < volume <= 5000:
            kob = 1.3
        else:
            kob = 1

        # инженерные сети
        results_gvs=results_otopl=results_hvs=results_vent=results_musor=results_gas=results_vodostok=results_elektr=0
        def calculate_cost(volume, table, max_vol, base_val, step_vol, step_price):
            """
            Универсальный расчет:
            volume - текущий объем
            table - список (таблица) порогов
            max_vol - порог, после которого идет формула
            base_val - цена на пороге max_vol
            step_vol - шаг объема (например, 1000 или 5000)
            step_price - шаг цены (например, 0.2 или 1.1)
            """
            if volume <= max_vol:
                for limit, value in table:
                    if volume <= limit:
                        return value
            # Если объем больше максимального в таблице
            return base_val + ((volume - max_vol) // step_vol) * step_price

        # Общая формула для всех результатов
        def get_final_sum(c_value, volume, K_inf, k10, nds):
            return round(c_value * volume * K_inf * k10 * nds, 2)

        # Горячее водоснабжение
        if gvs:
            c_gvs = calculate_cost(volume, tab_15_1, 40000, 5.6, 1000, 0.2)
            results_gvs = get_final_sum(c_gvs, volume, K_inf, k10, nds)

        # Отопление
        if otopl:
            с_otopl = calculate_cost(volume, tab_15_2, 20000, 4.9, 5000, 0.7)
            results_otopl = get_final_sum(с_otopl, volume, K_inf, k10, nds)

        # Холодное водоснабжение
        if hvs:
            c_hvs = calculate_cost(volume, tab_15_3, 40000, 6.2, 1000, 0.3)
            results_hvs = get_final_sum(c_hvs, volume, K_inf, k10, nds)

        # Вентиляция
        if vent:
            c_vent = calculate_cost(volume, tab_15_4, 20000, 6.6, 5000, 1.1)
            results_vent = get_final_sum(c_vent, volume, K_inf, k10, nds)

        # Мусороудаление (судя по твоему коду, параметры те же, что у вентиляции)
        if musor:
            c_musor = calculate_cost(volume, tab_15_5, 20000, 6.6, 5000, 1.1)
            results_musor = get_final_sum(c_musor, volume, K_inf, k10, nds)

        # Газоснабжение
        if gas:
            c_gas = calculate_cost(volume, tab_15_6, 40000, 5.0, 1000, 0.2)
            results_gas = get_final_sum(c_gas, volume, K_inf, k10, nds)

        # Водосток
        if vodostok:
            c_vodostok = calculate_cost(volume, tab_15_7, 20000, 2.7, 1000, 0.5)
            results_vodostok = get_final_sum(c_vodostok, volume, K_inf, k10, nds)

        # Электрика
        if elektr:
            results_elektr = (sqare/ 1000) * 1200 * K_inf * k10 * nds


        results_1 = round(volume * kob * 0.01 * cost_obm * K_inf * k_obm * k10 * nds, 2)  # стоимость обмерных работ
        results_2 = round(volume * kob * 0.01 * cost_obsl * K_inf * k_obs * k10 * nds, 2)  # стоимость обследовательских работ
        results_3 = round((results_gvs + results_otopl + results_hvs + results_vent + results_musor + results_gas + results_vodostok + results_elektr) * float(koef_1), 2)   # стоимость обследования инженерных систем
        # round и "2" в конце - округляем до второго знака после запятой
        results_4 = round(results_1 + results_2 + results_3, 2)

        session['smeta_data_2'] = {
            'results_1': results_1, 'results_2': results_2, 'results_3': results_3, 'results_4': results_4
        }

        # Перенаправляем на ту же страницу с методом GET
        return redirect(url_for('smeta') + '#results') # '#results' - отправляет вниз на якорь id="results"

    # Загружаем данные из сессии для предварительного заполнения
    smeta_data_1 = session.get('smeta_data_1', {})
    smeta_data_2 = session.get('smeta_data_2', {})

    return render_template('smeta_pir.html',
                           smeta_data_1 = smeta_data_1,
                           smeta_data_2 = smeta_data_2,
                           cat = cat
                           )



@app.route('/user/<name>')
def user(name):
    return '<h1> Hello, %s! </h1>' % name


if __name__ == '__main__':
    app.run(debug=True)

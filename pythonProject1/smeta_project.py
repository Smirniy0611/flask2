from flask import Blueprint, request, session, url_for, redirect, render_template
from baza import tab_project, tab_project_2


main_bp = Blueprint('main', __name__)


@main_bp.route('/smeta_project', methods=['POST', 'GET'])
def smeta_project():
    all_categories = list(tab_project.keys())
    form_data = session.get('form_data', {})

    # берем категорию из аргументов GET (для нашего JS/HTMX)
    current_cat = request.args.get('object') or form_data.get('object')
    if not current_cat:
        current_cat = all_categories[0]  # Если пусто, берем первую

    items = tab_project.get(current_cat, [])


    # Если запрос от нашего JS (имитируем HTMX)
    if request.headers.get('HX-Request'):
        # Генерируем только опции
        options_html = ""
        for item in items:
            options_html += f'<option value="{item["id"]}" data-unit="{item["unit"]}">{item["name"]}</option>'
        return options_html  # Возвращаем строку с опциями

    if request.method == 'POST':
        selected_id_str = request.form.get('object_tip')
        volume = request.form.get('volume')
        k10_1 = request.form.get('k10_1')  # = 1.2
        k10_2 = request.form.get('k10_2')  # = 1.25
        k10_3 = request.form.get('k10_3')  # = 1.2
        k10_4 = request.form.get('k10_4')  # = 1.1
        k10_5 = request.form.get('k10_5')  # = 1.2
        k10_6 = request.form.get('k10_6')  # = 1.25
        NDS = request.form.get('NDS')

        # Сохраняем данные в сессии
        session['form_data'] = request.form.to_dict()

        k101 = 1.2 if k10_1 else 1
        k102 = 1.25 if k10_2 else 1
        k103 = 1.2 if k10_3 else 1
        k104 = 1.1 if k10_4 else 1
        k105 = 1.2 if k10_5 else 1
        k106 = 1.25 if k10_6 else 1

        nds = 1.22 if NDS else 1

        k10 = k101 * k102 * k103 * k104 * k105 * k106

        volume = float(volume)
        selected_id = int(selected_id_str)
        a = tab_project_2.get(selected_id)[0]
        b = tab_project_2.get(selected_id)[1]
        results = round((a + b * volume) * k10 * nds, 2)  # volume * kob * 0.01 * cost_obm * K_inf * k_obm * k10 * nds

        session['form_data_2'] = {
            'results': results
        }


        return redirect(url_for('main.smeta_project'))

    # Загружаем данные из сессии для предварительного заполнения
    form_data = session.get('form_data', {})
    form_data_2 = session.get('form_data_2', 0)


    return render_template('smeta_project.html',
                           categories=all_categories,
                           items=items,
                           form_data=form_data,
                           form_data_2=form_data_2
                           )


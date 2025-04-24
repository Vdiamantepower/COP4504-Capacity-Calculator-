from flask import Flask, render_template, request
import sqlite3
from flask import send_file
import openpyxl
from io import BytesIO

app = Flask(__name__)


# History Route

@app.route('/history')
def history():
    connection = sqlite3.connect('pi_capacity.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id, pi_name, sprint_1, sprint_2, sprint_3, sprint_4, sprint_5, total_capacity FROM pi_results')
    results = cursor.fetchall()

    connection.close()
    return render_template('history.html', results=results, request=request)




# Home Route

@app.route('/', methods=['GET', 'POST'])
def home():
    sprint_capacity = []
    total_pi_capacity = None

    if request.method == 'POST':
        pi_name = request.form.get("pi_name", "Unnamed PI")
        action = request.form.get("action")

        if action == "clear":
            return render_template("index.html", sprint_capacity=None, total_pi_capacity=None, pi_name=None)

        try:
            num_devs = int(request.form.get('num_devs'))
            avg_story_points = int(request.form.get('avg_story_points'))
            unplanned_days_total = int(request.form.get('unplanned_days_total', 0))
            unplanned_per_sprint = unplanned_days_total / 5

            for i in range(1, 6):
                holidays = int(request.form.get(f'holidays_s{i}', 0))
                adjusted_per_dev = avg_story_points - (avg_story_points * 0.10 * holidays)
                sprint_capacity_points = 0

                for d in range(1, num_devs + 1):
                    pto_days = int(request.form.get(f'pto_s{i}_d{d}', 0))
                    dev_capacity = adjusted_per_dev - (adjusted_per_dev * 0.10 * pto_days)
                    sprint_capacity_points += dev_capacity

                sprint_capacity_points -= sprint_capacity_points * 0.10 * unplanned_per_sprint
                sprint_capacity.append(round(sprint_capacity_points, 2))

            total_pi_capacity = round(sum(sprint_capacity), 2)

            connection = sqlite3.connect('pi_capacity.db')
            cursor = connection.cursor()

            cursor.execute('''
                INSERT INTO pi_results (pi_name, sprint_1, sprint_2, sprint_3, sprint_4, sprint_5, total_capacity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                pi_name,
                sprint_capacity[0],
                sprint_capacity[1],
                sprint_capacity[2],
                sprint_capacity[3],
                sprint_capacity[4],
                total_pi_capacity
            ))

            connection.commit()
            connection.close()
            save_success = True

        except Exception as e:
            return render_template("index.html", sprint_capacity=None, total_pi_capacity=None, error=str(e), pi_name=pi_name)

    return render_template("index.html",sprint_capacity=sprint_capacity if sprint_capacity else None,total_pi_capacity=total_pi_capacity,pi_name=pi_name if request.method == 'POST' else None,save_success=locals().get('save_success', False), request=request
)







if __name__ == '__main__':
    app.run(debug=True, port=5001)

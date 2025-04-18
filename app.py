from flask import Flask, render_template, request

app = Flask(__name__)  
@app.route('/', methods=['GET', 'POST'])
def home():
    sprint_capacity= []
    total_pi_capacity = None

    if request.method == 'POST':
        action = request.form.get("action")
        if action == "clear":
            return render_template("index.html", sprint_capacity=None, total_pi_capacity=None)

        try:
            # Global Inputs
            num_devs = int(request.form.get('num_devs'))
            avg_story_points = int(request.form.get('avg_story_points'))
            unplanned_days_total = int(request.form.get('unplanned_days_total', 0))
            
            # Calculate unplanned impact per sprint
            unplanned_per_sprint = unplanned_days_total / 5

            for i in range(1, 6):  # 5 sprints
                holidays = int(request.form.get(f'holidays_s{i}', 0))

                # Adjust capacity per dev based on holidays
                adjusted_per_dev = avg_story_points- (avg_story_points * 0.10 * holidays)

                sprint_capacity_points	 = 0
                for d in range(1, num_devs + 1):
                    pto_days = int(request.form.get(f'pto_s{i}_d{d}', 0))
                    dev_capacity = adjusted_per_dev - (adjusted_per_dev * 0.10 * pto_days)
                    sprint_capacity_points	+= dev_capacity

                # Apply unplanned time off
                sprint_capacity_points	-= sprint_capacity_points	* 0.10 * unplanned_per_sprint

                sprint_capacity.append(round(sprint_capacity_points	, 2))

            total_pi_capacity = round(sum(sprint_capacity), 2)

        except Exception as e:
            return render_template("index.html", sprint_capacity=None, total_pi_capacity=None, error=str(e))

    return render_template("index.html", sprint_capacity=sprint_capacity if sprint_capacity else None, total_pi_capacity=total_pi_capacity)

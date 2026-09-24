from flask import Flask, render_template, request, redirect
from database import get_db_connection, create_database

app = Flask(__name__)

# Create database and tables
create_database()



# DASHBOARD


@app.route("/")
def home():

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM student ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if not student:
        connection.close()
        return render_template("profile.html")

    # Get activities
    activities = connection.execute(
        """
        SELECT * FROM activity
        WHERE student_id = ?
        ORDER BY id DESC
        """,
        (student["id"],)
    ).fetchall()

    # Get goals
    goals = connection.execute(
        """
        SELECT * FROM goals
        WHERE student_id = ?
        ORDER BY id DESC
        """,
        (student["id"],)
    ).fetchall()

    connection.close()


    
    # BASIC STATISTICS
    

    total_minutes = sum(
        activity["duration"]
        for activity in activities
    )

    total_hours = round(total_minutes / 60, 2)

    activity_count = len(activities)


    
    # LEARNING SCORE - 40 POINTS
    

    learning_score = min(
        40,
        (total_minutes / 600) * 40
    )


    
    # ACTIVITY SCORE - 20 POINTS
    

    activity_score = min(
        20,
        activity_count * 2
    )


    
    # CONSISTENCY SCORE - 20 POINTS
    

    unique_days = len(
        set(
            activity["activity_date"]
            for activity in activities
        )
    )

    consistency_score = min(
        20,
        unique_days * 2
    )


    
    # GOAL SCORE - 20 POINTS
    

    goal_score = 0
    average_goal_progress = 0

    if goals:

        total_progress = sum(
            goal["progress"]
            for goal in goals
        )

        average_goal_progress = round(
            total_progress / len(goals)
        )

        goal_score = round(
            average_goal_progress * 0.20
        )


    
    # DIGITAL TWIN SCORE
    

    score = round(
        learning_score
        + activity_score
        + consistency_score
        + goal_score
    )

    score = min(100, score)

    # AI-LIKE RECOMMENDATIONS

    recommendations = []


    if total_minutes < 300:

        recommendations.append(
            "Increase your learning time to at least 5 hours per week."
        )


    if activity_count < 5:

        recommendations.append(
            "Try to record at least 5 learning activities."
        )


    if unique_days < 5:

        recommendations.append(
            "Maintain a consistent learning schedule throughout the week."
        )


    if not student["skills"]:

        recommendations.append(
            "Add your technical skills to improve your Digital Twin profile."
        )


    if not goals:

        recommendations.append(
            "Create at least one career or learning goal."
        )


    if goals and average_goal_progress < 50:

        recommendations.append(
            "Your goal progress is below 50%. Focus on completing your active goals."
        )


    if goals and average_goal_progress >= 80:

        recommendations.append(
            "Excellent goal progress! You are close to achieving your targets."
        )


    if not recommendations:

        recommendations.append(
            "Excellent progress! Keep maintaining your current learning consistency."
        )


    return render_template(
        "dashboard.html",
        student=student,
        activities=activities,
        goals=goals,
        total_minutes=total_minutes,
        total_hours=total_hours,
        activity_count=activity_count,
        score=score,
        recommendations=recommendations,
        average_goal_progress=average_goal_progress
    )



# PROFILE


@app.route("/profile")
def profile():

    return render_template("profile.html")



# SAVE PROFILE


@app.route("/save-profile", methods=["POST"])
def save_profile():

    name = request.form["name"]
    email = request.form["email"]
    course = request.form["course"]
    skills = request.form["skills"]
    goals_text = request.form["goals"]

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO student
        (name, email, course, skills, goals)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            email,
            course,
            skills,
            goals_text
        )
    )

    connection.commit()
    connection.close()

    return redirect("/")



# ACTIVITY PAGE


@app.route("/activity")
def activity():

    return render_template("activity.html")



# SAVE ACTIVITY


@app.route("/save-activity", methods=["POST"])
def save_activity():

    activity_name = request.form["activity_name"]
    duration = request.form["duration"]
    activity_date = request.form["activity_date"]

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM student ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if student:

        connection.execute(
            """
            INSERT INTO activity
            (student_id, activity_name, duration, activity_date)
            VALUES (?, ?, ?, ?)
            """,
            (
                student["id"],
                activity_name,
                duration,
                activity_date
            )
        )

        connection.commit()

    connection.close()

    return redirect("/")



# ANALYTICS

@app.route("/analytics")
def analytics():

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM student ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if not student:

        connection.close()

        return redirect("/")


    activities = connection.execute(
        """
        SELECT * FROM activity
        WHERE student_id = ?
        ORDER BY activity_date
        """,
        (student["id"],)
    ).fetchall()


    # Get goals
    goals = connection.execute(
        """
        SELECT * FROM goals
        WHERE student_id = ?
        ORDER BY id DESC
        """,
        (student["id"],)
    ).fetchall()


    connection.close()


    # ACTIVITY STATISTICS

    total_minutes = sum(
        activity["duration"]
        for activity in activities
    )

    activity_count = len(activities)

    average_duration = 0

    if activity_count > 0:

        average_duration = round(
            total_minutes / activity_count,
            2
        )


    # GOAL STATISTICS

    average_goal_progress = 0

    if goals:

        total_progress = sum(
            goal["progress"]
            for goal in goals
        )

        average_goal_progress = round(
            total_progress / len(goals)
        )


    # CHART DATA

    activity_names = [
        activity["activity_name"]
        for activity in activities
    ]

    activity_durations = [
        activity["duration"]
        for activity in activities
    ]


    return render_template(
        "analytics.html",
        student=student,
        total_minutes=total_minutes,
        activity_count=activity_count,
        average_duration=average_duration,
        activity_names=activity_names,
        activity_durations=activity_durations,
        goals=goals,
        average_goal_progress=average_goal_progress
    )


# GOALS PAGE

@app.route("/goals")
def goals():

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM student ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if not student:

        connection.close()

        return redirect("/")


    goals = connection.execute(
        """
        SELECT * FROM goals
        WHERE student_id = ?
        ORDER BY id DESC
        """,
        (student["id"],)
    ).fetchall()


    connection.close()


    return render_template(
        "goals.html",
        student=student,
        goals=goals
    )


# SAVE GOAL

@app.route("/save-goal", methods=["POST"])
def save_goal():

    goal_name = request.form["goal_name"]
    target = request.form["target"]


    connection = get_db_connection()


    student = connection.execute(
        "SELECT * FROM student ORDER BY id DESC LIMIT 1"
    ).fetchone()


    if student:

        connection.execute(
            """
            INSERT INTO goals
            (student_id, goal_name, target, progress)
            VALUES (?, ?, ?, ?)
            """,
            (
                student["id"],
                goal_name,
                target,
                0
            )
        )

        connection.commit()


    connection.close()


    return redirect("/goals")


# UPDATE GOAL PROGRESS

@app.route("/update-goal/<int:goal_id>", methods=["POST"])
def update_goal(goal_id):

    progress = int(
        request.form["progress"]
    )


    # Keep progress between 0 and 100

    progress = max(
        0,
        min(100, progress)
    )


    connection = get_db_connection()


    connection.execute(
        """
        UPDATE goals
        SET progress = ?
        WHERE id = ?
        """,
        (
            progress,
            goal_id
        )
    )


    connection.commit()
    connection.close()


    return redirect("/goals")


# RUN APPLICATION

if __name__ == "__main__":

    app.run(debug=True)
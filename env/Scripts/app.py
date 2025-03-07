import mysql.connector
import pandas as pd
import streamlit as st
import logging

logging.basicConfig(level=logging.INFO)

class DatabaseConnection:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "MySQL!Secure#1234"
        self.database = "placement_eligibility"
        self.conn = None
        self.cursor = None

    def open_connection(self):
        logging.info("Opening database connection...")
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def close_connection(self):
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")

    def fetch_data(self, query, params=()):
        logging.info(f"Executing query: {query} with params: {params}")
        self.open_connection()
        self.cursor.execute(query, params)
        result = self.cursor.fetchall()
        self.close_connection()
        return pd.DataFrame(result)

class StreamlitApp:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def display_all_students(self):
        query = "SELECT name, age, city, email, phone, enrollment_year FROM students LIMIT 500;"
        df = self.db_connection.fetch_data(query)
        st.subheader("All Student Data")
        if not df.empty:
            st.dataframe(df, height=500)
        else:
            st.warning("No student data found.")

    def filter_eligible_students(self, problems_min, skills_min, age_min, city_filter, placement_status_filter):
        query_eligible = '''
        SELECT s.student_id, s.name, s.age, p.problems_solved, ss.communication, pl.placement_status, s.city
        FROM students s
        JOIN programming p ON s.student_id = p.student_id
        JOIN soft_skills ss ON s.student_id = ss.student_id
        JOIN placements pl ON s.student_id = pl.student_id
        WHERE p.problems_solved >= %s AND ss.communication >= %s
        AND s.age >= %s AND (s.city = %s OR %s = 'All') AND pl.placement_status = %s;
        '''
        eligible_students = self.db_connection.fetch_data(
            query_eligible, 
            params=(problems_min, skills_min, age_min, city_filter, city_filter, placement_status_filter)
        )
        st.subheader("Eligible Students Based on Your Criteria")
        if not eligible_students.empty:
            st.write(eligible_students)
            return eligible_students
        else:
            st.warning("No students match the given criteria.")
            return pd.DataFrame()

    def display_student_details(self, student_id):
        student_query = '''
        SELECT s.name, s.age, s.email, s.phone, s.city, p.language, p.problems_solved, p.assessments_completed, 
        ss.communication, ss.teamwork, ss.presentation, pl.placement_status, pl.company_name, pl.placement_package
        FROM students s
        JOIN programming p ON s.student_id = p.student_id
        JOIN soft_skills ss ON s.student_id = ss.student_id
        JOIN placements pl ON s.student_id = pl.student_id
        WHERE s.student_id = %s;
        '''
        student_details = self.db_connection.fetch_data(student_query, params=(student_id,))
        if not student_details.empty:
            student = student_details.iloc[0]  # Get the first row (only one student expected)
            st.subheader(f"Details for {student['name']}")
            st.write(student)
        else:
            st.warning(f"No details found for student ID {student_id}.")

    def display_avg_programming_performance(self):
        query_avg_programming = '''
        SELECT course_batch, AVG(problems_solved) AS avg_problems_solved, AVG(assessments_completed) AS avg_assessments_completed
        FROM programming p
        JOIN students s ON p.student_id = s.student_id
        GROUP BY course_batch;
        '''
        avg_programming_data = self.db_connection.fetch_data(query_avg_programming)
        st.subheader("Average Programming Performance per Batch")
        if not avg_programming_data.empty:
            st.write(avg_programming_data)
        else:
            st.warning("No data available for programming performance.")

    def display_top_5_students_for_placement(self):
        query_top_students = '''
        SELECT s.student_id, s.name, p.problems_solved, ss.communication, pl.placement_status 
        FROM students s
        JOIN programming p ON s.student_id = p.student_id
        JOIN soft_skills ss ON s.student_id = ss.student_id
        JOIN placements pl ON s.student_id = pl.student_id
        WHERE pl.placement_status = 'Ready'
        ORDER BY p.problems_solved DESC, ss.communication DESC
        LIMIT 5;
        '''
        top_students = self.db_connection.fetch_data(query_top_students)
        st.subheader("Top 5 Students Ready for Placement")
        if not top_students.empty:
            st.write(top_students)
        else:
            st.warning("No data available for top students.")

    def display_soft_skills_distribution(self):
        query_soft_skills = '''
        SELECT communication, COUNT(*) AS count
        FROM soft_skills
        GROUP BY communication
        ORDER BY communication;
        '''
        soft_skills_distribution = self.db_connection.fetch_data(query_soft_skills)
        st.subheader("Distribution of Soft Skills Scores")
        if not soft_skills_distribution.empty:
            st.write(soft_skills_distribution)
        else:
            st.warning("No soft skills data available.")

    def display_avg_placement_package_per_batch(self):
        query_avg_package = '''
        SELECT course_batch, AVG(placement_package) AS avg_placement_package
        FROM students s
        JOIN placements pl ON s.student_id = pl.student_id
        GROUP BY course_batch;
        '''
        avg_package_data = self.db_connection.fetch_data(query_avg_package)
        st.subheader("Average Placement Package per Batch")
        if not avg_package_data.empty:
            st.write(avg_package_data)
        else:
            st.warning("No placement package data available.")

    def display_count_of_students_by_placement_status(self):
        query_placement_status = '''
        SELECT pl.placement_status, COUNT(*) AS count
        FROM students s
        JOIN placements pl ON s.student_id = pl.student_id
        GROUP BY pl.placement_status;
        '''
        placement_status_data = self.db_connection.fetch_data(query_placement_status)
        st.subheader("Count of Students by Placement Status")
        if not placement_status_data.empty:
            st.write(placement_status_data)
        else:
            st.warning("No placement status data available.")

    def display_top_10_students_by_communication(self):
        query_top_communication = '''
        SELECT s.student_id, s.name, ss.communication
        FROM students s
        JOIN soft_skills ss ON s.student_id = ss.student_id
        ORDER BY ss.communication DESC
        LIMIT 10;
        '''
        top_communication = self.db_connection.fetch_data(query_top_communication)
        st.subheader("Top 10 Students by Soft Skills Communication")
        if not top_communication.empty:
            st.write(top_communication)
        else:
            st.warning("No data available for top communication students.")

    def display_students_with_more_than_50_problems(self):
        query_more_than_50 = '''
        SELECT COUNT(*) AS count
        FROM students s
        JOIN programming p ON s.student_id = p.student_id
        WHERE p.problems_solved > 50;
        '''
        students_more_than_50 = self.db_connection.fetch_data(query_more_than_50)
        st.subheader("Students Who Solved More Than 50 Problems")
        if not students_more_than_50.empty:
            st.write(students_more_than_50)
        else:
            st.warning("No students with more than 50 problems solved.")

    def display_avg_age_by_placement_status(self):
        query_avg_age = '''
        SELECT pl.placement_status, AVG(s.age) AS avg_age
        FROM students s
        JOIN placements pl ON s.student_id = pl.student_id
        GROUP BY pl.placement_status;
        '''
        avg_age_data = self.db_connection.fetch_data(query_avg_age)
        st.subheader("Average Age by Placement Status")
        if not avg_age_data.empty:
            st.write(avg_age_data)
        else:
            st.warning("No data available for average age by placement status.")

    def display_students_by_city(self):
        query_by_city = '''
        SELECT s.city, COUNT(*) AS student_count
        FROM students s
        GROUP BY s.city
        ORDER BY student_count DESC;
        '''
        students_by_city = self.db_connection.fetch_data(query_by_city)
        st.subheader("Number of Students by City")
        if not students_by_city.empty:
            st.write(students_by_city)
        else:
            st.warning("No data available for students by city.")

# Main function to run the Streamlit app
def main():
    db_connection = DatabaseConnection()
    
    app = StreamlitApp(db_connection)

    st.markdown("<h1 style='color: red;'>Student Placement Eligibility Insights</h1>", unsafe_allow_html=True)

    st.sidebar.header("Select a Query to display")
    query_choice = st.sidebar.selectbox(
        "Choose the query:",
        [
            "Display All Students",
            "Filter Eligible Students",
            "Average Programming Performance per Batch",
            "Top 5 Students Ready for Placement",
            "Soft Skills Distribution",
            "Average Placement Package per Batch",
            "Count of Students by Placement Status",
            "Top 10 Students by Communication",
            "Students Who Solved More Than 50 Problems",
            "Average Age by Placement Status",
            "Number of Students by City"
        ]
    )

    if query_choice == "Display All Students":
        app.display_all_students()

    if query_choice == "Filter Eligible Students":
        problems_min = st.sidebar.slider("Minimum Problems Solved", 0, 100, 50)
        skills_min = st.sidebar.slider("Minimum Communication Skills (Out of 100)", 0, 100, 75)
        age_min = st.sidebar.slider("Minimum Age", 18, 40, 21)
        city_filter = st.sidebar.selectbox("Select City", ["All", "City1", "City2", "City3"])
        placement_status_filter = st.sidebar.selectbox("Select Placement Status", ["Ready", "Not Ready"])
        
        eligible_students_df = app.filter_eligible_students(
            problems_min, skills_min, age_min, city_filter, placement_status_filter
        )
        if not eligible_students_df.empty:
            student_id = st.selectbox("Select a student to view detailed information", eligible_students_df['student_id'])
            if student_id:
                app.display_student_details(student_id)

    if query_choice == "Average Programming Performance per Batch":
        app.display_avg_programming_performance()

    if query_choice == "Top 5 Students Ready for Placement":
        app.display_top_5_students_for_placement()

    if query_choice == "Soft Skills Distribution":
        app.display_soft_skills_distribution()

    if query_choice == "Average Placement Package per Batch":
        app.display_avg_placement_package_per_batch()

    if query_choice == "Count of Students by Placement Status":
        app.display_count_of_students_by_placement_status()

    if query_choice == "Top 10 Students by Communication":
        app.display_top_10_students_by_communication()

    if query_choice == "Students Who Solved More Than 50 Problems":
        app.display_students_with_more_than_50_problems()

    if query_choice == "Average Age by Placement Status":
        app.display_avg_age_by_placement_status()

    if query_choice == "Number of Students by City":
        app.display_students_by_city()

if __name__ == "__main__":
    main()

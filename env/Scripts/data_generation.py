import mysql.connector
import faker

fake = faker.Faker()

try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="MySQL!Secure#1234",
        database="placement_eligibility"
    )
    print("Database connected successfully!")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit()

cursor = conn.cursor()

try:
    for _ in range(50):  
        student_id = fake.uuid4() 
        phone = fake.phone_number()[:20]  

        cursor.execute('''INSERT INTO students (student_id, name, age, gender, email, phone, enrollment_year, course_batch, city, graduation_year)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (
            student_id,
            fake.name(),
            fake.random_int(18, 25),
            fake.random_element(['Male', 'Female', 'Other']),
            fake.email(),
            phone,
            fake.random_int(2018, 2022),
            fake.random_element(['A', 'B', 'C']),
            fake.city(),
            fake.random_int(2023, 2025)
        ))

        cursor.execute('''INSERT INTO programming (programming_id, student_id, language, problems_solved, assessments_completed, mini_projects, certifications_earned, latest_project_score)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (
            fake.uuid4(),
            student_id,
            fake.random_element(['Python', 'SQL', 'JavaScript']),
            fake.random_int(30, 100),
            fake.random_int(5, 10),
            fake.random_int(1, 5),
            fake.random_int(0, 3),
            fake.random_int(50, 100)
        ))

        cursor.execute('''INSERT INTO soft_skills (soft_skill_id, student_id, communication, teamwork, presentation, leadership, critical_thinking, interpersonal_skills)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (
            fake.uuid4(),
            student_id,
            fake.random_int(50, 100),
            fake.random_int(50, 100),
            fake.random_int(50, 100),
            fake.random_int(50, 100),
            fake.random_int(50, 100),
            fake.random_int(50, 100)
        ))

        cursor.execute('''INSERT INTO placements (placement_id, student_id, mock_interview_score, internships_completed, placement_status, company_name, placement_package, interview_rounds_cleared, placement_date)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', (
            fake.uuid4(),
            student_id,
            fake.random_int(50, 100),
            fake.random_int(0, 3),
            fake.random_element(['Ready', 'Not Ready', 'Placed']),
            fake.company(),
            fake.random_int(30000, 100000),
            fake.random_int(1, 5),
            fake.date_this_decade()
        ))

    conn.commit()
    print("Data inserted and committed successfully!")

except mysql.connector.Error as err:
    print(f"Error during insert: {err}")
    conn.rollback() 

finally:
    conn.close()

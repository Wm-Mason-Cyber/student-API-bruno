from fastapi import FastAPI, HTTPException, Response, status, Header
from pydantic import BaseModel
from typing import List, Optional

# --- This is the hardcoded, secret API key for our server ---
API_KEY = "bruno-is-awesome"

app = FastAPI()

# --- Pydantic Models for Data Validation ---
# This ensures data is in the correct format

class StudentBase(BaseModel):
    name: str

class Student(StudentBase):
    id: int

# --- In-Memory "Database" ---
# This is our "database" -- a simple list in memory.
students_db = [
    Student(id=1, name="Ada Lovelace"),
    Student(id=2, name="Grace Hopper")
]
# A counter to make sure new student IDs are unique
next_id = 3

@app.get("/")
def home():
    # A simple welcome message for the root URL
    return {"message": "Welcome to the Student API! Visit /students to see the data or /docs for API info."}

# --- CRUD Operations ---

# CREATE: Add a new student
@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED)
def add_student(student_in: StudentBase):
    global next_id

    student = Student(
        id=next_id,
        name=student_in.name
    )

    students_db.append(student)
    next_id += 1

    # Return the new student's data
    return student

# READ: Get all students
@app.get("/students", response_model=List[Student])
def get_students():
    return students_db

# READ: Get a single student by ID
@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    # Find the student with the matching ID
    for student in students_db:
        if student.id == student_id:
            return student

    # If no student is found, raise a 404 "Not Found" error
    raise HTTPException(status_code=404, detail="Student not found")

# UPDATE: Modify an existing student
@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student_update: StudentBase):
    for student in students_db:
        if student.id == student_id:
            student.name = student_update.name
            return student

    # If no student is found, raise a 404
    raise HTTPException(status_code=404, detail="Student not found")

# DELETE: Remove a student
@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(student_id: int):
    global students_db

    student_found = any(s.id == student_id for s in students_db)

    if student_found:
        # Create a new list *without* the deleted student
        students_db = [s for s in students_db if s.id != student_id]
        return {"message": f"Student with id {student_id} deleted."}
    else:
        # If no student is found, raise a 404
        raise HTTPException(status_code=404, detail="Student not found")

# A secured endpoint that requires an API key
@app.get("/admin-only")
def get_admin_data(x_api_key: str = Header(None)):
    """
    Provides secret admin data, but only if a valid
    X-API-Key header is provided.
    """
    # 1. FastAPI's Header(None) gives us the header value or None

    # 2. Check if the key is missing or incorrect
    if not x_api_key or x_api_key != API_KEY:
        # 3. If so, raise a 403 Forbidden error
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )

    # 4. If the key is correct, send the secret data
    return {"message": "You found the secret admin data!"}

# Note: Unlike Flask, you don't run this file directly with `python3`.
# Instead, you run it with Uvicorn:
# uvicorn fastapi_server:app --host 0.0.0.0 --port 5000 --reload

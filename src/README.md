# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements`                                                  | List announcements currently within their date range                |
| GET    | `/announcements/manage`                                           | List all announcements (teacher session required)                    |
| POST   | `/announcements`                                                  | Create an announcement (teacher session required)                    |
| PUT    | `/announcements/{announcement_id}`                                | Update an announcement (teacher session required)                    |
| DELETE | `/announcements/{announcement_id}`                                | Delete an announcement (teacher session required)                    |
| POST   | `/auth/login?username=...&password=...`                           | Sign in and receive a bearer session token                           |

Send the token returned by `/auth/login` in the `Authorization: Bearer <token>` header for protected endpoints. An announcement body must include `message` and an ISO-8601 `expiration_date`; `start_date` is optional.

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.

# Django Scheduler API

A Django REST API for managing user weekly availability and guest bookings. Features include:
- Users set their weekly availability.
- Guests can book time slots (15m, 30m, 45m, 1hr) based on availability.
- Bookings do not overlap and only fit within available schedules.
- All endpoints are documented with Swagger and Redoc.
- SQLite database, Django REST Framework, and unit tests included.

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install django djangorestframework drf-yasg
   ```
2. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
3. **Create a superuser (optional, for admin access):**
   ```bash
   python manage.py createsuperuser
   ```
4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
5. **Access the API documentation:**
   - Swagger UI: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
   - Redoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

## API Endpoints

### 1. Weekly Availability

#### `GET /api/availability/`
- **Description:** List all weekly availability slots. Supports filtering by user.
- **Query Params:**
  - `user` (optional): User ID to filter availabilities.
- **Authentication:** Not required for GET.
- **Example Response:**
  ```json
  [
    {
      "id": 1,
      "user": 2,
      "weekday": 0,
      "start_time": "09:00:00",
      "end_time": "12:00:00"
    }
  ]
  ```

#### `POST /api/availability/`
- **Description:** Create a new availability slot for the authenticated user.
- **Body:**
  - `weekday`: Integer (0=Monday, ..., 6=Sunday)
  - `start_time`: HH:MM (24h)
  - `end_time`: HH:MM (24h)
- **Authentication:** Required.
- **Notes:**
  - No overlapping slots allowed for the same user and weekday.

#### `PUT /api/availability/{id}/`
- **Description:** Update an existing availability slot.
- **Authentication:** Required (owner only).

#### `DELETE /api/availability/{id}/`
- **Description:** Delete an availability slot.
- **Authentication:** Required (owner only).

---

### 2. Bookings

#### `GET /api/bookings/`
- **Description:** List all bookings.
- **Authentication:** Not required.

#### `POST /api/bookings/`
- **Description:** Book a time slot as a guest.
- **Body:**
  - `availability`: ID of the WeeklyAvailability slot
  - `guest_name`: Name of the guest
  - `date`: Date of booking (YYYY-MM-DD)
  - `start_time`: Start time (HH:MM)
  - `end_time`: End time (HH:MM)
  - `duration`: Duration in minutes (15, 30, 45, 60)
- **Notes:**
  - Booking must fit within the availability slot.
  - No overlapping bookings allowed.
  - End time must match start time + duration.

#### `GET /api/bookings/available-slots/?user={user_id}&weekday={weekday}&date={YYYY-MM-DD}&duration={minutes}`
- **Description:** List all available slots for a user on a specific weekday and date, for a given duration.
- **Query Params:**
  - `user`: User ID
  - `weekday`: Integer (0=Monday, ..., 6=Sunday)
  - `date`: Date (YYYY-MM-DD)
  - `duration`: Duration in minutes (default 15)
- **Example Response:**
  ```json
  [
    {
      "availability_id": 1,
      "start_time": "10:00:00",
      "end_time": "10:30:00",
      "duration": 30
    }
  ]
  ```
- **Notes:**
  - Returns all possible non-overlapping slots of the requested duration.
  - Steps through the availability in 15-minute increments.

---

### 3. Admin Panel
- **URL:** `/admin/`
- **Description:** Manage users, availabilities, and bookings via Django admin.
- **Authentication:** Superuser required.

---

## Authentication
- Use Django's default authentication for user-related endpoints (login, set availability, etc.).
- Bookings can be made by guests (no authentication required).

## API Documentation
- **Swagger UI:** `/swagger/`
- **Redoc:** `/redoc/`
- Interactive documentation for all endpoints, schemas, and parameters.

## Running Tests
```bash
python manage.py test
```

## Notes
- All time values use 24-hour format.
- Bookings and availabilities are validated to prevent overlaps.
- The project uses SQLite by default for easy setup.

## Example Usage
1. **Set Availability (as a user):**
   - POST `/api/availability/` with your weekday and time range.
2. **Find Available Slots (as a guest):**
   - GET `/api/bookings/available-slots/?user=1&weekday=0&date=2024-07-01&duration=30`
3. **Book a Slot (as a guest):**
   - POST `/api/bookings/` with the slot info from the previous step.

---

For any questions, see the Swagger docs or contact the project maintainer. 
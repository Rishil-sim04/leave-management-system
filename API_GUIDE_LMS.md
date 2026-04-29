# Register :- 

curl --location 'http://127.0.0.1:8000/auth/register/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email": "shubman@example.com",
    "full_name": "Shubman Gill",
    "password": "shubman@123",
    "role": "trainee",
    "department": "Python",
    "reports_to": 8
}'

#### Response :- 
```
{
    "message": "User registered successfully..."
}
```


========================================================================


# Login :- 

curl --location 'http://127.0.0.1:8000/auth/login/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email" : "virat@example.com",
    "password": "virat@123"
}'

#### Response :-
```
{
    "refresh": "Refresh-Token",
    "access": "Access-Token"
}
```


========================================================================


# Refresh Access Token :- 

curl --location 'http://127.0.0.1:8000/auth/token/refresh/' \
--header 'Content-Type: application/json' \
--data '{
    "refresh" : "Refresh_Token"
}'

#### Response :-
```
{
    "access": "Access_Token"
}
```


========================================================================


# Apply/Add Leave Request

curl --location 'http://127.0.0.1:8000/leaves/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{ Access-Token }}' \
--data '{
    "title": "Family Function",
    "leave_type": "unpaid",
    "description": "Have a Family Function to attend",
    "start_date": "2026-05-21",
    "end_date": "2026-05-23"
}'

#### Response :- 
```
{
    "id": 6,
    "employee": 7,
    "employee_detail": {
        "id": 7,
        "full_name": "Virat Kohli",
        "email": "virat@example.com",
        "role": "trainee",
        "department": "Python"
    },
    "applied_by": 7,
    "applied_by_detail": {
        "id": 7,
        "full_name": "Virat Kohli",
        "email": "virat@example.com",
        "role": "trainee",
        "department": "Python"
    },
    "title": "Family Function",
    "leave_type": "unpaid",
    "description": "Have a Family Function to attend",
    "start_date": "2026-05-21",
    "end_date": "2026-05-23",
    "approval_status": "pending",
    "approved_by": null,
    "approved_by_detail": null,
    "leave_status": "open",
    "created_at": "2026-04-23T05:12:00.993999Z",
    "remaining_balance": null
}
```


========================================================================


# Get ALL Leaves

curl --location 'http://127.0.0.1:8000/leaves/' \
--header 'Authorization: Bearer {{ Access-Token }}'

#### Response :- (HR)
```
[
    {
        "id": 4,
        "employee": 8,
        "employee_detail": {
            "id": 8,
            "full_name": "MS Dhoni",
            "email": "dhoni@example.com",
            "role": "software_engineer",
            "department": "Python"
        },
        "applied_by": 13,
        "applied_by_detail": {
            "id": 13,
            "full_name": "Shreyash Iyer",
            "email": "shreyash@example.com",
            "role": "manager",
            "department": "Python"
        },
        "title": "Sick Leave",
        "leave_type": "sick",
        "description": "Employee is unwell and requires a sick leave",
        "start_date": "2026-05-21",
        "end_date": "2026-05-21",
        "approval_status": "pending",
        "approved_by": null,
        "approved_by_detail": null,
        "leave_status": "open",
        "created_at": "2026-04-23T04:50:56.188970Z",
        "remaining_balance": null
    },
    {
        "id": 3,
        "employee": 7,
        "employee_detail": {
            "id": 7,
            "full_name": "Virat Kohli",
            "email": "virat@example.com",
            "role": "trainee",
            "department": "Python"
        },
        "applied_by": 7,
        "applied_by_detail": {
            "id": 7,
            "full_name": "Virat Kohli",
            "email": "virat@example.com",
            "role": "trainee",
            "department": "Python"
        },
        "title": "Vacation",
        "leave_type": "paid",
        "description": "Going on a trip",
        "start_date": "2025-05-01",
        "end_date": "2025-05-03",
        "approval_status": "rejected",
        "approved_by": 8,
        "approved_by_detail": {
            "id": 8,
            "full_name": "MS Dhoni",
            "email": "dhoni@example.com",
            "role": "software_engineer",
            "department": "Python"
        },
        "leave_status": "open",
        "created_at": "2026-04-23T04:12:56.489537Z",
        "remaining_balance": null
    },
    {
        "id": 5,
        "employee": 11,
        "employee_detail": {
            "id": 11,
            "full_name": "KL Rahul",
            "email": "rahul@example.com",
            "role": "manager",
            "department": "Python"
        },
        "applied_by": 11,
        "applied_by_detail": {
            "id": 11,
            "full_name": "KL Rahul",
            "email": "rahul@example.com",
            "role": "manager",
            "department": "Python"
        },
        "title": "Family Function",
        "leave_type": "paid",
        "description": "Have a Family Function to attend",
        "start_date": "2026-05-16",
        "end_date": "2026-05-16",
        "approval_status": "pending",
        "approved_by": null,
        "approved_by_detail": null,
        "leave_status": "open",
        "created_at": "2026-04-23T05:00:01.480823Z",
        "remaining_balance": null
    }
]
```


========================================================================


# Get Single Leave :- 

curl --location 'http://127.0.0.1:8000/leaves/3' \
--header 'Authorization: Bearer {{ Access-Token }}'

#### Response :- 
```
{
    "id": 3,
    "employee": 7,
    "employee_detail": {
        "id": 7,
        "full_name": "Virat Kohli",
        "email": "virat@example.com",
        "role": "trainee",
        "department": "Python"
    },
    "applied_by": 7,
    "applied_by_detail": {
        "id": 7,
        "full_name": "Virat Kohli",
        "email": "virat@example.com",
        "role": "trainee",
        "department": "Python"
    },
    "title": "Vacation",
    "leave_type": "paid",
    "description": "Going on a trip",
    "start_date": "2025-05-01",
    "end_date": "2025-05-03",
    "approval_status": "rejected",
    "approved_by": 8,
    "approved_by_detail": {
        "id": 8,
        "full_name": "MS Dhoni",
        "email": "dhoni@example.com",
        "role": "software_engineer",
        "department": "Python"
    },
    "leave_status": "open",
    "created_at": "2026-04-23T04:12:56.489537Z",
    "remaining_balance": null
}
```


========================================================================


# Get Leaves By Status:- 

curl --location 'http://127.0.0.1:8000/leaves/?leave_status=open' \
--header 'Authorization: Bearer {{ Access-Token }}'

#### Response :- 
```
[
    {
        "id": 4,
        "employee": 8,
        "employee_detail": {
            "id": 8,
            "full_name": "MS Dhoni",
            "email": "dhoni@example.com",
            "role": "software_engineer",
            "department": "Python"
        },
        "applied_by": 13,
        "applied_by_detail": {
            "id": 13,
            "full_name": "Shreyash Iyer",
            "email": "shreyash@example.com",
            "role": "manager",
            "department": "Python"
        },
        "title": "Sick Leave",
        "leave_type": "sick",
        "description": "Employee is unwell and requires a sick leave",
        "start_date": "2026-05-21",
        "end_date": "2026-05-21",
        "approval_status": "pending",
        "approved_by": null,
        "approved_by_detail": null,
        "leave_status": "open",
        "created_at": "2026-04-23T04:50:56.188970Z",
        "remaining_balance": null
    }
]
```


========================================================================


# Add Holidays (Only HR) :- 

curl --location 'http://127.0.0.1:8000/leaves/holidays/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{ Access-Token }}' \
--data '{
    "date": "2026-01-14",
    "day": "WednesDay",
    "title": "Makar Sankranti"
}'

#### Repsponse :- 
```
{
    "id": 2,
    "date": "2026-01-14",
    "day": "WednesDay",
    "title": "Makar Sankranti"
}
```


========================================================================


# Get Holidays (ALL Employee) :- 

curl --location 'http://127.0.0.1:8000/leaves/holidays/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{ Access-Token }}'

#### Repsponse :- 
```
{
    "success": true,
    "message": "Holidays fetched successfully.",
    "data": {
        "count": 8,
        "next": "http://127.0.0.1:8000/leaves/holidays/?page=2",
        "previous": null,
        "results": [
            {
                "id": 1,
                "date": "2025-08-15",
                "day": "Friday",
                "title": "Independence Day"
            },
            {
                "id": 2,
                "date": "2026-01-14",
                "day": "WednesDay",
                "title": "Makar Sankranti"
            },
            {
                "id": 3,
                "date": "2026-01-26",
                "day": "MonDay",
                "title": "Republic Day"
            },
            {
                "id": 4,
                "date": "2026-03-04",
                "day": "Wednesday",
                "title": "Holi"
            },
            {
                "id": 5,
                "date": "2026-08-28",
                "day": "Friday",
                "title": "Raksha Bandhan"
            }
        ]
    }
}
```


========================================================================


# Update Leave Status :- 

curl --location --request PATCH 'http://127.0.0.1:8000/leaves/1/' \
--header 'Authorization: Bearer Access-Token' \
--header 'Content-Type: application/json' \
--data '{
    "approval_status" : "approved"
}'

#### Responses :- 
```
{
    "message": "Leave approved by Shreyash Iyer.",
    "data": {
        "approval_status": "approved"
    }
}
```
```
{
    "error": "You can only cancel your own leave."
}
```
```
{
    "approval_status": "rejected"
}
```


========================================================================


# Apply Leave Behalf :- 

curl --location 'http://127.0.0.1:8000/leaves/behalf/8/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{ Access-Token }}' \
--data '{
    "title": "Sick Leave",
    "leave_type": "sick",
    "description": "Employee is unwell and requires a sick leave",
    "start_date": "2026-05-21",
    "end_date": "2026-05-21"
}'

#### Response :- 
```
{
    "id": 4,
    "employee": 8,
    "employee_detail": {
        "id": 8,
        "full_name": "MS Dhoni",
        "email": "dhoni@example.com",
        "role": "software_engineer",
        "department": "Python"
    },
    "applied_by": 13,
    "applied_by_detail": {
        "id": 13,
        "full_name": "Shreyash Iyer",
        "email": "shreyash@example.com",
        "role": "manager",
        "department": "Python"
    },
    "title": "Sick Leave",
    "leave_type": "sick",
    "description": "Employee is unwell and requires a sick leave",
    "start_date": "2026-05-21",
    "end_date": "2026-05-21",
    "approval_status": "pending",
    "approved_by": null,
    "approved_by_detail": null,
    "leave_status": "open",
    "created_at": "2026-04-23T04:50:56.188970Z",
    "remaining_balance": null
}
```

========================================================================


# Add Notify Person :- 

curl --location 'http://127.0.0.1:8000/leaves/notify/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{ Access-Token }}' \
--data '{
    "notify_user": 14
}'

#### Response :- 
```
{
    "id": 1,
    "employee": 7,
    "notify_user": 14
}
```


========================================================================


# Get Notify Person List :- 

curl --location 'http://127.0.0.1:8000/leaves/notify/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{ Access-Token }}'

#### Response :- 
```
[
    {
        "id": 1,
        "employee": 7,
        "notify_user": 14
    },
    {
        "id": 3,
        "employee": 7,
        "notify_user": 15
    }
]
```


========================================================================


# Delete Nofity Person from list :- 

curl --location --request DELETE 'http://127.0.0.1:8000/leaves/notify/2/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{ Access-Token }}'

#### Response :- 
```
{
    "message": "Removed from notify list."
}
```


========================================================================


# Change Password :- 

curl --location 'http://127.0.0.1:8000/auth/password-change/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{ Access-Token }}' \
--data-raw '{
    "old_password" : "virat@123",
    "new_password" : "virat@1234"
}'

#### Response :- 
```
{
    "message": "Password changed successfully"
}
```


========================================================================


# Logout :- 

curl --location 'http://127.0.0.1:8000/auth/logout/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{ Access-Token }}' \
--data '{
    "refresh" : "Refresh-Token"
}'

#### Response :- 
```
{
    "message": "Logged out successfully."
}
```


========================================================================


# Employee Update Profile (Only allow Full_name and department.)

curl --location --request PATCH 'http://127.0.0.1:8000/auth/profile/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{ Access-Token }}' \
--data '{
    "full_name" : "Viratbhai Kohli"
}'

#### Response :- 
```
{
    "success": true,
    "message": "Profile updated successfully.",
    "data": {
        "id": 7,
        "email": "virat@example.com",
        "full_name": "Viratbhai Kohli",
        "role": "trainee",
        "department": "Python",
        "is_hr": false,
        "reports_to": 8
    }
}
```


========================================================================


# HR Update Any Employee Profile (Can Update full_name, role, department, is_hr, reports_to):-

curl --location --request PATCH 'http://127.0.0.1:8000/auth/profile/7/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{ Access-Token }}' \
--data '{
    "full_name" : "Virat Kohli"
}'

#### Response :- 
```
{
    "success": true,
    "message": "Profile updated successfully.",
    "data": {
        "id": 7,
        "email": "virat@example.com",
        "full_name": "Virat Kohli",
        "role": "trainee",
        "department": "Python",
        "is_hr": false,
        "reports_to": 8
    }
}
```


========================================================================


# Get Employee By HR :- 

curl --location 'http://127.0.0.1:8000/auth/employees/?search=virat&department=python&role=trainee' \
--header 'Authorization: Bearer {{ Access-Token }}'

#### Response :- 
```
{
    "success": true,
    "message": "Employees fetched successfully.",
    "data": {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 7,
                "email": "virat@example.com",
                "full_name": "Virat Kohli",
                "role": "trainee",
                "department": "Python",
                "is_hr": false,
                "reports_to": 8
            }
        ]
    }
}
```


========================================================================


# Pagination 1 :- 

curl --location 'http://127.0.0.1:8000/leaves?page=1&page_size=3' \
--header 'Authorization: Bearer {{ Access-Token }}'

#### Response :- 
```
{
    "success": true,
    "message": "Leaves fetched successfully.",
    "data": {
        "count": 5,
        "next": "http://127.0.0.1:8000/leaves/?page=2&page_size=3",
        "previous": null,
        "results": [
            {
                "id": 7,
                "employee": 16,
                "employee_detail": {
                    "id": 16,
                    "full_name": "Ram Bhai",
                    "email": "rishil.kathiriya@simformsolutions.com",
                    "role": "senior_software_engineer",
                    "department": "Python"
                },
                "applied_by": 16,
                "applied_by_detail": {
                    "id": 16,
                    "full_name": "Ram Bhai",
                    "email": "rishil.kathiriya@simformsolutions.com",
                    "role": "senior_software_engineer",
                    "department": "Python"
                },
                "title": "Personal Reason",
                "leave_type": "unpaid",
                "description": "Have a Family Function to attend",
                "start_date": "2026-05-10",
                "end_date": "2026-05-11",
                "approval_status": "approved",
                "approved_by": 13,
                "approved_by_detail": {
                    "id": 13,
                    "full_name": "Shreyash Iyer",
                    "email": "shreyash@example.com",
                    "role": "manager",
                    "department": "Python"
                },
                "leave_status": "open",
                "created_at": "2026-04-24T10:07:03.447593Z",
                "remaining_balance": null
            },
            {
                "id": 6,
                "employee": 7,
                "employee_detail": {
                    "id": 7,
                    "full_name": "Virat Kohli",
                    "email": "virat@example.com",
                    "role": "trainee",
                    "department": "Python"
                },
                "applied_by": 7,
                "applied_by_detail": {
                    "id": 7,
                    "full_name": "Virat Kohli",
                    "email": "virat@example.com",
                    "role": "trainee",
                    "department": "Python"
                },
                "title": "Family Function",
                "leave_type": "unpaid",
                "description": "Have a Family Function to attend",
                "start_date": "2026-05-21",
                "end_date": "2026-05-23",
                "approval_status": "pending",
                "approved_by": null,
                "approved_by_detail": null,
                "leave_status": "open",
                "created_at": "2026-04-23T05:12:00.993999Z",
                "remaining_balance": null
            },
            {
                "id": 5,
                "employee": 11,
                "employee_detail": {
                    "id": 11,
                    "full_name": "KL Rahul",
                    "email": "rahul@example.com",
                    "role": "manager",
                    "department": "Python"
                },
                "applied_by": 11,
                "applied_by_detail": {
                    "id": 11,
                    "full_name": "KL Rahul",
                    "email": "rahul@example.com",
                    "role": "manager",
                    "department": "Python"
                },
                "title": "Family Function",
                "leave_type": "paid",
                "description": "Have a Family Function to attend",
                "start_date": "2026-05-16",
                "end_date": "2026-05-16",
                "approval_status": "pending",
                "approved_by": null,
                "approved_by_detail": null,
                "leave_status": "open",
                "created_at": "2026-04-23T05:00:01.480823Z",
                "remaining_balance": null
            }
        ]
    }
}
```


========================================================================


# Pagination 2 :- 

curl --location 'http://127.0.0.1:8000/leaves/?page=2&page_size=3' \
--header 'Authorization: Bearer {{ Access-Token }}'

#### Response :- 
```
{
    "success": true,
    "message": "Leaves fetched successfully.",
    "data": {
        "count": 5,
        "next": null,
        "previous": "http://127.0.0.1:8000/leaves/?page_size=3",
        "results": [
            {
                "id": 4,
                "employee": 8,
                "employee_detail": {
                    "id": 8,
                    "full_name": "MS Dhoni",
                    "email": "dhoni@example.com",
                    "role": "software_engineer",
                    "department": "Python"
                },
                "applied_by": 13,
                "applied_by_detail": {
                    "id": 13,
                    "full_name": "Shreyash Iyer",
                    "email": "shreyash@example.com",
                    "role": "manager",
                    "department": "Python"
                },
                "title": "Sick Leave",
                "leave_type": "sick",
                "description": "Employee is unwell and requires a sick leave",
                "start_date": "2026-05-21",
                "end_date": "2026-05-21",
                "approval_status": "pending",
                "approved_by": null,
                "approved_by_detail": null,
                "leave_status": "open",
                "created_at": "2026-04-23T04:50:56.188970Z",
                "remaining_balance": null
            },
            {
                "id": 3,
                "employee": 7,
                "employee_detail": {
                    "id": 7,
                    "full_name": "Virat Kohli",
                    "email": "virat@example.com",
                    "role": "trainee",
                    "department": "Python"
                },
                "applied_by": 7,
                "applied_by_detail": {
                    "id": 7,
                    "full_name": "Virat Kohli",
                    "email": "virat@example.com",
                    "role": "trainee",
                    "department": "Python"
                },
                "title": "Vacation",
                "leave_type": "paid",
                "description": "Going on a trip",
                "start_date": "2025-05-01",
                "end_date": "2025-05-03",
                "approval_status": "rejected",
                "approved_by": 8,
                "approved_by_detail": {
                    "id": 8,
                    "full_name": "MS Dhoni",
                    "email": "dhoni@example.com",
                    "role": "software_engineer",
                    "department": "Python"
                },
                "leave_status": "open",
                "created_at": "2026-04-23T04:12:56.489537Z",
                "remaining_balance": 2.0
            }
        ]
    }
}
```


========================================================================
































 




 
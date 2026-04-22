# Register :- 

curl --location 'http://127.0.0.1:8000/auth/register/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "rahul",
    "email": "rahul@gmail.com",
    "password": "rahul@123",
    "role": "trainee",
    "department": "python"
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
    "username" : "rahul",
    "password": "rahul@123"
}'

#### Response :-
```
{
    "refresh": "Refresh_Token",
    "access": "Access_Token"
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
--header 'Authorization: Bearer Access-Token' \
--data '{
    "title" : "Apply for Leave on 2nd to 4th May",
    "leave_type" : "unpaid",
    "description" : "I wanna attend the wedding function on these days.",
    "start_date" : "2026-05-02",
    "end_date" : "2026-05-04"
}'

#### Response :- 
```
{
    "id": 2,
    "employee": 4,
    "applied_by": 4,
    "title": "Apply for Leave on 2nd to 4th May",
    "leave_type": "unpaid",
    "description": "I wanna attend the wedding function on these days.",
    "start_date": "2026-05-02",
    "end_date": "2026-05-04",
    "approval_status": "pending",
    "approved_by": null,
    "leave_status": "open",
    "created_at": "2026-04-22T09:03:35.324345Z",
    "remaining_balance": null
}
```




========================================================================

# Get ALL Leaves

curl --location 'http://127.0.0.1:8000/leaves/' \
--header 'Authorization: Access-Token'

#### Response :- 
```
[
    {
        "id": 1,
        "employee": 3,
        "applied_by": 3,
        "title": "Apply for Leave on 21th May",
        "leave_type": "paid",
        "description": "I want to take leave of Personal Reason.",
        "start_date": "2026-05-21",
        "end_date": "2026-05-21",
        "approval_status": "pending",
        "approved_by": null,
        "leave_status": "open",
        "created_at": "2026-04-22T08:50:25.827325Z",
        "remaining_balance": null
    },
    {
        "id": 2,
        "employee": 4,
        "applied_by": 4,
        "title": "Apply for Leave on 2nd to 4th May",
        "leave_type": "unpaid",
        "description": "I wanna attend the wedding function on these days.",
        "start_date": "2026-05-02",
        "end_date": "2026-05-04",
        "approval_status": "pending",
        "approved_by": null,
        "leave_status": "open",
        "created_at": "2026-04-22T09:03:35.324345Z",
        "remaining_balance": null
    }
]
```



========================================================================

# Get Single Leave :- 

curl --location 'http://127.0.0.1:8000/leaves/' \
--header 'Authorization: Bearer Access-Token'

#### Response :- 
```
{
    "id": 1,
    "employee": 3,
    "applied_by": 3,
    "title": "Apply for Leave on 21th May",
    "leave_type": "paid",
    "description": "I want to take leave of Personal Reason.",
    "start_date": "2026-05-21",
    "end_date": "2026-05-21",
    "approval_status": "pending",
    "approved_by": null,
    "leave_status": "open",
    "created_at": "2026-04-22T08:50:25.827325Z",
    "remaining_balance": null
}
```



========================================================================

# Leave Balance :- 

curl --location 'http://127.0.0.1:8000/leaves/balance/' \
--header 'Authorization: Bearer Access-Token'

#### Response :- 
```
Hello
```



========================================================================

# Get Holidays :- 

curl --location 'http://127.0.0.1:8000/leaves/holidays/' \
--header 'Authorization: Bearer Access-Token'

#### Repsponse :- 
```
Holidays
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
    "approval_status": "approved"
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






























 
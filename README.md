
# To get Coverage Report
coverage run --source='.' manage.py test 
coverage report

# To run celery
celery -A config worker -l info
celery -A config beat -l info

# Create a new User
```
curl --location 'http://localhost:8000/api/user/register/' \
--header 'Content-Type: application/json' \
--data-raw '{
  "username": "pnklsdsdfsafn",
  "password": "1234",
  "email": "pradyneel+jaasknsadfv@gmail.com"
}
'
```
![PYJAMAHR](https://github.com/user-attachments/assets/678a2649-a993-4875-9de0-80abd427484e)


TOKEN=$(docker exec app-web-1 python manage.py shell -c "from rest_framework_simplejwt.tokens import AccessToken; from django.contrib.auth import get_user_model; print(AccessToken.for_user(get_user_model().objects.get(username='admin')))")
PAYMENT_ID=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/payments/ | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
docker run --rm --net host node:18-alpine sh -c "npm install -g autocannon && autocannon -c 10 -d 30 -H 'Authorization: Bearer $TOKEN' http://localhost:8000/api/v1/payments/$PAYMENT_ID/"

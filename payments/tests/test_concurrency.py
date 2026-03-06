import pytest
import uuid
import threading
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from django.db import connection

@pytest.mark.django_db(transaction=True)
class TestConcurrency:
    def test_concurrent_identical_payment_intake(self, auth_client, test_user):
        """
        FR-12: The system shall handle simultaneous identical payment intake requests.
        """
        url = reverse('payment_list_create')
        payment_id = str(uuid.uuid4())
        data = {
            'payment_id': payment_id,
            'amount': '200.00',
            'currency': 'USD',
            'recipient_email': 'concurrent@example.com'
        }
        
        results = []
        
        # We need a shared client or session usually, but for simple threading 
        # using the same auth_client which is already authenticated should work.
        # Note: Django's test DB handles transactions differently per thread 
        # unless specified.
        
        def send_request():
            # Closures to capture results
            # Each thread needs its own DB connection in some environments,
            # but pytest-django transaction=True helps.
            try:
                with patch('payments.views.process_payment_notification.delay'):
                    response = auth_client.post(url, data)
                    results.append(response.status_code)
            except Exception as e:
                results.append(str(e))
            finally:
                connection.close()

        threads = [threading.Thread(target=send_request) for _ in range(2)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        # One should be 202, the other should be 409
        assert status.HTTP_202_ACCEPTED in results
        assert status.HTTP_409_CONFLICT in results
        assert len(results) == 2

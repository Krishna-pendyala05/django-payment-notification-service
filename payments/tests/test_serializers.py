import pytest
import uuid
from payments.serializers import PaymentSerializer

def test_payment_serializer_valid():
    data = {
        'payment_id': str(uuid.uuid4()),
        'amount': '100.00',
        'currency': 'USD',
        'recipient_email': 'test@example.com',
        'description': 'Test payment'
    }
    serializer = PaymentSerializer(data=data)
    assert serializer.is_valid()

def test_payment_serializer_invalid_amount():
    data = {
        'payment_id': str(uuid.uuid4()),
        'amount': '-10.00',
        'currency': 'USD',
        'recipient_email': 'test@example.com'
    }
    serializer = PaymentSerializer(data=data)
    assert not serializer.is_valid()
    assert 'amount' in serializer.errors

def test_payment_serializer_invalid_currency():
    data = {
        'payment_id': str(uuid.uuid4()),
        'amount': '100.00',
        'currency': 'US', # too short
        'recipient_email': 'test@example.com'
    }
    serializer = PaymentSerializer(data=data)
    assert not serializer.is_valid()
    assert 'currency' in serializer.errors

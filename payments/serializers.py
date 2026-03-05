from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'payment_id', 
            'amount', 
            'currency', 
            'recipient_email', 
            'description', 
            'status', 
            'created_at'
        ]
        read_only_fields = ['status', 'created_at']
        extra_kwargs = {
            'payment_id': {'validators': []}  # Disable unique validator to handle in view
        }

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        if value > 999999.99:
            raise serializers.ValidationError("Amount exceeds maximum allowed limit.")
        return value

    def validate_currency(self, value):
        if len(value) != 3:
            raise serializers.ValidationError("Currency must be a 3-letter ISO code.")
        return value.upper()

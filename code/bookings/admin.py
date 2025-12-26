from django.contrib import admin
from .models import Customer, Booking, MessageLog

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'last_name', 'created_at')
    search_fields = ('phone_number', 'first_name', 'last_name')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('get_customer_name', 'start_time', 'status', 'google_event_id')
    list_filter = ('status', 'start_time')

    # custom column to show name
    def get_customer_name(self, obj):
        if obj.customer.first_name:
            return f"{obj.customer.first_name} {obj.customer.last_name or ''}"
        return obj.customer.phone_number
    get_customer_name.short_description = 'Customer'

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('get_sender_name', 'direction', 'message_body', 'timestamp')
    list_filter = ('direction',)
    
    # Custom column to look up name from Customer table
    def get_sender_name(self, obj):
        # Try to find the customer by phone number
        try:
            c = Customer.objects.get(phone_number=obj.sender)
            if c.first_name:
                return f"{c.first_name} ({obj.sender})"
        except Customer.DoesNotExist:
            pass
        return obj.sender
    get_sender_name.short_description = 'Sender'
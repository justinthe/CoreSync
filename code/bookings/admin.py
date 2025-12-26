from django.contrib import admin
from .models import Customer, Booking, MessageLog

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'created_at')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer', 'start_time', 'status')
    list_filter = ('status', 'start_time')

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('sender', 'direction', 'timestamp')
    list_filter = ('direction',)
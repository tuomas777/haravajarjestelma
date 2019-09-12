from django.dispatch import Signal

event_approved = Signal(providing_args=["instance"])

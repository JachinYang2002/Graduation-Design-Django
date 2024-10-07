from django.dispatch import Signal

container_stopped_signal = Signal(providing_args=["image_pk"])
from django.apps import AppConfig


class KvmConfig(AppConfig):
    name = 'kvm'

    def ready(self):
        import kvm.signals

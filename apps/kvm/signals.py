from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from kvm.models import VmInstance
import libvirt


@receiver(pre_delete, sender=VmInstance)
def toppings_changed(sender, instance, **kwargs):
    # try:
    #     status = instance.get_status
    # except libvirt.libvirtError:
    #     pass
    # else:
    #     if status == 1:
    #         instance.proxy.force_shutdown()
    #     instance.proxy.delete_all_disks()
    #     instance.proxy.delete()
    pass

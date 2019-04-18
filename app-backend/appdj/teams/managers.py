from django.db import models
from treebeard.mp_tree import MP_NodeQuerySet

from appdj.base.models import TBSQuerySetMixin


class GroupQuerySet(TBSQuerySetMixin, MP_NodeQuerySet):
    pass


class GroupManager(models.Manager):
    def get_queryset(self):
        return GroupQuerySet(self.model).order_by('path')

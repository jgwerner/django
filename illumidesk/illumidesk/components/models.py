from django.db.models import DateTimeField
from django.db.models import Model


class IllumiDeskBaseModel(Model):
    """
    Base model that includes default created / updated timestamps.
    """
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True

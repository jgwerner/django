from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from guardian.compat import url

from .models import CanvasInstance


@admin.register(CanvasInstance)
class CanvasInstanceAdmin(GuardedModelAdmin):
    list_display = ('instance_guid', 'name')
    filter_horizontal = ('users', 'applications', 'clusters')

    def get_urls(self):
        """
        JKP: needed to adjust for uuids.

        Extends standard admin model urls with the following:

        - ``.../permissions/`` under ``app_mdodel_permissions`` url name (params: object_pk)
        - ``.../permissions/user-manage/<user_id>/`` under ``app_model_permissions_manage_user`` url name (params: object_pk, user_pk)
        - ``.../permissions/group-manage/<group_id>/`` under ``app_model_permissions_manage_group`` url name (params: object_pk, group_pk)

        .. note::
           ``...`` above are standard, instance detail url (i.e.
           ``/admin/flatpages/1/``)

        """
        urls = super(GuardedModelAdmin, self).get_urls()
        if self.include_object_permissions_urls:
            info = self.model._meta.app_label, self.model._meta.model_name
            myurls = [
                url(r'^(?P<object_pk>.+)/permissions/$',
                    view=self.admin_site.admin_view(
                        self.obj_perms_manage_view),
                    name='%s_%s_permissions' % info),
                url(r'^(?P<object_pk>.+)/permissions/user-manage/(?P<user_id>[\w-]+)/$',
                    view=self.admin_site.admin_view(
                        self.obj_perms_manage_user_view),
                    name='%s_%s_permissions_manage_user' % info),
                url(r'^(?P<object_pk>.+)/permissions/group-manage/(?P<group_id>[\w-]+)/$',
                    view=self.admin_site.admin_view(
                        self.obj_perms_manage_group_view),
                    name='%s_%s_permissions_manage_group' % info),
            ]
            urls = myurls + urls
        return urls

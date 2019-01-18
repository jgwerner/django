from django.contrib.auth import get_user_model


class Namespace(object):
    def __init__(self, name='', typ='', obj=None):
        self.name = name
        self.object = obj
        self.type = typ

    @staticmethod
    def from_name(name):
        from appdj.teams.models import Team
        ns = Namespace(name=name)
        ns.object = get_user_model().objects.filter(username=name,
                                                    is_active=True).first()
        if ns.object is not None:
            ns.type = 'user'
            return ns

        ns.object = Team.objects.filter(name=name).first()
        if ns.object is not None:
            ns.type = 'team'
            return ns

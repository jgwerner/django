class SearchSerializerMixin: # pylint disable=too-few-public-methods
    def to_representation(self, instance):
        if not isinstance(instance, self.Meta.model):
            instance = instance.object
        return super().to_representation(instance)

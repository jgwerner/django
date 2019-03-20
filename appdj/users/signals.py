from django import dispatch


user_authenticated = dispatch.Signal(providing_args=['user'])

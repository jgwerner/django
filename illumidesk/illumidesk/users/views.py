from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from django.views.decorators.http import require_POST

from .forms import IllumiDeskUserChangeForm, UploadAvatarForm
from .models import IllumiDeskUser


User = get_user_model()


@login_required
def profile(request):
    if request.method == 'POST':
        form = IllumiDeskUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = IllumiDeskUserChangeForm(instance=request.user)
    return render(request, 'account/profile.html', {
        'form': form,
        'active_tab': 'profile'
    })


@login_required
@require_POST
def upload_profile_image(request):
    user = request.user
    form = UploadAvatarForm(request.POST, request.FILES)
    if form.is_valid():
        user.avatar = request.FILES['avatar']
        user.save()
    return HttpResponse('Success!')


class UserDetailView(LoginRequiredMixin, DetailView):

    model = IllumiDeskUser
    slug_field = 'username'
    slug_url_kwarg = 'username'


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = IllumiDeskUser
    fields = ['name']

    def get_success_url(self):
        return reverse('users:detail', kwargs={'username': self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, _('Infos successfully updated')
        )
        return super().form_valid(form)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail', kwargs={'username': self.request.user.username})


user_redirect_view = UserRedirectView.as_view()

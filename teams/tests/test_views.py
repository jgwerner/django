from unittest.mock import patch
from django.conf import settings
from django.urls import reverse
from django.test import TestCase, Client, override_settings
from rest_framework import status
from rest_framework.test import APITransactionTestCase, APITestCase

from billing.models import Subscription, Plan
from billing.tests.factories import (SubscriptionFactory,
                                     InvoiceFactory,
                                     InvoiceItemFactory)
from billing.tests import fake_stripe
from users.tests.factories import UserFactory, EmailFactory
from projects.utils import assign_to_team
from projects.tests.factories import ProjectFactory
from servers.tests.factories import ServerFactory, ServerSizeFactory
from jwt_auth.utils import create_auth_jwt

from .factories import TeamFactory
from ..models import Team, Group


class TeamTest(APITransactionTestCase):

    fixtures = ['plans.json']

    @override_settings(ENABLE_BILLING=True)
    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUp(self):
        self.user = UserFactory()
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    @override_settings(ENABLE_BILLING=True)
    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_create_team(self):
        url = reverse('team-list', kwargs={'version': settings.DEFAULT_VERSION})
        data = {'name': 'TestTeam'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 1)
        team = Team.objects.get()
        self.assertEqual(team.name, data['name'])
        self.assertEqual(team.groups.count(), 2)
        self.assertTrue(team.groups.filter(name='owners').exists())
        self.assertTrue(team.groups.filter(name='members').exists())
        self.assertIsNotNone(team.customer)

    def test_create_team_with_name_same_as_user(self):
        UserFactory(username='test')
        url = reverse('team-list', kwargs={'version': settings.DEFAULT_VERSION})
        data = {'name': 'test'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_teams(self):
        teams_count = 4
        url = reverse('team-list', kwargs={'version': settings.DEFAULT_VERSION})
        TeamFactory.create_batch(teams_count)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), teams_count)

    def test_list_my_teams(self):
        teams_count = 4
        url = reverse('my-team-list', kwargs={'version': settings.DEFAULT_VERSION})
        TeamFactory.create_batch(teams_count, created_by=self.user)
        TeamFactory.create_batch(teams_count)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), teams_count)

    def test_list_my_team_groups(self):
        team = TeamFactory(created_by=self.user)
        url = reverse('my-group-list', kwargs={'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_team_details(self):
        team = TeamFactory(created_by=self.user)
        url = reverse('team-detail', kwargs={'version': settings.DEFAULT_VERSION, 'team': str(team.pk)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], team.name)

    def test_team_details_with_name(self):
        team = TeamFactory(created_by=self.user)
        url = reverse('team-detail', kwargs={'version': settings.DEFAULT_VERSION, 'team': team.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], team.name)

    def _create_base_permission_test(self):
        owner = UserFactory()
        token = create_auth_jwt(owner)
        cli = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')
        team = TeamFactory(created_by=owner)
        return team, cli

    def test_team_group_permission_for_project(self):
        team, cli = self._create_base_permission_test()
        project_url = reverse('project-list', kwargs={'version': settings.DEFAULT_VERSION, 'namespace': team.name})
        resp = cli.post(project_url, data=dict(name='Test'))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.client.post(project_url, data=dict(name='Test2'))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_group_permission_for_project_file(self):
        team, cli = self._create_base_permission_test()
        project = ProjectFactory()
        assign_to_team(team=team, project=project)
        projectfile_url = reverse('projectfile-list', kwargs={
            'version': settings.DEFAULT_VERSION, 'namespace': team.name, 'project_project': str(project.pk)})
        resp = cli.post(projectfile_url, data=dict(name='Test'))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.client.post(projectfile_url, data=dict(name='Test2'))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_group_permission_for_server(self):
        srv_size = ServerSizeFactory()
        team, cli = self._create_base_permission_test()
        project = ProjectFactory(team=team)
        server_url = reverse('server-list', kwargs={
            'version': settings.DEFAULT_VERSION, 'namespace': team.name, 'project_project': str(project.pk)})
        data = dict(
            size=str(srv_size.pk),
            name='Test',
            image_name='test',
            config={'type': 'jupyter'}
        )
        resp = cli.post(server_url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data['name'] = 'Test2'
        resp = self.client.post(server_url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_group_permission_for_ssh_tunnel(self):
        team, cli = self._create_base_permission_test()
        project = ProjectFactory()
        server = ServerFactory(project=project)
        tunnel_url = reverse('sshtunnel-list', kwargs={
                'version': settings.DEFAULT_VERSION,
                'namespace': team.name,
                'project_project': str(project.pk),
                'server_server': str(server.pk)
            }
        )
        data = dict(
            name='Test',
            host='localhost',
            local_port=1234,
            remote_port=1234,
            endpoint='localhost:1234',
            username='test'
        )
        resp = cli.post(tunnel_url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data['name'] = 'Test2'
        resp = self.client.post(tunnel_url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_group(self):
        team = TeamFactory(created_by=self.user)
        data = dict(name='testers', permissions=[])
        url = reverse('group-list', kwargs={'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk)})
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.filter(name=data['name']).count(), 1)

    def test_add_group_child(self):
        team = TeamFactory(created_by=self.user)
        owners = team.groups.get(name='owners')
        data = dict(name='testers', parent=str(owners.pk), permissions=[])
        url = reverse('group-list', kwargs={'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk)})
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        owners.refresh_from_db()
        self.assertEqual(owners.get_children_count(), 1)

    def test_group_read_perm(self):
        team, cli = self._create_base_permission_test()
        owners = team.groups.get(name='owners')
        url = reverse('group-detail', kwargs={
            'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk), 'group': str(owners.pk)})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = cli.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_group_write_perm(self):
        team, cli = self._create_base_permission_test()
        owners = team.groups.get(name='owners')
        data = dict(private=not owners.private)
        url = reverse('group-detail', kwargs={
            'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk), 'group': str(owners.pk)})
        resp = self.client.patch(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = cli.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_group_public(self):
        team, cli = self._create_base_permission_test()
        owners = team.groups.get(name='owners')
        owners.private = False
        owners.save()
        url = reverse('group-detail', kwargs={
            'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk), 'group': str(owners.pk)})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = cli.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


@override_settings(ENABLE_BILLING=True)
class SubscriptionTest(APITestCase):
    fixtures = ['notification_types.json', 'plans.json']

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUp(self):
        self.user = UserFactory(first_name="Foo",
                                last_name="Bar",
                                is_staff=True)
        EmailFactory(user=self.user,
                     address=self.user.email)
        self.team = TeamFactory(created_by=self.user, customer=self.user.customer)
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.plans_to_delete = []
        self.url_kwargs = {
            'version': settings.DEFAULT_VERSION,
            'team_team': str(self.team.pk),
        }

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_subscription_create(self):
        pre_test_sub_count = Subscription.objects.count()
        plan = Plan.objects.get(stripe_id="standard")
        data = {'plan': plan.pk}
        url = reverse("team-subscription-list", kwargs=self.url_kwargs)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), pre_test_sub_count + 1)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_update_subscription_fails(self):
        subscription = SubscriptionFactory(customer=self.user.customer,
                                           status="trialing")
        url = reverse("team-subscription-detail", kwargs={'pk': subscription.pk, **self.url_kwargs})
        response = self.client.patch(url, data={'status': "active"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_list_subscriptions(self):
        not_me_sub_count = 3
        for _ in range(not_me_sub_count):
            UserFactory()
            # Dont need to create a Subscription, one is created to the free plan automatically
        my_subs_count = 2
        SubscriptionFactory.create_batch(my_subs_count,
                                         customer=self.user.customer,
                                         plan__amount=500,
                                         status=Subscription.ACTIVE)
        url = reverse("team-subscription-list", kwargs=self.url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.filter(customer=self.user.customer,
                                                     plan__amount__gt=0).count(), my_subs_count)
        # The + 1 here corresponds to the automatically created default subscription when the user is entered in
        # The database
        self.assertEqual(len(response.data), my_subs_count + 1)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_subscription_details(self):
        sub = SubscriptionFactory(customer=self.user.customer,
                                  status=Subscription.ACTIVE)
        url = reverse("team-subscription-detail", kwargs={'pk': sub.pk, **self.url_kwargs})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(sub.pk), response.data.get('id'))

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_subscription_cancel(self):
        pre_test_sub_count = Subscription.objects.count()
        subscription = SubscriptionFactory(customer=self.user.customer,
                                           status="trialing")
        url = reverse("team-subscription-detail", kwargs={'pk': subscription.pk, **self.url_kwargs})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Subscription.objects.count(), pre_test_sub_count + 1)
        sub_reloaded = Subscription.objects.get(pk=subscription.pk)
        self.assertEqual(sub_reloaded.status, Subscription.CANCELED)
        self.assertIsNotNone(sub_reloaded.canceled_at)
        self.assertIsNotNone(sub_reloaded.ended_at)


@override_settings(ENABLE_BILLING=True)
class InvoiceTest(TestCase):

    fixtures = ['notification_types.json', 'plans.json']

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUp(self):
        self.user = UserFactory(first_name="Foo",
                                last_name="Bar",
                                is_staff=True)
        EmailFactory(user=self.user,
                     address=self.user.email)
        token = create_auth_jwt(self.user)
        self.api_client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.client = Client()
        self.team = TeamFactory(created_by=self.user, customer=self.user.customer)
        self.url_kwargs = {
            'version': settings.DEFAULT_VERSION,
            'team_team': str(self.team.pk),
        }

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_invoice_items_list_is_scoped_by_invoice(self):
        first_invoice = InvoiceFactory(customer=self.user.customer)
        InvoiceItemFactory.create_batch(3, invoice=first_invoice)

        second_invoice = InvoiceFactory(customer=self.user.customer)
        InvoiceItemFactory.create_batch(2, invoice=second_invoice)

        url = reverse('team-invoice-items-list', kwargs={'invoice_id': str(second_invoice.id),
                                                         **self.url_kwargs})
        response = self.api_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        for item in response.data:
            self.assertEqual(item['invoice'], second_invoice.id)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_invoice_item_retrieve(self):
        first_invoice = InvoiceFactory(customer=self.user.customer)
        InvoiceItemFactory.create_batch(3, invoice=first_invoice)

        second_invoice = InvoiceFactory(customer=self.user.customer)
        item = InvoiceItemFactory(invoice=second_invoice)

        url = reverse('team-invoice-items-detail', kwargs={'invoice_id': str(second_invoice.id),
                                                           'pk': str(item.id),
                                                           **self.url_kwargs})
        response = self.api_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(item.id))

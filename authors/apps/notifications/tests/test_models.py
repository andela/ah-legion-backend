from authors.apps.notifications.models import Notification
from .basetest import BaseTest

class TestModels(BaseTest):

    def test_string_representation(self):
        """ test for the value returned by __str__ """
        self.assertEqual(str(self.notification), self.notification_body)

    def test_notification_stored(self):
        """ test whether a notification is succesfully stored in the database """
        self.assertEqual(Notification.objects.all().count(),2)
        self.assertEqual(self.notification.pk,1)

    def test_ordering_of_notifications(self):
        """ test if notifications are returned in the order specified """
        notifications = Notification.objects.all()
        self.assertEqual(self.notification,notifications[0])
        self.assertEqual(self.notification1,notifications[1])
    
    def test_model_mark_all_as_read(self):
        """ test if the model has ability to mark all notifications as read """
        response = Notification.objects.mark_all_as_read(self.user1)
        notifications = self.user1.notified.all()
        for notification in notifications:
            self.assertEqual(Notification.objects.filter(pk=notification.id,read=self.user1.id).exists(), True)

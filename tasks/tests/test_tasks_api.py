from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()

class TaskApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", "alice@example.com", "pass123456")
        token = self.client.post("/api/auth/token/", {"username":"alice","password":"pass123456"}, format="json").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_list_update_delete_task(self):
        # create
        res = self.client.post("/api/tasks/", {"title":"T1","priority":"High"}, format="json")
        self.assertEqual(res.status_code, 201)
        task_id = res.data["id"]

        # list
        res = self.client.get("/api/tasks/")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(any(t["id"] == task_id for t in res.data))

        # update
        res = self.client.put(f"/api/tasks/{task_id}/", {"title":"T1-upd","priority":"Low"}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["title"], "T1-upd")

        # toggle complete
        res = self.client.patch(f"/api/tasks/{task_id}/complete/", {"is_completed": True}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["is_completed"])

        # delete
        res = self.client.delete(f"/api/tasks/{task_id}/")
        self.assertEqual(res.status_code, 204)

    def test_ownership_enforced(self):
        # task for alice
        t = Task.objects.create(user=self.user, title="Private")
        # new user
        bob = User.objects.create_user("bob", "bob@example.com", "pass123456")
        token_bob = self.client.post("/api/auth/token/", {"username":"bob","password":"pass123456"}, format="json").data["access"]

        # bob cannot access alice's task
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_bob}")
        res = self.client.get(f"/api/tasks/{t.id}/")
        self.assertEqual(res.status_code, 404)  # not visible in queryset

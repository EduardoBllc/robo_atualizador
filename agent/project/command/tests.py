from rest_framework.test import APITestCase

from agent.project.command.serializer import CommandSerializer
from agent.project.models import Project
from agent.project.command.models import Command


class CommandViewTests(APITestCase):

    project: Project = None

    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            id=1,
            name="Test Project",
            path="/Volumes/ESSD/Projetos/vendabemweb"
        )

    def create_test_command(self):
        Command.objects.create(
            project=self.project,
            name="Test Command",
            command="echo 'Hello, World!'"
        )

    def test_project_not_found(self):
        response = self.client.get('/project/999/command/')
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)
        self.assertEqual(response.data['error'], "Project not found.")

    def test_get_commands(self):
        self.create_test_command()

        response = self.client.get('/project/1/command/')
        self.assertEqual(response.status_code, 200)

        # Gathering expected data
        project = Project.objects.get(id=1)
        command = Command.objects.filter(project=project).first()
        serialized_command = CommandSerializer(command).data

        self.assertEqual(response.data, [serialized_command])

    def test_post_command(self):
        # Valid command creation
        response = self.client.post('/project/1/command/', {
            "name": "New Command",
            "command": "echo 'New Command Executed'",
            "description": "This is a new command.",
            "restart_command": False
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.data)
        self.assertIn('command_id', response.data)

        # Invalid command creation (missing required 'command' field)
        response = self.client.post('/project/1/command/', {
            "name": "Invalid Command",
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertIn("details", response.data)

    def test_patch_command(self):
        self.create_test_command()

        # First, test updating without changing any fields
        response = self.client.patch('/project/1/command/', {
            "id": 1,
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data['message'], "Nothing changed")

        # Now, test updating with a field change
        response = self.client.patch('/project/1/command/', {
            "id": 1,
            "name": "Updated Command Name"
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.data)

        command = Command.objects.get(id=1)
        self.assertEqual(command.name, "Updated Command Name")

    def test_delete_command(self):
        self.create_test_command()

        response = self.client.delete('/project/1/command/', {
            "id": 1,
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data['message'], "Command successfully deleted")

        # Verify the command is actually deleted
        with self.assertRaises(Command.DoesNotExist):
            Command.objects.get(id=1)


class CommandDetailViewTests(APITestCase):

    project: Project = None

    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            id=1,
            name="Test Project",
            path="/Volumes/ESSD/Projetos/vendabemweb"
        )

    def create_test_command(self):
        Command.objects.create(
            project=self.project,
            name="Test Command",
            command="echo 'Hello, World!'"
        )

    def test_project_not_found(self):
        response = self.client.get('/project/999/command/1/')
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)
        self.assertEqual(response.data['error'], "Project not found.")

        response = self.client.get('/project/1/command/999/')
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)
        self.assertEqual(response.data['error'], "Command not found for the given project.")

    def test_get_commands(self):
        self.create_test_command()

        response = self.client.get('/project/1/command/1/')
        self.assertEqual(response.status_code, 200)

        # Gathering expected data
        project = Project.objects.get(id=1)
        command = Command.objects.filter(project=project).first()
        serialized_command = CommandSerializer(command).data

        self.assertEqual(response.data, serialized_command)

    def test_patch_command(self):
        self.create_test_command()

        # First, test updating without changing any fields
        response = self.client.patch('/project/1/command/1/')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data['message'], "Nothing changed")

        # Now, test updating with a field change
        response = self.client.patch('/project/1/command/1/', {
            "name": "Updated Command Name"
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.data)

        command = Command.objects.get(id=1)
        self.assertEqual(command.name, "Updated Command Name")

    def test_delete_command(self):
        self.create_test_command()

        response = self.client.delete('/project/1/command/1/')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data['message'], "Command successfully deleted")

        # Verify the command is actually deleted
        with self.assertRaises(Command.DoesNotExist):
            Command.objects.get(id=1)

import os
from agent.project.command.models import Command
from agent.project.command.serializer import CommandSerializer


def register_command(serializer: CommandSerializer) -> Command:
    serialized_data = serializer.validated_data

    if cwd := serialized_data.get('cwd'):
        project_path = serialized_data['project'].path
        full_cwd = cwd if os.path.isabs(cwd) else os.path.join(project_path, cwd)

        if not os.path.exists(full_cwd):
            raise AssertionError(f'The directory "{full_cwd}" does not exist.')

        if not os.path.isdir(full_cwd):
            raise AssertionError(f'The path "{full_cwd}" is not a directory.')

    return serializer.save()


def modify_command(command: Command, data: dict) -> bool:
    something_changed = False

    def change_field(field_name):

        if value := data.get(field_name):
            if getattr(command, field_name) == value:
                return

            setattr(command, field_name, value)
            nonlocal something_changed
            something_changed = True

            if validate_func := locals().get(f'validate_{field_name}'):
                validate_func(value)

    fields: tuple = ('description', 'name', 'command', 'restart_command', 'cwd')

    for field in fields:
        change_field(field)

    if something_changed:
        command.save()

    return something_changed

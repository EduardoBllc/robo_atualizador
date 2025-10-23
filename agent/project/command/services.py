import os
from agent.project.command.models import Command


def modify_command(command: Command, data: dict):
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

    fields: tuple = ('description', 'name', 'command', 'restart_command')

    for field in fields:
        change_field(field)

    if something_changed:
        command.save()

    return something_changed

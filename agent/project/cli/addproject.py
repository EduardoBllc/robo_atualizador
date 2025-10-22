def prepare_project_register(args):
    from agent.project.serializer import ProjectSerializer
    from agent.project.services import register_project

    data = {}

    if name := args.name:
        data['name'] = name
    else:
        name = input("Enter the project name: ")
        data['name'] = (name or '').strip()

    if path := args.path:
        data['path'] = path
    else:
        path = input("Enter the project path: ")
        data['path'] = path

    if args.auto_update is not None:
        data['auto_update'] = args.auto_update
    else:
        auto_update_input = input("Enable automatic updates? (y/n) [y]: ").strip().lower()
        data['auto_update'] = (auto_update_input != 'n')

    if 'trunk_branch' in args and args.trunk_branch is not None:
        data['trunk_branch'] = args.trunk_branch

    if 'dev_branch' in args and args.dev_branch is not None:
        data['development_branch'] = args.dev_branch

    if 'homologation_branch' in args and args.homologation_branch is not None:
        data['homologation_branch'] = args.homologation_branch

    if 'production_branch' in args and args.production_branch is not None:
        data['production_branch'] = args.production_branch

    serializer = ProjectSerializer(data=data)

    if not serializer.is_valid():
        print("Invalid data provided:")
        for field, errors in serializer.errors.items():
            for error in errors:
                print(f" - {field}: {error}")
        return 1

    try:
        project = register_project(serializer)
        print(f"Project '{project.name}' registered successfully with ID {project.id}.")
        return 0
    except Exception as e:
        print(f"Failed to register project: {e}")
        return 1


def build_addproject_subparser(subparser):
    p_addproject = subparser.add_parser("addproject", help="Register a new project.")
    p_addproject.add_argument("-n", "--name",
                              type=str,
                              help="Name of the project.")
    p_addproject.add_argument("-p", "--path",
                              type=str,
                              help="Path to the project directory.")
    p_addproject.add_argument("--remote",
                              type=str,
                              help="Remote name for the project.")
    p_addproject.add_argument("--auto-update",
                              dest="auto_update",
                              action="store_true",
                              help="Enable automatic updates for the project.")
    p_addproject.set_defaults(func=prepare_project_register)


def run_update(args):
    from django.db.models import Q
    from agent.runner.services import update
    from agent.project.models import Project

    if project_id := args.project_id:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            print(f"Project with ID {project_id} does not exist.")
            return 1

        update(project)
    else:
        q_projects = Q()

        if not args.force:
            q_projects &= Q(auto_update=True)

        try:
            for project in Project.objects.filter(q_projects):
                if args.dry_run or args.verbose:
                    print(f"Updating project ID {project.id} at path {project.path}")

                    if args.dry_run:
                        continue

                if args.branch:
                    if project.active_branch != args.branch:
                        print(
                            f'Skipping project ID {project.id} as it is on branch {project.active_branch},'
                            f' not {args.branch}.'
                        )
                        continue

                update(project)

        except Exception as e:
            print(f"Update failed: {e}")
            return 1

    print("Update completed successfully.")
    return 0


def build_update_subparser(subparser):
    p_update = subparser.add_parser("update", help="Run an update.")
    p_update.add_argument("--branch",
                          type=str,
                          required=False,
                          help="Branch name.")
    p_update.add_argument("--remote",
                          type=str,
                          required=False,
                          help="Remote name.")
    p_update.add_argument("--force",
                          action="store_true",
                          help="Force the update (event if project auto_update configuration = False).")
    p_update.add_argument("--project-id",
                          type=int,
                          required=False,
                          help="Project ID to update.")
    p_update.add_argument("--dry-run",
                          action="store_true",
                          help="Perform a dry run without executing the update.")
    p_update.add_argument("--auto-stash",
                          action="store_true",
                          help="Automatically stash local changes before updating.")

    p_update.set_defaults(func=run_update)

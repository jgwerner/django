import logging
from django.contrib.auth import get_user_model
from projects.models import Project, ProjectFile
from teams.models import Team
log = logging.getLogger('projects')
User = get_user_model()


def run(files_list):

    for file_line in files_list:
        line = file_line['name']
        to_delete = not file_line['exists']
        path_parts = line.split("/")

        project_pk = path_parts[0]

        if project_pk == ".ssh":
            log.info("File watcher picked up the .ssh directory. Skipping it.")
            continue

        if line[:4].lower() == ".nfs":
            log.info("File watcher picked up nfs info as a project file. Skipping it.")
            continue
        project = Project.objects.get(pk=project_pk)
        author = project.owner.owner if isinstance(project.owner, Team) else project.owner

        if to_delete:
            proj_file = ProjectFile.objects.filter(author=author,
                                                   project=project,
                                                   file=line).first()
            if proj_file is None:
                log.warning("It seems like you're attempting to delete a file that doesn't"
                            "exist in the database anymore (or never did) {fname}".format(fname=line))
            else:
                log.info("Deleting file via Watchman: {pf}".format(pf=proj_file))
                proj_file.delete()
        else:
            proj_file, created = ProjectFile.objects.get_or_create(author=author,
                                                                   project=project,
                                                                   file=line)
            if created:
                log.info("Just created a file via Watchman: {pf}".format(pf=proj_file))
            else:
                log.info("File {pf} already exists in the database. Doing nothing.".format(pf=proj_file))

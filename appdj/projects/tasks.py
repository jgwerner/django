from celery import shared_task
from git import Repo


@shared_task()
def clone_git_repo(url, path):
    Repo.clone_from(url, path)

import logging
import base64
import os
from django.core.files.base import ContentFile, File

log = logging.getLogger('projects')


def get_files_from_request(request):
    django_files = []
    form_files = request.FILES.get("file") or request.FILES.getlist("files")
    b64_data = request.data.get("base64_data")
    path = request.data.get("path", "")

    if b64_data is not None:
        log.info("Base64 data uploaded.")

        # request.data.pop("base64_data")
        name = request.data.get("name")
        if name is None:
            log.warning("Base64 data was uploaded, but no name was provided")
            raise ValueError("When uploading base64 data, the 'name' field must be populated.")

        file_data = base64.b64decode(b64_data)
        form_files = [ContentFile(file_data, name=name)]

    if not isinstance(form_files, list):
        form_files = [form_files]

    for reg_file in form_files:
        new_name = os.path.join(path, reg_file.name)
        dj_file = File(file=reg_file, name=new_name)
        log.debug(dj_file.name)
        django_files.append(dj_file)

    return django_files

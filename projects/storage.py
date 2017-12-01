import errno
import os
import logging
from django.conf import settings
from django.core.files import File, locks
from django.core.files.move import file_move_safe
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import force_text
from django.utils.deconstruct import deconstructible
log = logging.getLogger('projects')


@deconstructible
class TbsStorage(FileSystemStorage):
    """
    This class is essentially a carbon copy of FileSystemStorage, except
    for the handling of files that already exist on disk. Sometimes it
    may be intentional that we're saving a file by a name that is already
    on disk. In that scenario we do nothing. This class is trimmed as much
    as possible, but the handling of certain exceptions does require some
    copy/pasting.
    """
    def _save(self, name, content):
        if not self.project_root_included:
            full_path = self.path(name)

            # Create any intermediate directories that do not exist.
            # Note that there is a race between os.path.exists and os.makedirs:
            # if os.makedirs fails with EEXIST, the directory was created
            # concurrently, and we can continue normally. Refs #16082.
            directory = os.path.dirname(full_path)
            if not os.path.exists(directory):
                try:
                    if self.directory_permissions_mode is not None:
                        # os.makedirs applies the global umask, so we reset it,
                        # for consistency with file_permissions_mode behavior.
                        old_umask = os.umask(0)
                        try:
                            os.makedirs(directory, self.directory_permissions_mode)
                        finally:
                            os.umask(old_umask)
                    else:
                        os.makedirs(directory)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
            if not os.path.isdir(directory):
                raise IOError("%s exists and is not a directory." % directory)

            # There's a potential race condition between get_available_name and
            # saving the file; it's possible that two threads might return the
            # same name, at which point all sorts of fun happens. So we need to
            # try to create the file, but if it already exists we have to go back
            # to get_available_name() and try again.

            while True:
                try:
                    # This file has a file path that we can move.
                    if hasattr(content, 'temporary_file_path'):
                        file_move_safe(content.temporary_file_path(), full_path)

                    # This is a normal uploadedfile that we can stream.
                    else:
                        # This fun binary flag incantation makes os.open throw an
                        # OSError if the file already exists before we open it.
                        flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                 getattr(os, 'O_BINARY', 0))
                        # The current umask value is masked out by os.open!
                        fd = os.open(full_path, flags, 0o666)
                        _file = None
                        try:
                            locks.lock(fd, locks.LOCK_EX)
                            for chunk in content.chunks():
                                if _file is None:
                                    mode = 'wb' if isinstance(chunk, bytes) else 'wt'
                                    _file = os.fdopen(fd, mode)
                                _file.write(chunk)
                        finally:
                            locks.unlock(fd)
                            if _file is not None:
                                _file.close()
                            else:
                                os.close(fd)
                except OSError as e:
                    if e.errno == errno.EEXIST:
                        # Ooops, the file exists.
                        # We're trying to "upload" a file that already exists,
                        # so do nothing. This happens thanks to some wonderful
                        # vagaries surrounding NFS and Jupyter notebooks.
                        # The likelihood of this race condition occurring is about
                        # 1 in 7 billion, and even lower when considering
                        # That files are scoped by project, and so on.
                        # Since this isn't a fighter jet or something, we're going to
                        # assume that the file on disk is indeed the one we intended to write.
                        log.warning(f"File {name} already exists on disk. It's almost certainly a file from"
                                    f" a jupyter notebook, but it is possible that a genuine race condition happened."
                                    f" Heres the stacktrace:")
                        log.exception(e)
                        break
                    else:
                        log.exception(e)
                        raise
                else:
                    # OK, the file save worked. Break out of the loop.
                    break

            if self.file_permissions_mode is not None:
                os.chmod(full_path, self.file_permissions_mode)

        # Store filenames with forward slashes, even on Windows.
        return force_text(name.replace('\\', '/'))

    def get_available_name(self, name, max_length=None):
        if self.exists(name) and self.project_root_included:
            log.info("Project root was included in the file's name. Not going to attempt"
                     " to generate a unique file name; assuming the file is already on disk."
                     " Instead, we simply remove settings.RESOUCE_DIR (probably /workspaces)"
                     " from the file name.")
            # We know the file exists, and we want it to be that name. Break the loop
            return name.replace(settings.RESOURCE_DIR + "/", "")
        else:
            return super(TbsStorage, self).get_available_name(name=name, max_length=max_length)

    def generate_filename(self, filename, project_root_included=False):
        """
        Validate the filename by calling get_valid_name() and return a filename
        to be passed to the save() method.
        """
        self.project_root_included = project_root_included
        # `filename` may include a path as returned by FileField.upload_to.
        dirname, filename = os.path.split(filename)
        return os.path.normpath(os.path.join(dirname, self.get_valid_name(filename)))

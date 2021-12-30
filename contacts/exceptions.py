import logging
import traceback


def get_exception_object(e):
    return {
        'exception': (
            'Internal server error. '
            'Please contact an administrator.'
        ),
        'stackTrace': traceback.format_tb(e.__traceback__)
    }


def log_exception(title, e):
    exception_object = get_exception_object(e)
    logging.error(title, exception_object)
    exception_object.pop('stackTrace')
    return {
        'status': 500,
        'title': title,
        'detail': exception_object,
        'type': None
    }


class VanityException(Exception):
    def __init__(self, title='', detail=None, status=None):
        self.title = title
        self.detail = None
        logmsg = '%s: %s' % (self.__class__.__name__, title)
        if isinstance(detail, list):
            self.detail = {
                'errors': detail
            }
        elif isinstance(detail, str):
            self.detail = {
                'errors': [detail]
            }
        elif isinstance(detail, Exception):
            self.detail = get_exception_object(detail)
        if self.detail is None:
            logging.error(logmsg)
        else:
            logging.error(logmsg, self.detail)
        self.status = status
        self.type = None

    def __str__(self):
        return self.title

    def to_problem(self):
        return {
            'status': self.status,
            'title': self.title,
            'detail': self.detail,
            'type': self.type
        }

    def to_response(self):
        return (self.to_problem(), self.status)


class RepositoryException(VanityException):
    def __init__(self, title='', detail=None, status=500):
        super(RepositoryException, self).__init__(
            title, detail, status=status
        )


class ItemNotFoundException(VanityException):
    def __init__(self, title='', detail=None, status=404):
        super(ItemNotFoundException, self).__init__(
            title, detail, status=status
        )

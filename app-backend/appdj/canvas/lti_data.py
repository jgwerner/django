from django.core import validators


VALID_ROLES = {
    'http://purl.imsglobal.org/vocab/lis/v2/system/person': [
        'Administrator', 'None', 'AccountAdmin', 'Creator',
        'SysAdmin', 'SysSupport', 'User',
    ],
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person': [
        'Administrator', 'Faculty', 'Guest', 'None', 'Other',
        'Staff', 'Student', 'Alumni', 'Instructor', 'Learner',
        'Member', 'Mentor', 'Observer', 'ProspectiveStudent',
    ],
    'http://purl.imsglobal.org/vocab/lis/v2/membership': [
        'Administrator', 'ContentDeveloper', 'Instructor',
        'Learner', 'Mentor', 'Manager', 'Member', 'Officer',
    ]
}


SHORT_ROLES = {role for _, typ_roles in VALID_ROLES.items() for role in typ_roles}


def check_roles(roles):
    if not roles:
        return
    for role in roles:
        if '#' not in role:
            if role not in SHORT_ROLES:
                raise ValueError("There is no such role")
        else:
            typ, rol, *_ = role.split('#')
            if typ not in VALID_ROLES or rol not in VALID_ROLES[typ]:
                raise ValueError(f"There is no role {role}")


def check_param(param):
    def check(value):
        if param not in value:
            raise ValueError(f"{param} is required")
    return check


REQUIRED = {
    # schema: claim: [vaild values or validators]
    'https://purl.imsglobal.org/spec/lti/claim/message_type': ['LtiResourceLinkRequest', 'LtiDeepLinkingRequest'],
    'https://purl.imsglobal.org/spec/lti/claim/version': ['1.3.0'],
    'https://purl.imsglobal.org/spec/lti/claim/deployment_id': [validators.MaxLengthValidator(256)],
    'sub': [validators.MaxLengthValidator(256)],
    'email': [validators.EmailValidator()],
    'https://purl.imsglobal.org/spec/lti/claim/roles': [check_roles]
}


OPTIONAL = {
    'https://purl.imsglobal.org/spec/lti/claim/target_link_uri': [validators.URLValidator()],
    'https://purl.imsglobal.org/spec/lti/claim/resource_link': [check_param('id')],
}

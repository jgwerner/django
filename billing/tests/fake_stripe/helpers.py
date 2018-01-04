import logging
import stripe
import inspect
import re
from billing import models


log = logging.getLogger('billing')

retrieve_regex = re.compile("stripe\.(\w)*\.retrieve\((.)*\)")


def convert_db_object_to_stripe_dict(db_object) -> dict:
    model_class = db_object.__class__
    retdict = {}

    non_relational = [f for f in model_class._meta.get_fields() if not f.is_relation]
    relational = [f for f in model_class._meta.get_fields() if f.is_relation and f.related_model == model_class]

    for field in non_relational:
        if field.name != "id":
            retdict[field.name] = getattr(db_object, field.name)

    for field in relational:
        log.debug((field.name, field.related_model, field.model))
        retdict[field.name] = getattr(db_object, field.name).stripe_id
    return retdict


def mock_stripe_retrieve(stripe_id: str) -> dict:
    cur_frame = inspect.currentframe()
    frames = inspect.getouterframes(cur_frame)

    caller = frames[2]
    code_context = [line.replace("\n", "").strip() for line in caller.code_context]
    log.debug(f"Lines of code in calling context: {code_context}")
    parts = []
    for line in code_context:
        parts.extend([token.strip() for token in line.split("=")])

    # Note: I'm just assuming there is only one retrieve call in the context for now.
    # Not entirely sure if that's true. I also don't know what will happen if it isn't true.
    retrieve_calls = list(filter(retrieve_regex.match, parts))
    log.debug(f"Retrieve calls")

    # I'm *pretty* sure, the [1] index will always be correct
    model_class_name = retrieve_calls[0].split(".")[1]
    log.debug(f"Model Class Name: {model_class_name}")

    model_class = getattr(models, model_class_name)
    db_object = model_class.objects.get(stripe_id=stripe_id)

    return convert_db_object_to_stripe_dict(db_object)


def signature_verification_error():
    return stripe.error.SignatureVerificationError("foo", "bar")

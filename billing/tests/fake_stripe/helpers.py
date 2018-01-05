import logging
import stripe
import inspect
import re
from billing import models


log = logging.getLogger('billing')

retrieve_regex = re.compile("stripe\.(\w)*\.retrieve\((.)*\)")
sources_retrieve_regex = re.compile("stripe_customer\.sources\.retrieve\(instance\.stripe_id\)")


def convert_db_object_to_stripe_dict(db_object) -> dict:
    model_class = db_object.__class__
    retdict = {}

    non_relational = [f for f in model_class._meta.get_fields() if not f.is_relation]
    relational = [f for f in model_class._meta.get_fields() if f.is_relation and hasattr(db_object, f.name)]

    for field in non_relational:
        if field.name != "id":
            retdict[field.name] = getattr(db_object, field.name)

    for field in relational:
        related_object = getattr(db_object, field.name)
        if hasattr(related_object, "stripe_id"):
            retdict[field.name] = related_object.stripe_id
    return retdict


def parse_code_context(frames) -> list:
    log.debug("Parsing the callstack")
    for frame in frames:
        this_code_context = [line.replace("\n", "").strip() for line in frame.code_context]
        parts = []
        for line in this_code_context:
            parts.extend([token.strip() for token in line.split("=")])
        retrieve_calls = list(filter(retrieve_regex.match, parts))
        if retrieve_calls:
            # If there is more than one retrieve call in the stack,
            # we only care about the most recent one anyhow
            log.debug(f"Found the retrieve call!")
            log.debug(f"Frame info:\n{frame}")
            return retrieve_calls
        sources_retrieve_calls = list(filter(sources_retrieve_regex.match, parts))
        if sources_retrieve_calls:
            log.debug(f"Found the retrieve call!")
            log.debug(f"Frame info:\n{frame}")
            return sources_retrieve_calls
    return []


def mock_stripe_retrieve(stripe_id: str) -> dict:
    cur_frame = inspect.currentframe()
    frames = inspect.getouterframes(cur_frame)
    retrieve_calls = parse_code_context(frames)

    log.debug(f"Retrieve calls:\n {retrieve_calls}")
    model_class_name = retrieve_calls[0].split(".")[1]
    log.debug(f"Model Class Name: {model_class_name}")

    model_class = getattr(models, model_class_name, models.Card)
    db_object = model_class.objects.get(stripe_id=stripe_id)

    return convert_db_object_to_stripe_dict(db_object)


def signature_verification_error():
    return stripe.error.SignatureVerificationError("foo", "bar")

import logging
from ftmstore import get_dataset

log = logging.getLogger(__name__)
MODEL_ORIGIN = "model"


def get_ftmstore_name(collection):
    return "collection_%s" % collection.id


def get_ftmstore(collection, origin="aleph"):
    """Connect to a followthemoney dataset."""
    dataset = get_ftmstore_name(collection)
    return get_dataset(dataset, origin=origin)

from banal import ensure_list
from ftmstore import get_dataset
from followthemoney import model
from followthemoney.types import registry
from followthemoney.exc import InvalidData
from followthemoney.helpers import remove_checksums

MODEL_ORIGIN = "model"


def get_ftmstore_name(collection):
    return "collection_%s" % collection.id


def get_ftmstore(collection, origin="aleph"):
    """Connect to a followthemoney dataset."""
    dataset = get_ftmstore_name(collection)
    return get_dataset(dataset, origin=origin)


def bulk_write_entities(collection, entities, safe=False, role_id=None, mutable=True):
    """Write a set of entities - given as dicts - to a collections ftmstore."""
    # This is called mainly by the /api/2/collections/X/_bulk API.
    ftmstore = get_ftmstore(collection)
    writer = ftmstore.bulk()
    for data in entities:
        entity = model.get_proxy(data, cleaned=False)
        entity = collection.ns.apply(entity)
        if entity.id is None:
            raise InvalidData("No ID for entity", errors=entity.to_dict())
        if safe:
            entity = remove_checksums(entity)
        entity.context = {"role_id": role_id, "mutable": mutable}
        for field, func in (("created_at", min), ("updated_at", max)):
            ts = func(ensure_list(data.get(field)), default=None)
            dt = registry.date.to_datetime(ts)
            if dt is not None:
                entity.context[field] = dt.isoformat()
        writer.put(entity, origin="bulk")
        yield entity.id
    writer.flush()

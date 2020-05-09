from collections import OrderedDict
from sys import version_info

from ..metadata import validate_metadata, value_at_key_path
from .dicts import freeze_object, merge_dict


class Metastack:
    def __init__(self):
        # We rely heavily on insertion order in this dict.
        if version_info < (3, 7):
            self._layers = OrderedDict()
        else:
            self._layers = {}

    def get(self, path, default, use_default=True):
        if not isinstance(path, (tuple, list)):
            path = path.split('/')

        result = None
        undef = True

        for layer in self._layers.values():
            try:
                value = value_at_key_path(layer, path)
            except KeyError:
                pass
            else:
                if undef:
                    # First time we see anything.
                    result = {'data': value}
                    undef = False
                else:
                    result = merge_dict(result, {'data': value})

        if undef:
            if use_default:
                return default
            else:
                raise MetastackKeyError('Path {} not in metastack'.format('/'.join(path)))
        else:
            return freeze_object(result['data'])

    def has(self, path):
        try:
            self.get(path, '<unused>', use_default=False)
        except MetastackKeyError:
            return False
        return True

    def _as_dict(self):
        final_dict = {}

        for layer in self._layers.values():
            final_dict = merge_dict(final_dict, layer)

        return final_dict

    def _as_blame(self):
        # TODO
        raise NotImplementedError

    def _set_layer(self, identifier, new_layer):
        # Marked with an underscore because only the internal metadata
        # reactor routing is supposed to call this method.
        validate_metadata(new_layer)
        changed = self._layers.get(identifier, {}) != new_layer
        self._layers[identifier] = new_layer
        return changed


class MetastackKeyError(Exception):
    pass

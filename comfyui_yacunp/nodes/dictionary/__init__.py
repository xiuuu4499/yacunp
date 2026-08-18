"""YACUNP Dictionary category nodes."""

from .combine_dictionaries import YacunpCombineDictionaries
from .format_text_with_dictionary import YacunpFormatTextWithDictionary
from .get_dictionary_keys import YacunpGetDictionaryKeys
from .get_dictionary_value import YacunpGetDictionaryValue
from .make_dictionary import YacunpMakeDictionary
from .make_kvpair import YacunpMakeKVPair
from .read_kvpair import YacunpReadKVPair
from .set_dictionary_value import YacunpSetDictionaryValue

NODES = [
    YacunpMakeKVPair,
    YacunpReadKVPair,
    YacunpMakeDictionary,
    YacunpGetDictionaryValue,
    YacunpGetDictionaryKeys,
    YacunpFormatTextWithDictionary,
    YacunpSetDictionaryValue,
    YacunpCombineDictionaries,
]

"""
charex
~~~~~~

Tools for exploring unicode characters and other character sets.
"""
from collections import defaultdict
from collections.abc import Generator, Sequence
from dataclasses import dataclass
from json import loads
import re
import unicodedata as ucd

from charex import util
from charex.escape import schemes


# Data classes.
@dataclass
class CaseFold:
    """A record in CaseFolding.txt.

    :param code: The address of the character.
    :param status: The type of casefold being defined.
    :param mapping: The casefolded character(s).
    """
    code: str
    status: str
    mapping: str


@dataclass
class NameAlias:
    """A record in NameAliases.txt.

    :param code: The address of the character.
    :param alias: The name alias for the character.
    :param type_: The type of name alias.
    """
    code: str
    alias: str
    type_: str

    def __str__(self) -> str:
        return f'<{self.type_}>{self.alias}'


@dataclass
class Property:
    alias: str
    long: str
    other: tuple[str, ...]


@dataclass
class PropertyValue:
    property: str
    alias: str
    long: str
    other: tuple[str, ...]


@dataclass
class SpecialCase:
    code: str
    lower: str
    title: str
    upper: str
    condition_list: str


@dataclass
class UCD:
    """A record from the UnicodeData.txt file for Unicode 14.0.0.

    :param code_point: The address for the character in Unicode.
    :param name: The name for the code point.
    :param category: The type of code point, such as "control" or
        "lower case letter."
    :param canonical_combining_class: The combining class of the code point,
        largely used for CJK languages.
    :param bidi_class: Unknown.
    :param decomposition_type: Whether and how the character can be
        decomposed.
    :param decimal: If the character is a decimal digit, this is its
        numeric value.
    :param digit: If the character is a digit, this is its numeric
        value.
    :param numeric: If the character is a number, this is its numeric
        value.
    :param bidi_mirrored: Unknown.
    :param unicode_1_name: The name of the character used in Unicode
        version 1. This is mainly needed to give names to control
        characters.
    :param iso_comment: Unknown.
    :param simple_uppercase_mapping: The code point for the upper case
        version of the code point.
    :param simple_lowercase_mapping: The code point for the lower case
        version of the code point.
    :param simple titlecase_mapping: The code point for the title case
        version of the code point.
    """
    address: str
    na: str
    gc: str
    ccc: str
    bc: str
    dt: str
    decimal: str
    digit: str
    nv: str
    bidi_m: str
    na1: str
    isc: str
    suc: str
    slc: str
    stc: str


@dataclass(order=True)
class ValueRange:
    """The range of characters that have a property value."""
    start: int
    stop: int
    value: str


# Types:
CaseFoldCache = defaultdict[str, tuple[CaseFold, ...]]
DenormalCache = dict[str, defaultdict[str, tuple[str, ...]]]
PropListCache = dict[str, defaultdict[str, bool]]
PropsCache = dict[str, Property]
PropValsCache = dict[str, dict[str, PropertyValue]]
MultiValCache = dict[str, defaultdict[str, tuple[str, ...]]]
NameAliasCache = defaultdict[str, tuple[NameAlias, ...]]
RangeListCache = dict[str, tuple[ValueRange, ...]]
Records = tuple[tuple[str, ...], ...]
SimpleListCache = dict[str, tuple[str, ...]]
SingleValCache = dict[str, defaultdict[str, str]]
SpecCaseCache = defaultdict[str, tuple[SpecialCase, ...]]
UnicodeDataCache = dict[str, UCD]


# Default values for defaultdicts.
class MissingBool:
    def __init__(self, value: bool) -> None:
        self.value = value

    def __call__(self) -> bool:
        return self.value


class MissingCaseFold:
    def __init__(self, value: tuple[CaseFold, ...]) -> None:
        self.value = value

    def __call__(self) -> tuple[CaseFold, ...]:
        return self.value


class MissingSpecialCase:
    def __init__(self, value: tuple[SpecialCase, ...]) -> None:
        self.value = value

    def __call__(self) -> tuple[SpecialCase, ...]:
        return self.value


class MissingTuple:
    def __init__(self, value: tuple[str, ...]) -> None:
        self.value = value

    def __call__(self) -> tuple[str, ...]:
        return self.value


class MissingValue:
    def __init__(self, value: str) -> None:
        self.value = value

    def __call__(self) -> str:
        return self.value


# Classes.
class Cache:
    """Data caching mechanism for :mod:`charex`. This is used to
    reduce the number of times data needs to be loaded from disk.
    It shouldn't be called directly. It's intended to be used
    through :class:`charex.Character`.
    """
    forms = ('casefold', 'nfc', 'nfd', 'nfkc', 'nfkd')
    multis = ('scx',)
    ranges = ('age', 'blk', 'sc',)
    simples = ('ce',)
    singles = (
        'bmg', 'ea', 'equideo', 'gcb', 'hst', 'inpc', 'insc', 'jg', 'jsn',
        'jt', 'lb', 'sb', 'vo', 'wb',
    )
    scases = ('lc', 'tc', 'uc',)

    def __init__(self) -> None:
        mvalue_cf = MissingCaseFold((CaseFold('<self>', 'C', '<self>'),))
        mvalue_sc = MissingSpecialCase((SpecialCase(
            '<self>',
            '<slc>',
            '<stc>',
            '<suc>',
            ''
        ),))
        self.__casefold: CaseFoldCache = defaultdict(mvalue_cf)
        self.__denormal: DenormalCache = {}
        self.__emoji: SimpleListCache = {}
        self.__multival: MultiValCache = {}
        self.__namealias: NameAliasCache = defaultdict(tuple)
        self.__normalsimplelist: SimpleListCache = {}
        self.__normalsingleval: SingleValCache = {}
        self.__proplist: SingleValCache = {}
        self.__props: PropsCache = {}
        self.__propvals: PropValsCache = {}
        self.__rangelist: RangeListCache = {}
        self.__simplelist: SimpleListCache = {}
        self.__singleval: SingleValCache = {}
        self.__speccase: SpecCaseCache = defaultdict(mvalue_sc)
        self.__unicodedata: UnicodeDataCache = {}

    @property
    def casefold(self) -> CaseFoldCache:
        if not self.__casefold:
            data = self.parse('cf')
            casefold: dict[str, list[CaseFold]] = {}
            for item in data:
                code, status, mapping, _ = item
                n = int(code, 16)
                c = chr(n)
                casefold.setdefault(c, list())
                casefold[c].append(CaseFold(code, status, mapping))
            for c in casefold:
                self.__casefold[c] = tuple(casefold[c])
        return self.__casefold

    @property
    def denormal(self) -> DenormalCache:
        if not self.__denormal:
            for form in self.forms:
                source = f'rev_{form}'
                lines = util.read_resource(source)
                json = '\n'.join(lines)
                data = loads(json)
                result = defaultdict(tuple)
                for key in data:
                    result[key] = tuple(data[key])
                self.__denormal[form] = result
        return self.__denormal

    @property
    def emoji(self) -> SimpleListCache:
        if not self.__emoji:
            self.__emoji = self.get_emoji()
        return self.__emoji

    @property
    def multival(self) -> MultiValCache:
        if not self.__multival:
            self.__multival = {
                key: self.get_multiple_value_property(key)
                for key in self.multis
            }
        return self.__multival

    @property
    def namealias(self) -> NameAliasCache:
        if not self.__namealias:
            data = self.parse('name_alias')
            namealias: dict[str, list[NameAlias]] = {}
            for item in data:
                code, alias, type_ = item
                n = int(code, 16)
                c = chr(n)
                namealias.setdefault(c, list())
                namealias[c].append(NameAlias(code, alias, type_))
            for c in namealias:
                self.__namealias[c] = tuple(namealias[c])
        return self.__namealias

    @property
    def normalsimplelist(self) -> SimpleListCache:
        if not self.__normalsimplelist:
            self.__normalsimplelist = self.get_normalprops()[0]
        return self.__normalsimplelist

    @property
    def normalsingleval(self) -> SingleValCache:
        if not self.__normalsingleval:
            self.__normalsingleval = self.get_normalprops()[1]
        return self.__normalsingleval

    @property
    def props(self) -> PropsCache:
        if not self.__props:
            self.__props = self.get_properties()
        return self.__props

    @property
    def proplist(self) -> SingleValCache:
        if not self.__proplist:
            proplist = self.parse_binary_properties('proplist')
            for prop in proplist:
                alias = alias_property(prop, True)
                alias = alias.casefold()
                self.__proplist[alias] = proplist[prop]

            dproplist = self.parse_binary_properties('dproplist')
            for prop in dproplist:
                alias = alias_property(prop, True)
                alias = alias.casefold()
                self.__proplist[alias] = dproplist[prop]

        return self.__proplist

    @property
    def propvals(self) -> PropValsCache:
        if not self.__propvals:
            self.__propvals = self.get_property_values()
        return self.__propvals

    @property
    def rangelist(self) -> RangeListCache:
        if not self.__rangelist:
            self.__rangelist = {
                key: self.get_value_ranges(key)
                for key in self.ranges
            }
        return self.__rangelist

    @property
    def simplelist(self) -> SimpleListCache:
        if not self.__simplelist:
            for source in self.simples:
                data = self.parse(source)
                values = self.parse_simple_ranges(data)
                self.__simplelist[source] = values
        return self.__simplelist

    @property
    def singleval(self) -> SingleValCache:
        if not self.__singleval:
            self.__singleval = {
                key: self.get_single_value_property(key)
                for key in self.singles
            }
        return self.__singleval

    @property
    def speccase(self) -> SpecCaseCache:
        if not self.__speccase:
            data = self.parse('speccase')
            result: dict[str, list[SpecialCase]] = {}
            for item in data:
                code, lc, tc, uc, conds, *_ = item
                n = int(code, 16)
                c = chr(n)
                sc = SpecialCase(code, lc, tc, uc, conds)
                result.setdefault(c, list())
                result[c].append(sc)
            for c in result:
                self.__speccase[c] = tuple(result[c])
        return self.__speccase

    @property
    def unicodedata(self) -> UnicodeDataCache:
        if not self.__unicodedata:
            lines = util.read_resource('unicodedata')
            data: dict[str, UCD] = {}
            for i, line in enumerate(lines):
                fields = line.split(';')
                datum = UCD(*fields)
                n = int(datum.address, 16)
                data[chr(n)] = datum

                if (
                    datum.na.startswith('<')
                    and datum.na.endswith('First>')
                ):
                    nextline = lines[i + 1]
                    next_fields = nextline.split(';')
                    start = int(datum.address, 16)
                    stop = int(next_fields[0], 16) + 1
                    for n in range(start, stop):
                        gap_fields = (f'{n:04x}'.upper(), *fields[1:])
                        datum = UCD(*gap_fields)
                        n = int(datum.address, 16)
                        data[chr(n)] = datum

            self.__unicodedata = data
        return self.__unicodedata

    def alias_property(self, prop: str) -> str:
        prop = prop.casefold()
        return self.props[prop].alias

    def alias_property_value(self, prop: str, value: str) -> str:
        if not value:
            return value
        prop = prop.casefold()
        if prop in self.propvals:
            value = self.propvals[prop][value.casefold()].alias
        return value

    def get_emoji(self) -> SimpleListCache:
        lines = util.read_resource('emoji')
        docs: list[list[str]] = []
        doc: list[str] = list()
        for line in lines:
            if line.startswith('# ====='):
                docs.append(doc)
                doc = list()
            doc.append(line)
        else:
            docs.append(doc)

        simples: SimpleListCache = {}
        for doc in docs:
            lines = self.strip_comments(doc)
            if not lines:
                continue
            data = self.parse_sdt(lines)

            prop = data[0][1].casefold()
            prop = self.alias_property(prop)

            result = self.parse_simple_ranges(data)
            simples[prop.casefold()] = tuple(result)
        return simples

    def get_multiple_value_property(
        self,
        source: str
    ) -> defaultdict[str, tuple[str, ...]]:
        missing, data = self.parse_with_missing(source)
        mvalue = MissingTuple(tuple(missing.split()))
        values: defaultdict[str, tuple[str, ...]] = defaultdict(mvalue)
        for datum in data:
            points, value = datum
            parts = points.split('..')
            start = int(parts[0], 16)
            stop = start + 1
            if len(parts) > 1:
                stop = int(parts[1], 16) + 1
            for i in range(start, stop):
                values[chr(i)] = tuple(value.split())
        return values

    def get_normalprops(self) -> tuple[SimpleListCache, SingleValCache]:
        lines = util.read_resource('dnormprops')
        docs: list[list[str]] = []
        buffer: list[str] = []
        for line in lines:
            if 'property:' in line.casefold():
                docs.append(buffer)
                buffer = list()
            buffer.append(line)
        else:
            docs.append(buffer)

        simples: SimpleListCache = {}
        singles: SingleValCache = {}
        for doc in docs:
            mline = self.parse_missing(doc)
            lines = self.strip_comments(doc)
            if not lines:
                continue

            data = self.parse_sdt(lines)
            prop = data[0][1].casefold()
            prop = self.alias_property(prop)

            mvalue = ''
            if mline:
                mvalue = mline[0][-1]
                mvalue = self.alias_property_value(prop, mvalue)

            if len(data[0]) == 3:
                data = tuple((item[0], item[2]) for item in data)
                singles[prop.casefold()] = self.parse_single(
                    data, mvalue, prop
                )
            else:
                result = self.parse_simple_ranges(data)
                simples[prop.casefold()] = tuple(result)
        return simples, singles

    def get_properties(self) -> PropsCache:
        data = self.parse('props')
        result: PropsCache = {}
        for datum in data:
            alias, long, *other = datum
            prop = Property(alias, long, tuple(other))
            for name in datum:
                result[name.casefold()] = prop
        return result

    def get_property_values(self) -> PropValsCache:
        data = self.parse('propvals')
        result: PropValsCache = {}
        for datum in data:
            prop, *names = datum
            alias, long, *other = names
            propval = PropertyValue(prop, alias, long, tuple(other))
            prop = prop.casefold()
            result.setdefault(prop, dict())
            for name in names:
                result[prop][name.casefold()] = propval
        return result

    def get_value_ranges(self, src: str) -> tuple[ValueRange, ...]:
        """Get the tuple of derived ages. The derived age of a character
        is the Unicode version where the character was assigned to a code
        point.

        :param src: The source key for the values.
        :return: The possible ages as a :class:`tuple`.
        :rtype: tuple
        """
        results = (ValueRange(*vr) for vr in self.parse_range_for_value(src))
        return tuple(results)

    def get_single_value_property(self, source: str) -> defaultdict[str, str]:
        missing, data = self.parse_with_missing(source)
        missing = self.alias_property_value(source, missing)
        mvalue = MissingValue(missing)
        return self.parse_single(data, missing, source)

    def parse(self, source: str) -> tuple[tuple[str, ...], ...]:
        lines = util.read_resource(source)
        lines = self.strip_comments(lines)
        data = self.parse_sdt(lines)
        return data

    def parse_binary_properties(
        self,
        source: str
    ) -> SingleValCache:
        data = self.parse(source)
        missing = MissingValue('N')
        result: SingleValCache = {}
        for datum in data:
            try:
                point, key = datum
            except ValueError:
                raise ValueError(datum)
            if key not in result:
                result[key] = defaultdict(missing)
            parts = point.split('..')
            start = int(parts[0], 16)
            stop = start + 1
            if len(parts) > 1:
                stop = int(parts[1], 16) + 1
            for i in range(start, stop):
                result[key][chr(i)] = 'Y'

        return result

    def parse_docs(self, source: str) -> tuple[tuple[str, ...], ...]:
        lines = util.read_resource(source)
        text = '\n'.join(lines)
        docs = text.split(
            '# ================================================'
        )
        return tuple(tuple(doc.split('\n')) for doc in docs)

    def parse_missing(
        self,
        lines: Sequence[str]
    ) -> tuple[tuple[str, ...], ...]:
        prefix = '# @missing: '
        lines = [line[12:] for line in lines if line.startswith(prefix)]
        lines = self.strip_comments(lines)
        return self.parse_sdt(lines)

    def parse_simple_ranges(
        self,
        data: tuple[tuple[str, ...], ...]
    ) -> tuple[str, ...]:
        result = list()
        for points, *_ in data:
            parts = points.split('..')
            start = int(parts[0], 16)
            stop = start + 1
            if len(parts) > 1:
                stop = int(parts[1], 16) + 1
            for i in range(start, stop):
                result.append(f'{i:04x}'.casefold())
        return tuple(result)

    def parse_range_for_value(
        self,
        source: str
    ) -> tuple[tuple[int, int, str], ...]:
        missing, data = self.parse_with_missing(source)
        values = []
        for datum in data:
            parts = datum[0].split('..')
            start = int(parts[0], 16)
            stop = start + 1
            if len(parts) > 1:
                stop = int(parts[1], 16) + 1
            value = (start, stop, datum[1])
            values.append(value)
        return tuple(fill_gaps(values, missing))

    def parse_sdt(
        self,
        lines: tuple[str, ...]
    ) -> tuple[tuple[str, ...], ...]:
        """Parse semicolon delimited text.

        :param lines: The lines from a semicolon delimited test file.
        :return: The lines split into data fields as a :class:`tuple`.
        :rtype: tuple
        """
        result = []
        for line in lines:
            parts = line.split(';')
            fields = (part.strip() for part in parts)
            result.append(tuple(fields))
        return tuple(result)

    def parse_single(
        self,
        data: Records,
        missing: str,
        source: str
    ) -> defaultdict[str, str]:
        mvalue = MissingValue(missing)
        result = defaultdict(mvalue)
        for datum in data:
            points, value = datum
            parts = points.split('..')
            start = int(parts[0], 16)
            stop = start + 1
            if len(parts) > 1:
                stop = int(parts[1], 16) + 1
            for i in range(start, stop):
                result[chr(i)] = self.alias_property_value(source, value)
        return result

    def parse_with_missing(
        self,
        source: str
    ) -> tuple[str, tuple[tuple[str, ...], ...]]:
        lines = util.read_resource(source)

        missing_data = self.parse_missing(lines)
        missing = ''
        if missing_data:
            missing = missing_data[0][-1]

        lines = self.strip_comments(lines)
        data = self.parse_sdt(lines)
        return missing, data

    def strip_comments(self, lines: Sequence[str]) -> tuple[str, ...]:
        """Remove the comments and blank lines from a data file.

        :param lines: The lines from a Unicode data file.
        :return: The lines with comments removed as a :class:`tuple`.
        :rtype: tuple
        """
        lines = [line.split('#')[0] for line in lines]
        return tuple([
            line for line in lines
            if line.strip() and not line.startswith('#')
        ])


class Character:
    """A Unicode character.

    :param value: A character address string for the Unicode
        character. See below.
    :return: The character as a :class:`charex.Character`.
    :rtype: charex.Character

    Address Formats
    ---------------
    The understood str-based formats for manual input of addresses are:

    *   Character: A string with length equal to one.
    *   Code Point: The prefix "U+" followed by a hexadecimal number.
    *   Binary String: The prefix "0b" followed by a binary number.
    *   Hex String: The prefix "0x" followed by a hexadecimal number.

    The following formats are available for use through the API:

    *   Bytes: A :class:`bytes`.
    *   Integer: An :class:`int`.

    Usage
    -----
    To create a :class:`charex.Character` object for a single
    character string::

        >>> value = 'a'
        >>> char = Character(value)
        >>> char.value
        'a'

    To create a :class:`charex.Character` object for a Unicode code
    point::

        >>> value = 'U+0061'
        >>> char = Character(value)
        >>> char.value
        'a'

    To create a :class:`charex.Character` object for a binary string::

        >>> value = '0b01100001'
        >>> char = Character(value)
        >>> char.value
        'a'

    To create a :class:`charex.Character` object for an octal string::

        >>> value = '0o141'
        >>> char = Character(value)
        >>> char.value
        'a'

    To create a :class:`charex.Character` object for a decimal string::

        >>> value = '0d97'
        >>> char = Character(value)
        >>> char.value
        'a'

    To create a :class:`charex.Character` object for a hex string::

        >>> value = '0x61'
        >>> char = Character(value)
        >>> char.value
        'a'

    Beyond the declared properties and methods described below, most
    Unicode properties for the character are available by calling
    their alias as a property of :class:`charex.Character`::

        >>> value = 'a'
        >>> char = Character(value)
        >>> char.na
        'LATIN SMALL LETTER A'
        >>> char.blk
        'Basic Latin'
        >>> char.sc
        'Latin'
        >>> char.suc
        '0041'

    """
    cache = Cache()

    def __init__(self, value: bytes | int | str) -> None:
        value = util.to_char(value)
        self.__value = value
        self._rev_normal_cache: dict[str, tuple[str, ...]] = {}

    def __getattr__(self, name):
        name = name.casefold()

        if name in UCD.__annotations__:
            try:
                data = self.cache.unicodedata
                return getattr(data[self.value], name)

            # There are a few undefined characters in the Unicode
            # data file. The code points still exist, but they
            # don't have properties.
            except KeyError:
                return ''

        if name in self.cache.proplist:
            return self.cache.proplist[name][self.value]

        if name in self.cache.ranges:
            rangelist = self.cache.rangelist[name]
            vr = bintree(
                rangelist,
                ord(self.value),
                len(rangelist) // 2,
                0,
                len(rangelist)
            )
            return vr.value

        if name in self.cache.multis:
            multival = self.cache.multival[name]
            value = multival[self.value]
            value = self._handle_dynamic_value(name, value)
            return value

        if name in self.cache.singles:
            singleval = self.cache.singleval[name]
            value = singleval[self.value]
            return value

        if name in self.cache.simples:
            simplelist = self.cache.simplelist[name]
            address = self.code_point[2:]
            if address in simplelist:
                return 'Y'
            return 'N'

        if name in self.cache.normalsimplelist:
            simplelist = self.cache.normalsimplelist[name]
            address = self.code_point[2:].casefold()
            if address in simplelist:
                return 'Y'
            return 'N'

        if name in self.cache.normalsingleval:
            singleval = self.cache.normalsingleval[name]
            value = singleval[self.value]
            if value == '<code point>':
                value = self.code_point[2:]
            return value

        if name in self.cache.emoji:
            emoji = self.cache.emoji[name]
            address = self.code_point[2:].casefold()
            if address in emoji:
                return 'Y'
            return 'N'

        raise AttributeError(name)

    def __repr__(self) -> str:
        name = self.na
        if name == '<control>':
            name = f'<{self.na1}>'
        return f'{self.code_point} ({name})'

    # Private methods.
    def _handle_dynamic_value(
        self,
        prop: str,
        values: Sequence[str]
    ) -> tuple[str, ...]:
        result = []
        for value in values:
            if value.startswith('<') and value.endswith('>'):
                attr = self.cache.alias_property(value[1:-1])
                value = getattr(self, attr.casefold())
            result.append(value)
        return tuple(result)

    # Derived properties.
    @property
    def bpb(self) -> str:
        """For an opening bracket, the code point of the matching
        closing bracket. For a closing bracket, the code point of
        the matching opening bracket. This property is used in the
        implementation of parenthesis matching. See Unicode Standard
        Annex #9, "Unicode Bidirectional Algorithm" [UAX9].
        """
        bpb = '<none>'
        if self.bpt != 'n':
            bpb = self.bmg
        return bpb

    @property
    def bpt(self) -> str:
        """Type of a paired bracket, either opening or closing. This
        property is used in the implementation of parenthesis matching.
        See Unicode Standard Annex #9, "Unicode Bidirectional Algorithm"
        [UAX9].
        """
        bpt = 'n'
        if self.bc == 'ON' and self.bidi_m == 'Y':
            if self.gc == 'Ps':
                bpt = 'o'
            elif self.gc == 'Pe':
                bpt = 'c'
        return bpt

    @property
    def cf(self) -> str:
        """Mapping from characters to their case-folded forms. This is
        an informative file containing normative derived properties.
        Derived from UnicodeData and SpecialCasing.
        """
        data = self.cache.casefold
        options = {cf.status: cf for cf in data[self.value]}
        if 'F' in options:
            value = options['F'].mapping
        elif 'C' in options and options['C'].mapping == '<self>':
            value = f'{self.code_point[2:]}'
        else:
            value = options['C'].mapping
        return value

    @property
    def lc(self) -> str:
        cases = self.cache.speccase[self.value]
        values = []
        for case_ in cases:
            code = case_.lower
            if code.startswith('<') and code.endswith('>'):
                code = getattr(self, code[1:-1])
                if not code:
                    code = self.code_point[2:]
            cond = case_.condition_list
            if cond:
                cond = f'({cond})'
            values.append(f'{cond}{code}')
        return ';'.join(values)

    @property
    def scf(self) -> str:
        """Mapping from characters to their case-folded forms. This is
        an informative file containing normative derived properties.
        Derived from UnicodeData and SpecialCasing.
        """
        data = self.cache.casefold
        options = {cf.status: cf for cf in data[self.value]}
        if 'S' in options:
            return options['S'].mapping
        elif 'C' in options and options['C'].mapping == '<self>':
            return f'{self.code_point[2:]}'
        else:
            return options['C'].mapping

    @property
    def tc(self) -> str:
        cases = self.cache.speccase[self.value]
        values = []
        for case_ in cases:
            code = case_.title
            if code.startswith('<') and code.endswith('>'):
                code = getattr(self, code[1:-1])
                if not code:
                    code = self.code_point[2:]
            cond = case_.condition_list
            if cond:
                cond = f'({cond})'
            values.append(f'{cond}{code}')
        return ';'.join(values)

    @property
    def uc(self) -> str:
        cases = self.cache.speccase[self.value]
        values = []
        for case_ in cases:
            code = case_.upper
            if code.startswith('<') and code.endswith('>'):
                code = getattr(self, code[1:-1])
                if not code:
                    code = self.code_point[2:]
            cond = case_.condition_list
            if cond:
                cond = f'({cond})'
            values.append(f'{cond}{code}')
        return ';'.join(values)

    # Properties.
    @property
    def name_alias(self) -> str:
        return ' '.join(f'{a}' for a in self.cache.namealias[self.value])

    @property
    def code_point(self) -> str:
        """The address for the character in the Unicode database."""
        x = ord(self.value)
        return f'U+{x:04x}'.upper()

    @property
    def value(self) -> str:
        """The Unicode character as a string."""
        return self.__value

    # Public methods.
    def denormalize(self, form: str) -> tuple[str, ...]:
        """Return the characters that normalize to the character using
        the given form.

        :param form: The normalization form to check against.
        :return: The denormalization results in a :class:`tuple`.
        :rtype: tuple

        Usage
        -----
        To denormalize the character for the given form::

            >>> # Create the character object.
            >>> value = '<'
            >>> char = Character(value)
            >>>
            >>> # Get the denormalizations for the character.
            >>> form = 'nfkc'
            >>> char.denormalize(form)
            ('﹤', '＜')

        """
        return self.cache.denormal[form][self.value]

    def escape(self, scheme: str, codec: str = 'utf8') -> str:
        """The escaped version of the character.

        :param scheme: The escape scheme to use.
        :param codec: The codec to use when escaping to a hexadecimal
            string.
        :return: A :class:`str` with the escaped character.
        :rtype: str

        Usage
        -----
        To escape the character with the given form::

            >>> value = '<'
            >>> char = Character(value)
            >>>
            >>> scheme = 'html'
            >>> char.escape(scheme)
            '&lt;'

        """
        try:
            scheme = scheme.casefold()
            fn = schemes[scheme]
            return fn(self.value, codec)

        # UTF-16 surrogates will error when anything tries to
        # encode them as UTF-8.
        except UnicodeEncodeError:
            return ''

    def encode(self, codec: str) -> str:
        """The hexadecimal value for the character in the given
        character set.

        :param codec: The codec to use when encoding to a hexadecimal
            string.
        :return: A :class:`str` with the encoded character.
        :rtype: str

        Usage
        -----
        To encode the character with the given character set::

            >>> value = 'å'
            >>> char = Character(value)
            >>>
            >>> codec = 'utf8'
            >>> char.encode(codec)
            'C3 A5'

        """
        try:
            b = self.value.encode(codec)
            hexes = [f'{x:02x}'.upper() for x in b]
            return ' '.join(x for x in hexes)

        # UTF-16 surrogates will error when anything tries to
        # encode them as UTF-8.
        except UnicodeEncodeError:
            return ''

    def is_normal(self, form: str) -> bool:
        """Is the character normalized to the given form?

        :param form: The normalization form to check against.
        :return: A :class:`bool` indicating whether the character is
            normalized.
        :rtype: bool

        Usage
        -----
        To determine whether the character is already normalized for
        the given scheme.

            >>> value = 'å'
            >>> char = Character(value)
            >>>
            >>> form = 'nfc'
            >>> char.is_normal(form)
            True

        """
        return ucd.is_normalized(form.upper(), self.value)

    def normalize(self, form: str) -> str:
        """Normalize the character using the given form.

        :param form: The normalization form to check against.
        :return: The normalization result as a :class:`str`.
        :rtype: str

        Usage
        -----
        To normalize the character for the given form::

            >>> value = '＜'
            >>> char = Character(value)
            >>>
            >>> form = 'nfkc'
            >>> char.normalize(form)
            '<'

        """
        return ucd.normalize(form.upper(), self.value)

    def summarize(self) -> str:
        """Return a summary of the character's information.

        :return: The character information as a :class:`str`.
        :rtype: str

        Usage
        -----
        To summarize the character::

            >>> value = 'å'
            >>> char = Character(value)
            >>>
            >>> char.summarize()
            'å U+00E5 (LATIN SMALL LETTER A WITH RING ABOVE)'
        """
        value = util.neutralize_control_characters(self.value)
        return f'{value} {self!r}'


# Utility functions.
def alias_property(longname: str, space: bool = True) -> str:
    if space:
        longname = longname.replace(' ', '_')
    return Character.cache.props[longname.casefold()].alias


def bintree(
    vranges: Sequence[ValueRange],
    address: int,
    index: int,
    min_: int,
    max_: int
) -> ValueRange:
    """Find the range of a Unicode character using a binary
    tree search.

    :param vranges: The possible ranges for Unicode characters.
    :param address: The code point of the character an an :class:`int`.
    :param index: The current location of the search cursor.
    :param min_: The minimum possible index within ages that hasn't been
        excluded by the search.
    :param max_: The maximum possible index within ages that hasn't been
        excluded by the search.
    :return: The range of the character as a
        :class:`charex.charex.ValueRange`.
    :rtype: charex.charex.ValueRange
    """
    vr = vranges[index]
    if address < vr.start:
        max_ = index
        index = min_ + (max_ - min_) // 2
        vr = bintree(vranges, address, index, min_, max_)
    elif address >= vr.stop:
        min_ = index
        index = min_ + (max_ - min_) // 2
        vr = bintree(vranges, address, index, min_, max_)
    return vr


def expand_property(prop: str) -> str:
    """Translate the short name of a Unicode property into the long
    name for that property.

    :param prop: The short name of the property.
    :return: The long name as a :class:`str`.
    :rtype: str

    Usage
    -----
    To get the long name of a Unicode property.

        >>> prop = 'cf'
        >>> expand_property(prop)
        'Case Folding'

    """
    long = Character.cache.props[prop.casefold()].long
    long = long.replace('_', ' ')
    return long


def expand_property_value(prop: str, alias: str) -> str:
    """Translate the short name of a Unicode property value into the
    long name for that property.

    :param prop: The type of property.
    :param alias: The short name to translate.
    :return: The long name of the property as a :class:`str`.
    :rtype: str

    Usage
    -----
    To get the long name for a property value::

        >>> alias = 'Cc'
        >>> prop = 'gc'
        >>> expand_property_value(prop, alias)
        'Control'

    """
    prop = prop.casefold()
    alias = alias.casefold()
    long = Character.cache.propvals[prop][alias].long
    return long.replace('_', ' ')


def fill_gaps(
    values: Sequence[tuple[int, int, str]],
    missing: str
) -> tuple[tuple[int, int, str], ...]:
    """Fill gaps in the given values."""
    values = sorted(values)
    filled = []
    for i in range(len(values) - 1):
        filled.append(values[i])
        _, stop, _ = values[i]
        nstart, _, _ = values[i + 1]
        if stop != nstart:
            gap = (stop, nstart, missing)
            filled.append(gap)
    filled.append(values[-1])
    if filled[-1][1] != util.LEN_UNICODE:
        gap = (filled[-1][1], util.LEN_UNICODE, missing)
        filled.append(gap)
    return tuple(filled)


def filter_by_property(
    prop: str,
    value: str,
    chars: Sequence[Character] | None = None,
    insensitive: bool = False,
    regex: bool = False
) -> Generator[Character, None, None]:
    """Return all the characters with the given property value.

    :param prop: The property to filter on.
    :param value: The pattern to filter on.
    :param chars: (Optional.) The characters to filter. Defaults
        to filtering all Unicode characters.
    :param insensitive: (Optional.) Whether the matching should
        be case insensitive. Defaults to false.
    :param regex: (Optional.) Whether the value should be used as a
        regular expression for the matching. Defaults to false.
    :return: the filtered characters as a
        :class:`collections.abc.Generator`.
    :rtype: collections.abc.Generator

    Usage
    -----
    To get a generator that produces the Emoji modifiers::

        >>> prop = 'emod'
        >>> value = 'Y'
        >>> gen = filter_by_property(prop, value)
        >>> for char in gen:
        ...     print(char.summarize())
        ...
        🏻 U+1F3FB (EMOJI MODIFIER FITZPATRICK TYPE-1-2)
        🏼 U+1F3FC (EMOJI MODIFIER FITZPATRICK TYPE-3)
        🏽 U+1F3FD (EMOJI MODIFIER FITZPATRICK TYPE-4)
        🏾 U+1F3FE (EMOJI MODIFIER FITZPATRICK TYPE-5)
        🏿 U+1F3FF (EMOJI MODIFIER FITZPATRICK TYPE-6)

    You can limit the number of characters being searched with the
    `chars` parameter::

        >>> prop = 'gc'
        >>> value = 'Cc'
        >>> chars = [Character(chr(n)) for n in range(128)]
        >>> gen = filter_by_property(prop, value, chars)
        >>> for char in gen:
        ...     print(char.summarize())
        ...
        ␀ U+0000 (<NULL>)
        ␁ U+0001 (<START OF HEADING>)
        ␂ U+0002 (<START OF TEXT>)
        ␃ U+0003 (<END OF TEXT>)
        ␄ U+0004 (<END OF TRANSMISSION>)
        ␅ U+0005 (<ENQUIRY>)
        ␆ U+0006 (<ACKNOWLEDGE>)
        ␇ U+0007 (<BELL>)
        ␈ U+0008 (<BACKSPACE>)
        ␉ U+0009 (<CHARACTER TABULATION>)
        ␊ U+000A (<LINE FEED (LF)>)
        ␋ U+000B (<LINE TABULATION>)
        ␌ U+000C (<FORM FEED (FF)>)
        ␍ U+000D (<CARRIAGE RETURN (CR)>)
        ␎ U+000E (<SHIFT OUT>)
        ␏ U+000F (<SHIFT IN>)
        ␐ U+0010 (<DATA LINK ESCAPE>)
        ␑ U+0011 (<DEVICE CONTROL ONE>)
        ␒ U+0012 (<DEVICE CONTROL TWO>)
        ␓ U+0013 (<DEVICE CONTROL THREE>)
        ␔ U+0014 (<DEVICE CONTROL FOUR>)
        ␕ U+0015 (<NEGATIVE ACKNOWLEDGE>)
        ␖ U+0016 (<SYNCHRONOUS IDLE>)
        ␗ U+0017 (<END OF TRANSMISSION BLOCK>)
        ␘ U+0018 (<CANCEL>)
        ␙ U+0019 (<END OF MEDIUM>)
        ␚ U+001A (<SUBSTITUTE>)
        ␛ U+001B (<ESCAPE>)
        ␜ U+001C (<INFORMATION SEPARATOR FOUR>)
        ␝ U+001D (<INFORMATION SEPARATOR THREE>)
        ␞ U+001E (<INFORMATION SEPARATOR TWO>)
        ␟ U+001F (<INFORMATION SEPARATOR ONE>)
        ⑿ U+007F (<DELETE>)

    You can set the `insensitive` parameter to do case insensitive
    matching::

        >>> prop = 'emod'
        >>> value = 'y'
        >>> insensitive = True
        >>> gen = filter_by_property(prop, value, insensitive=insensitive)
        >>> for char in gen:
        ...     print(char.summarize())
        ...
        🏻 U+1F3FB (EMOJI MODIFIER FITZPATRICK TYPE-1-2)
        🏼 U+1F3FC (EMOJI MODIFIER FITZPATRICK TYPE-3)
        🏽 U+1F3FD (EMOJI MODIFIER FITZPATRICK TYPE-4)
        🏾 U+1F3FE (EMOJI MODIFIER FITZPATRICK TYPE-5)
        🏿 U+1F3FF (EMOJI MODIFIER FITZPATRICK TYPE-6)

    If you set the `regex` parameter, you can search using regular
    expressions::

        >>> prop = 'na'
        >>> value = '.*EYE$'
        >>> regex = True
        >>> gen = filter_by_property(prop, value, regex=regex)
        >>> for char in gen:
        ...     print(char.summarize())
        ...
        ◉ U+25C9 (FISHEYE)
        ◎ U+25CE (BULLSEYE)
        ⺫ U+2EAB (CJK RADICAL EYE)
        ⽬ U+2F6C (KANGXI RADICAL EYE)
        👁 U+1F441 (EYE)
        😜 U+1F61C (FACE WITH STUCK-OUT TONGUE AND WINKING EYE)
        🤪 U+1F92A (GRINNING FACE WITH ONE LARGE AND ONE SMALL EYE)
        🫣 U+1FAE3 (FACE WITH PEEKING EYE)

    .. _warning:
        If you don't limit the characters you are doing the filter on,
        this will be a single-threaded regular expression comparison
        on 1,114,111 characters. In other words, it's not the speediest
        thing in the world.
    """
    if not chars:
        chars = [Character(n) for n in range(util.LEN_UNICODE)]

    if regex:
        flags = 0
        if insensitive:
            flags = re.IGNORECASE
        pattern = re.compile(value, flags=flags)
        for char in chars:
            if pattern.match(getattr(char, prop)):
                yield char

    elif insensitive:
        value = value.casefold()
        for char in chars:
            if getattr(char, prop).casefold() == value:
                yield char

    else:
        for char in chars:
            if getattr(char, prop) == value:
                yield char


def get_category_members(category: str) -> tuple[Character, ...]:
    """Get all characters that are members of the given category."""
    ulen = 0x10FFFF
    members = (
        Character(n) for n in range(ulen)
        if ucd.category(chr(n)) == category
    )
    return tuple(members)


def get_properties() -> tuple[str, ...]:
    """Get the valid Unicode properties.

    :return: The properties as a :class:`tuple`.
    :rtype: tuple

    Usage
    -----
    To get the list of Unicode properties::

        >>> get_properties()                    # doctest: +ELLIPSIS
        ('age', 'ahex',... 'xo_nfkd')

    """
    props = Character.cache.props
    result = []
    for key in props:
        if props[key] not in result:
            result.append(props[key])
    aliases = tuple(prop.alias for prop in result)
    saliases = sorted(alias.casefold() for alias in aliases)
    return tuple(saliases)


def get_property_values(prop: str) -> tuple[str, ...]:
    """Get the valid property value aliases for a property.

    :param prop: The short name of the property.
    :return: The valid values for the property as a :class:`tuple`.
    :rtype: tuple

    Usage
    -----
    To get the valid property values::

        >>> prop = 'gc'
        >>> get_property_values(prop)           # doctest: +ELLIPSIS
        ('C', 'Cc', 'Cf', 'Cn', 'Co', 'Cs', 'L',... 'Zs')

    """
    propvals = Character.cache.propvals[prop]
    result = []
    for key in propvals:
        if propvals[key] not in result:
            result.append(propvals[key])
    return tuple(val.alias for val in result)


if __name__ == '__main__':
    for item in filter_by_property('na', '.*FROWN.*', regex=True):
        text = item.summarize()
        btext = text.encode('utf_8', errors='replace')
        print(btext.decode('utf_8'))

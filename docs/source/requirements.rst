###################
charex Requirements
###################

The purpose of this document is to detail the requirements for the
:mod:`charex` package. This is an initial take to help with planning.
There may be additional requirements or non-required features added in
the future. Changes may be made in the code that are not reflected here.


Purpose
=======
The purposes of :mod:`charex` are:

*   Be a tool to explore character information,
*   Be a tool for demonstrating how character encoded data works,
*   Provide a reverse lookup for character decomposition for use in
    security testing.


Functional Requirement
======================
The following are the functional requirements for :mod:`charex`. It can:

*   Display the code point for a given series of bits,
*   Display the bits for a given code point,
*   Show the bits for all normalization forms of a given code point,
*   Show all code points that normalize to a given code point,
*   Show escaped versions of a given code point,
*   Show full details for a given code point,
*   Guess the code point for a given text,
*   Show the denormalized forms of a given string,
*   Put practical limits on the number of denormalized forms given,
*   Display the released versions of the Unicode specification.


Technical Requirements
======================
The following are the technical requirements for :mod:`charset`. It:

*   Supports a list of common character sets,
*   Supports big and little endian byte order,
*   Has a command line interface.


Design Discussion
=================
The purpose of this section is to think through design challenges
encountered in the course of developing `charex`. As this is a living
process, information here is not guaranteed to describe the current
state of the package.


Denormalize
-----------
The problem is: denormalizing long strings with lots of denormalization
options can become a very deep recursion. It may hit the recursion limit.
But, maybe I don't start with worrying about it. I can add a maximum
depth to it later to help control that a little.


List of Codecs
--------------
Python doesn't have an easy way to get all the codecs. There are ways
to do it, but they run into problems. May be best to hardcode this
list in.


Database and Caching
--------------------
The problems I'm trying to solve:

*   Reloading data from file for each property look up is slow.
*   Data is stored in different formats in different files.
*   The values stored in the files sometimes needs processing to
    get the actual value.
*   That processing sometimes requires data from other files.
*   Eventually, I'd like to be able to switch between versions.

To this point, I've been trying to hide the file from :mod:`charex`
as much as possible. Maybe that's the wrong direction. Maybe the
data should be stored by file. That way, I don't have to come up
with an elaborate scheme for how to store the data. I just need to
map the properties to the relavant file information.

OK, so, a query for the 'jsn' property of the character U+1100
has to contain the following information:

*   The zip archive,
*   The file,
*   The property (because some files contain multiple properties),
*   The code point.

However, the property determines the archive and file, so the user
should never need to know those parts of the query. I think the design
here needs four layers:

*   File reader: reads the raw data from file,
*   File processor: adjusts the raw data as needed to get real values,
*   File cache: stores the real values in memory after loading,
*   Property map: gets value for the property for the code point.

How do I handle the difference in the return types between Jamo.txt
and UnicodeData.txt? I guess that's up to the property map. It will
just need to know how to return the data from the relevant file for
each property. That means, I'm going to need two hard coded data
structures:

*   property -> file
*   file -> archive

Not everything that is needed from the files is a property. The list
of property value aliases, for example, is necessary for translating
between the aliases and long names for the property values, but they
aren't a property themselves. They are searchable by property alias
and property value long name. So, the property map is more of a data
map rather than a specific property map.


FileCache and Typing
~~~~~~~~~~~~~~~~~~~~
Things I don't want to do:

*   Load all data files when starting the script,
*   Load all single_value type files the first time a single_value
    property is needed.
*   Have to type check the data after it leaves the FileCache.
*   Define properties for each file.

That said, using :attr:`FileCache.__getattr__` seems like the best
approach. The only problem is that the current keys of the `path_map`
contain characters that won't work in identifiers (forward slash and
period). I'll need to have an algorithm to change those. It's not
idea, but I think it's probably the best approach.

The algorithm will:

*   Case fold,
*   Drop everything before the last forward slash,
*   Drop everything after the first period.

I can probably just regenerate `path_map.json` with that, rather than
having to do it at run time.

It doesn't seem to like to use :func:`getattr` from within
:attr:`__getattr__`, which means :attr:`__getattr__` is going to
get big. That's unfortunate, but it might be less unfortunate than
what I'm currently doing in :mod:`charex.charex`.


Rethinking the Cache
--------------------
The :class:`charex.db.FileCache` and all of :mod:`charex.db` feels very
complex. The goal was to use the data straight from the Unicode files
as the database, but this requires those files to be loaded and parsed
while :mod:`charex` is running. That means all the parsing logic needs
to be in :mod:`charex.db`. Maybe this decision was wrong-headed. Maybe
I should parse all that data into an easier to call database, allowing
all the Unicode parsing code to be pulled out into :mod:`util`.

This will be a huge change. I'm not sure it's worth doing in 0.2.3. That
might be a 1.0.0 feature.

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
*   Guess the code point for a given text.
*   Show the denormalized forms of a given string.
*   Put practical limits on the number of denormalized forms given.


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
Telemetry Storage Layout
========================

The basic idea is to partition the data by a number of useful dimensions, then
use the dimensions to form a directory hierarchy. Finally, the actual
submissions will be stored in compressed files that may be read and processed
in parallel. The files in a directory will be split into manageable sized
pieces. Each line in the file will be of the form <uuid><tab><json>.  See
[StorageFormat](StorageFormat.md) for more details about the contents of the 
files.

The main thing to define here is exactly which dimensions will be used for
partitioning, and in which order to apply them.

If we used submission day, channel, and operating system, we would end up with
a structure like this:
```bash
20130612/
  nightly/
    winnt/
      001.lz4
      002.lz4
    darwin/
      001.lz4
    linux/
      001.lz4
  aurora/
    winnt/
      001.lz4
      002.lz4
      ...
      005.lz4
    darwin/
      001.lz4
    linux/
      001.lz4
  beta/
    winnt/
      001.lz4
      002.lz4
      ...
      005.lz4
    darwin/
      001.lz4
    linux/
      001.lz4
  release/
    winnt/
      001.lz4
      002.lz4
      ...
      061.lz4
    darwin/
      001.lz4
      002.lz4
    linux/
      001.lz4
  other/
    winnt/
      001.lz4
    darwin/
      001.lz4
20130611/
  nightly/
...
```

In order for each individual file not to get too small (and thus make
compression less effective), we will want to bucket certain rarely-occuring
dimensions into an "other" directory.  This way we do not need to maintain a
mostly-empty directory tree for customized channels, for example.

One way to accomplish this is to maintain a predefined schema of which values
are acceptable in a dimension, with anything outside the whitelist being
grouped into "other".

Another way is not to use a schema, but to "roll up" small partitions based on
the number/size of documents.

Schema-based Storage
--------------------

### Option 1: Filesystem as Schema
One possibility is to use the filesystem itself as the schema, whereby if an
expected directory does not exist, a document is automatically put in the 
"other" category for that level.

This has the advantage that you can update the schema in real time, simply by
creating new directories in the filesystem.

One disadvantage is that you would have to reprocess everything in the "other"
category to redistribute documents into newly created directories.  It would
also require the ongoing creation of submission day directories (though those
could be created say 5 days ahead).

Another disadvantage is that the schema is not defined explicitly, so it could
become inconsistent across servers or days.

### Option 2: Schema document
Another possibility is to keep the schema documented separately, and have the 
partitioning code consult the schema and create any directories on demand.

This has the advantage that the schema is defined explicitly, and is easily
shared in a multi-server scenario.

One disadvantage is that you would have to signal the partitioner of any change
to the schema so that documents could be re-routed with the updated schema.


Size-based partitions
---------------------

One could have a batch process to go through the data for the previous day,
and combine any files that contained less than a certain amount of data.

This has the advantage that it does not require manual intervention to maintain
reasonably well-balanced splitting of data files.

A disadvantage is that during the current day, the "long tail" of infrequently
appearing dimension values could result in a huge number of files and
directories being created.
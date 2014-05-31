logstash-elasticsearch-scripts
==============================

Management scripts for Logstash over ES

 * logstash_index_optimize.py : Optimizing logstash indexes newer than n days.
 * logstash_index_cleaner.py : Delete logstash indexes older than n days.


logstash_index_optimize.py
--------------------------

Optimise all the indexes newer that argv. Ex:

```
$ ./logstash_index_optimize.py -d 5
Optimizing daily indices newer than 5 days.

Optimizing index logstash-2012.10.27 because it is 2 days, 12:46:23.759359 newer than cutoff.
Successfully optimized index: logstash-2012.10.29
Optimizing index logstash-2012.10.28 because it is 3 days, 12:46:23.759359 newer than cutoff.
Successfully optimized index: logstash-2012.10.29
Optimizing index logstash-2012.10.29 because it is 4 days, 12:46:23.759359 newer than cutoff.
Successfully optimized index: logstash-2012.10.29

Done in 0:00:18.505136.
```

```
$ ./logstash_index_optimize.py -h
usage: logstash_index_optimize.py [-h] [-v] [--host HOST] [--port PORT]
                                  [-t TIMEOUT] [-p PREFIX] [-s SEPARATOR]
                                  [-H HOURS_TO_OPTIMIZE] [-d DAYS_TO_OPTIMIZE]
                                  [-n]

Optimize logstash indices from Elasticsearch.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --host HOST           Elasticsearch host.
  --port PORT           Elasticsearch port
  -t TIMEOUT, --timeout TIMEOUT
                        Elasticsearch timeout
  -p PREFIX, --prefix PREFIX
                        Prefix for the indices. Indices that do not have this
                        prefix are skipped.
  -s SEPARATOR, --separator SEPARATOR
                        Time unit separator
  -H HOURS_TO_OPTIMIZE, --hours-to-optimize HOURS_TO_OPTIMIZE
                        Number of hours to optimize.
  -d DAYS_TO_OPTIMIZE, --days-to-optimize DAYS_TO_OPTIMIZE
                        Number of days to optimize.
  -n, --dry-run         If true, does not perform any changes to the
                        Elasticsearch indices.
```

logstash_index_cleaner.py
--------------------------

Delete the indexes older than argv. Ex:

```
$ ./logstash_index_cleaner.py -d 365
Deleting daily indices older than 365 days.

logstash-2012.10.27 is 362 days, 12:42:45.724690 above the cutoff.
logstash-2012.10.28 is 363 days, 12:42:45.724690 above the cutoff.
logstash-2012.10.29 is 364 days, 12:42:45.724690 above the cutoff.

Done in 0:00:00.038624.
```

```
$ ./logstash_index_cleaner.py -h
usage: logstash_index_cleaner.py [-h] [-v] [--host HOST] [--port PORT]
                                 [-t TIMEOUT] [-p PREFIX] [-s SEPARATOR]
                                 [-H HOURS_TO_KEEP] [-d DAYS_TO_KEEP] [-n]

Delete old logstash indices from Elasticsearch.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --host HOST           Elasticsearch host.
  --port PORT           Elasticsearch port
  -t TIMEOUT, --timeout TIMEOUT
                        Elasticsearch timeout
  -p PREFIX, --prefix PREFIX
                        Prefix for the indices. Indices that do not have this
                        prefix are skipped.
  -s SEPARATOR, --separator SEPARATOR
                        Time unit separator
  -H HOURS_TO_KEEP, --hours-to-keep HOURS_TO_KEEP
                        Number of hours to keep.
  -d DAYS_TO_KEEP, --days-to-keep DAYS_TO_KEEP
                        Number of days to keep.
  -n, --dry-run         If true, does not perform any changes to the
                        Elasticsearch indices.
```

Alternatives
--------------------------

- [elasticsearch curator](https://github.com/elasticsearch/curator)

#!/usr/bin/env python
#
# Optimize all indices with a datestamp newer than "days-to-optimize" for daily
# if you have hourly indices, it will optimize all of those newer than "hours-to-optimize"
#
# This script presumes an index is named typically, e.g. logstash-YYYY.MM.DD
# It will work with any name-YYYY.MM.DD or name-YYYY.MM.DD.HH type sequence
#
# Requires python and the following dependencies (all pip/easy_installable):
#
# pyes (python elasticsearch bindings, which might need simplejson)
# argparse (built-in in python2.7 and higher, python 2.6 and lower will have to easy_install it)
#
# TODO: Proper logging instead of just print statements, being able to configure a decent logging level.
#       Unit tests. The code is somewhat broken up into logical parts that may be tested separately.
#       Better error reporting?
#       Improve the get_index_epoch method to parse more date formats. Consider renaming (to "parse_date_to_timestamp"?)

import sys
import time
import argparse
from datetime import timedelta

import pyes


__version__ = '0.1.1'


def make_parser():
    """ Creates an ArgumentParser to parse the command line options. """
    parser = argparse.ArgumentParser(description='Optimize logstash indices from Elasticsearch.')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s '+__version__)

    parser.add_argument('--host', help='Elasticsearch host.', default='localhost')
    parser.add_argument('--port', help='Elasticsearch port', default=9200, type=int)
    parser.add_argument('-t', '--timeout', help='Elasticsearch timeout', default=30, type=int)

    parser.add_argument('-p', '--prefix', help='Prefix for the indices. Indices that do not have this prefix are skipped.', default='logstash-')
    parser.add_argument('-s', '--separator', help='Time unit separator', default='.')

    parser.add_argument('-H', '--hours-to-optimize', action='store', help='Number of hours to optimize.', type=int)
    parser.add_argument('-d', '--days-to-optimize', action='store', help='Number of days to optimize.', type=int)

    parser.add_argument('-n', '--dry-run', action='store_true', help='If true, does not perform any changes to the Elasticsearch indices.', default=False)

    return parser


def get_index_epoch(index_timestamp, separator='.'):
    """ Gets the epoch of the index.

    :param index_timestamp: A string on the format YYYY.MM.DD[.HH]
    :return The creation time (epoch) of the index.
    """
    year_month_day_optionalhour = index_timestamp.split(separator)
    if len(year_month_day_optionalhour) == 3:
        year_month_day_optionalhour.append('3')

    return time.mktime([int(part) for part in year_month_day_optionalhour] + [0,0,0,0,0])


def find_indices_to_optimize(connection, days_to_optimize=None, hours_to_optimize=None, separator='.', prefix='logstash-', out=sys.stdout, err=sys.stderr):
    """ Generator that yields indices to optimize.

    :return: Yields tuples on the format ``(index_name, to_optimize)`` where index_name
        is the name of the index to optimize and to_optimize is the number of seconds (a float value) that the
        index is to optimize.
    """
    utc_now_time = time.time() + time.altzone
    days_cutoff = utc_now_time - days_to_optimize * 24 * 60 * 60 if days_to_optimize is not None else None
    hours_cutoff = utc_now_time - hours_to_optimize * 60 * 60 if hours_to_optimize is not None else None

    for index_name in sorted(set(connection.get_indices().keys())):
        if not index_name.startswith(prefix):
            print >> out, 'Skipping index due to missing prefix {0}: {1}'.format(prefix, index_name)
            continue

        unprefixed_index_name = index_name[len(prefix):]

        # find the timestamp parts (i.e ['2011', '01', '05'] from '2011.01.05') using the configured separator
        parts = unprefixed_index_name.split(separator)

        # perform some basic validation
        if len(parts) < 3 or len(parts) > 4 or not all([item.isdigit() for item in parts]):
            print >> err, 'Could not find a valid timestamp from the index: {0}'.format(index_name)
            continue

        # find the cutoff. if we have more than 3 parts in the timestamp, the timestamp includes the hours and we
        # should compare it to the hours_cutoff, otherwise, we should use the days_cutoff
        cutoff = hours_cutoff
        if len(parts) == 3:
            cutoff = days_cutoff

        # but the cutoff might be none, if the current index only has three parts (year.month.day) and we're only
        # optimizing hourly indices:
        if cutoff is None:
            print >> out, 'Skipping {0} because it is of a type (hourly or daily) that I\'m not asked to optimize.'.format(index_name)
            continue

        index_epoch = get_index_epoch(unprefixed_index_name)

        # if the index is older than the cutoff
        if index_epoch > cutoff:
            yield index_name, cutoff-index_epoch

        else:
            print >> out, '{0} is {1} above the cutoff.'.format(index_name, timedelta(seconds=index_epoch-cutoff))


def main():
    start = time.time()

    parser = make_parser()
    arguments = parser.parse_args()

    if not arguments.hours_to_optimize and not arguments.days_to_optimize:
        print >> sys.stderr, 'Invalid arguments: You must specify either the number of hours or the number of days to optimize.'
        parser.print_help()
        return

    connection = pyes.ES('{0}:{1}'.format(arguments.host, arguments.port), timeout=arguments.timeout)

    if arguments.days_to_optimize:
        print 'Optimizing daily indices newer than {0} days.'.format(arguments.days_to_optimize)
    if arguments.hours_to_optimize:
        print 'Optimizing hourly indices newer than {0} hours.'.format(arguments.hours_to_optimize)

    print ''

    for index_name, to_optimize in find_indices_to_optimize(connection, arguments.days_to_optimize, arguments.hours_to_optimize, arguments.separator, arguments.prefix):
        expiration = timedelta(seconds=to_optimize)

        if arguments.dry_run:
            print 'Would have attempted optimizing index {0} because it is {1} newer than the calculated cutoff.'.format(index_name, abs(expiration))
            continue

        print 'Optimizing index {0} because it is {1} newer than cutoff.'.format(index_name, abs(expiration))

        optimization = connection.optimize(index_name)
        # ES returns a dict on the format {u'acknowledged': True, u'ok': True} on success.
        if optimization.get('ok'):
            print 'Successfully optimized index: {0}'.format(index_name)
        else:
            print 'Error optimizing index: {0}. ({1})'.format(index_name, optimization)

    print ''
    print 'Done in {0}.'.format(timedelta(seconds=time.time()-start))


if __name__ == '__main__':
    main()

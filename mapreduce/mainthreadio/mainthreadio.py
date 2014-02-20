import simplejson as json
import numpy
import io
import csv
import scipy.stats

from string import maketrans

def clean(s):
    return normalize(s).translate(None, ",")

def normalize(s):
    if type(s) == unicode:
        return s.encode('utf8', 'ignore')
    else:
        return str(s)

def safe_key(pieces):
    output = io.BytesIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(pieces)
    return output.getvalue().strip()

def map(k, d, v, cx):
    global n_pings

    parsed = json.loads(v)
    reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date = d

    if not "fileIOReports" in parsed:
        return

    if not parsed["fileIOReports"]:
        return

    disk = parsed['info'].get('profileHDDModel', "NA")
    arch = parsed['info']['arch']
    OS_version = parsed['info']['version']
    addons = parsed['info'].get('addons', "")
    addons = addons.replace(',',';')

    for f, arr in parsed["fileIOReports"].iteritems():
        arr.append(arch)
        arr.append(OS_version)
        arr.append(disk)
        arr.append(addons)
        arr.append(addons.count(';'))
        #cx.write(safe_key(["TOTAL"]), arr)
        cx.write(safe_key([clean(f)]), arr)

def setup_reduce(cx):
    cx.field_separator = ","

def reduce(k, v, cx):
    totals = []
    avgs = []
    counts = []
    n_opens = []
    n_reads = []
    n_writes = []
    n_fsyncs = []
    n_stats = []
    n_pings = len(v)

    if n_pings > 10000:
        for total, n_open, n_read, n_write, n_fsync, n_stat, arch, OS_version, disk, addons, addons_count in v[:n_pings/2]:
            cx.write(k, ",".join([str(total), str(n_open), str(n_read), str(n_write), str(n_fsync), str(n_stat), arch, OS_version, disk, addons, str(addons_count)]))
            #totals.append(total)
            #n_opens.append(n_open)
            #n_reads.append(n_read)
            #n_writes.append(n_write)
            #n_fsyncs.append(n_fsync)
            #n_stats.append(n_stat)

            #count = n_open + n_read + n_write + n_fsync + n_stat
            #counts.append(count)

        # Output fields:
        # submission_date, app_name, app_version
        # app_update_channel, filename, submission_count, median_time, median_count
        #cx.write(k, ",".join([str(n_pings),
                             #str(scipy.stats.scoreatpercentile(totals, 90)),
                             #str(scipy.stats.scoreatpercentile(count, 90)),
                             #str(scipy.stats.scoreatpercentile(n_opens, 90)),
                             #str(scipy.stats.scoreatpercentile(n_reads, 90)),
                             #str(scipy.stats.scoreatpercentile(n_writes, 90)),
                             #str(scipy.stats.scoreatpercentile(n_fsyncs, 90)),
                             #str(scipy.stats.scoreatpercentile(n_stats, 90)) ]))

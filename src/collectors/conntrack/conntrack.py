# coding=utf-8

"""
Shells out to get the value of sysctl net.netfilter.nf_conntrack_count and
net.netfilter.nf_conntrack_count_max

#### Dependencies

 * nf_conntrack module

"""

import diamond.collector
import os


class ConnTrackCollector(diamond.collector.Collector):
    """
    Collector of number of conntrack connections
    """

    def get_default_config_help(self):
        """
        Return help text for collector configuration
        """
        config_help = super(ConnTrackCollector, self).get_default_config_help()
        config_help.update({
            "dir":      "Directories with files of interest, comma seperated",
            "files":    "List of files to collect statistics from",
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(ConnTrackCollector, self).get_default_config()
        config.update({
            "path":  "conntrack",
            "dir":   "/proc/sys/net/ipv4/netfilter,/proc/sys/net/netfilter",
            "files": "ip_conntrack_count,ip_conntrack_max,"
            "nf_conntrack_count,nf_conntrack_max",
        })
        return config

    def collect(self):
        """
        Collect metrics
        """
        collected = {}
        files = []

        if isinstance(self.config['dir'], basestring):
            dirs = [d.strip() for d in self.config['dir'].split(',')]
        elif isinstance(self.config['dir'], list):
            dirs = self.config['dir']

        if isinstance(self.config['files'], basestring):
            files = [f.strip() for f in self.config['files'].split(',')]
        elif isinstance(self.config['files'], list):
            files = self.config['files']

        for sdir in dirs:
            for sfile in files:
                fpath = "%s/%s" % (sdir, sfile)
                if sfile[-15:] == 'conntrack_count':
                    metric_name = 'ip_conntrack_count'
                elif sfile[-13:] == 'conntrack_max':
                    metric_name = 'ip_conntrack_max'
                else:
                    self.log.error('Unknown file for collection: %s', sfile)
                    continue
                if not os.path.exists(fpath):
                    continue
                try:
                    with open(fpath, "r") as fhandle:
                        metric = float(fhandle.readline().rstrip("\n"))
                        collected[metric_name] = metric
                except Exception as exception:
                    self.log.error("Failed to collect from '%s': %s",
                                   fpath,
                                   exception)

        for key in collected.keys():
            self.publish(key, collected[key])

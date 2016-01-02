import subprocess, re, os, sys, subprocess
from os import listdir, access, X_OK, makedirs
from os.path import join, exists, basename
from module.plugins.internal.Addon import Addon
from module.utils import save_join


class FileBot(Addon):
    __name__ = "FileBot"
    __version__ = "1.8"
    __type__    = "hook"
    __status__  = "testing"
    __config__ = [("activated", "bool", "Activated", "False"),

                  ("destination", "folder", "destination folder", ""),

                  ("conflict", """skip;override""", "conflict handling", "override"),

                  ("action", """move;copy;test""", "copy, move or test(dry run)", "move"),
                  
                  ("unsorted", """y;n""", "sort out files that cannot be proceed to $destination/unsorted/", "n"),

                  ("lang", "str", "language (en, de, fr, es, etc)", "de"),

                  ("subtitles", "str", "subtitles language (en, de, fr, es, etc)", "de"),

                  ("ignore", "str", "ignore files (regex)", ""),

                  ("artwork", """y;n""", "download artwork", "y"),

                  ("clean", """y;n""", "clean folder from clutter thats left behind", "y"),
                  
                  ("storeReport", """y;n""", "save reports to local filesystem", "n"),

                  ("movie", "str", "movie destination (relative to destination or absolute)", ""),

                  ("series", "str", "series destination (relative to destination or absolute)", ""),

                  ("excludeList", "str", "exclude list file", "pyload-amc.txt"),

                  ("reperror", """y;n""", "Report Error via Email", "n"),

                  ("filebot", "str", "filebot executable", "filebot"),

                  ("exec", "str", "additional exec script", ""),

                  ("no-xattr", "bool", "no-xattr", "False"),

                  ("xbmc", "str", "xbmc hostname", ""),

                  ("plex", "str", "plex hostname", ""),

                  ("plextoken", "str", "plex token (only needed with external plex servers)", ""),

                  ("extras", """y;n""", "create .url with all available backdrops", "n"),
                  
                  ("pushover", "str", "pushover user-key", ""),

                  ("pushbullet", "str", "pushbullet api-key", ""),

                  ("cleanfolder", "bool", "remove DownloadFolder after moving", "False"),
                  
                  ("output_to_log", "bool", "write FileBot Output to pyLoad Logfile", "True"),
                  
                  ("delete_extracted", "bool", "Delete archives after succesful extraction", "True")]

    __description__ = "Automated renaming and sorting for tv episodes movies, music and animes"
    __author_name__ = ("Branko Wilhelm", "Kotaro", "Gutz-Pilz")
    __author_mail__ = ("branko.wilhelm@gmail.com", "screver@gmail.com", "unwichtig@gmail.com")

    def init(self):
        self.event_map  = {'package_extracted': "package_extracted",
                           'package_finished': "package_finished" }

    def coreReady(self):
        self.pyload.config.set("general", "folder_per_package", "True")
        ##self.pyload.config.setPlugin("FileBot", "exec", 'cd / && ./filebot.sh "{file}"')
        if self.config.get('delete_extracted') is True:
            self.pyload.config.setPlugin("ExtractArchive", "delete", "True")
            self.pyload.config.setPlugin("ExtractArchive", "deltotrash", "False")
        else:
            self.pyload.config.setPlugin("ExtractArchive", "delete", "False")

    def package_finished(self, pypack):
        download_folder = self.pyload.config['general']['download_folder']
        folder = save_join(download_folder, pypack.folder)
        if self.config.get('delete_extracted') is True:
            x = False
            self.log_debug("MKV-Checkup (packageFinished)")
            for root, dirs, files in os.walk(folder):
                for name in files:
                    if name.endswith((".rar", ".r0", ".r12")):
                        self.log_debug("Hier sind noch Archive")
                        x = True
                    break
                break
            if x == False:
                self.log_debug("Hier sind keine Archive")
                self.Finished(folder)
        else:
            self.Finished(folder)
            
    def package_extracted(self, pypack):
        x = False

        download_folder = self.pyload.config['general']['download_folder']
        extract_destination = self.pyload.config.getPlugin("ExtractArchive", "destination")
        extract_subfolder = self.pyload.config.getPlugin("ExtractArchive", "subfolder")
        
        # determine output folder
        folder = save_join(download_folder, pypack.folder, extract_destination, "")  #: force trailing slash

        if extract_subfolder is True:
            folder = save_join(folder, pypack.folder)
        
        if self.config.get('delete_extracted') is True:
            self.log_debug("MKV-Checkup (package_extracted)")
            for root, dirs, files in os.walk(folder):
                for name in files:
                    if name.endswith((".rar", ".r0", ".r12")):
                        self.log_debug("Hier sind noch Archive")
                        x = True
                    break
                break
            if x == False:
                self.log_debug("Hier sind keine Archive")
                self.Finished(folder)
        else:
            self.Finished(folder)


    def Finished(self, folder):
        args = []

        if self.config.get('filebot'):
            args.append(self.config.get('filebot'))
        else:
            args.append('filebot')

        args.append('-script')
        args.append('fn:amc')

        args.append('-non-strict')

        args.append('--log-file')
        args.append('amc.log')

        args.append('-r')

        args.append('--conflict')
        args.append(self.config.get('conflict'))

        args.append('--action')
        args.append(self.config.get('action'))

        if self.config.get('destination'):
            args.append('--output')
            args.append(self.config.get('destination'))
        else:
            args.append('--output')
            args.append(folder)

        if self.config.get('lang'):
            args.append('--lang')
            args.append(self.config.get('lang'))

        # start with all definitions:
        args.append('--def')

        if self.config.get('exec'):
            args.append('exec=' + self.config.get('exec'))

        if self.config.get('clean'):
            args.append('clean=' + self.config.get('clean'))

        args.append('skipExtract=y')

        if self.config.get('excludeList'):
            args.append('excludeList=' + self.config.get('excludeList'))

        if self.config.get('reperror'):
            args.append('reportError=' + self.config.get('reperror'))

        if self.config.get('unsorted'):
            args.append('unsorted=' + self.config.get('unsorted'))
            
        if self.config.get('storeReport'):
            args.append('storeReport=' + self.config.get('storeReport'))

        if self.config.get('artwork'):
            args.append('artwork=' + self.config.get('artwork'))

        if self.config.get('subtitles'):
            args.append('subtitles=' + self.config.get('subtitles'))

        if self.config.get('ignore'):
            args.append('ignore=' + self.config.get('ignore'))

        if self.config.get('movie'):
            args.append('movieFormat=' + self.config.get('movie'))

        if self.config.get('series'):
            args.append('seriesFormat=' + self.config.get('series'))

        if self.config.get('no-xattr') is True:
            args.append(" -no-xattr")

        if self.config.get('xbmc'):
            args.append('xbmc=' + self.config.get('xbmc'))
            
        if self.config.get('pushover'):
            args.append('pushover=' + self.config.get('pushover'))

        if self.config.get('pushbullet'):
            args.append('pushbullet=' + self.config.get('pushbullet'))

        if self.config.get('plex'):
            if self.config.get('plextoken'):
                plexToken = ":" + self.config.get('plextoken')
            else:
                plexToken = ""

            args.append('plex=' + self.config.get('plex') + plexToken)
            self.log_info('plex refreshed at ' + self.config.get('plex') + plexToken)


        if self.config.get('extras'):
            args.append('extras='+ self.config.get('extras'))

        args.append(folder)

        try:
            if self.config.get('output_to_log') is True:
                self.log_info('executed')
                proc=subprocess.Popen(args, stdout=subprocess.PIPE)
                for line in proc.stdout:
                    self.log_info(line.decode('utf-8').rstrip('\r|\n'))
                proc.wait()
                try:
                    if self.config.get('cleanfolder') is True:
                        self.log_info('cleaning')
                        proc=subprocess.Popen(['filebot -script fn:cleaner --def root=y ', folder], stdout=subprocess.PIPE)
                        for line in proc.stdout:
                            self.log_info(line.decode('utf-8').rstrip('\r|\n'))
                        proc.wait()
                except:
                    self.log_info('kein Ordner zum cleanen vorhanden')
            else:
                self.log_info('executed')
                subprocess.Popen(args, bufsize=-1)
                try:
                    if self.config.get('cleanfolder') is True:
                        self.log_info('cleaning')
                        subprocess.Popen(['filebot -script fn:cleaner --def root=y ', folder], bufsize=-1)
                except:
                    self.log_info('kein Ordner zum cleanen vorhanden')
        except Exception, e:
            self.log_error(str(e))

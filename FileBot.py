import subprocess, re, os, sys, subprocess
from os import listdir, access, X_OK, makedirs
from os.path import join, exists, basename
from module.plugins.internal.Hook import Hook
from module.utils import save_join


class FileBot(Hook):
    __name__ = "FileBot"
    __version__ = "1.1"
    __config__ = [("activated", "bool", "Activated", "False"),

                  ("destination", "folder", "destination folder", ""),

                  ("conflict", """skip;override""", "conflict handling", "override"),

                  ("action", """move;copy;test""", "copy, move or test(dry run)", "move"),

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
        self.pyload.config.setPlugin("FileBot", "exec", 'cd / && ./filebot.sh "{file}"')
        if self.get_config('delete_extracted') is True:
            self.pyload.config.setPlugin("ExtractArchive", "delete", "True")
            self.pyload.config.setPlugin("ExtractArchive", "deltotrash", "False")
        else:
            self.pyload.config.setPlugin("ExtractArchive", "delete", "False", section='plugin')

    def package_finished(self, pypack):
        download_folder = self.pyload.config['general']['download_folder']
        folder = save_join(download_folder, pypack.folder)
        if self.get_config('delete_extracted') is True:
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
        
        if self.get_config('delete_extracted') is True:
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

        if self.get_config('filebot'):
            args.append(self.get_config('filebot'))
        else:
            args.append('filebot')

        args.append('-script')
        args.append('fn:amc')

        args.append('-non-strict')

        args.append('--log-file')
        args.append('amc.log')

        args.append('-r')

        args.append('--conflict')
        args.append(self.get_config('conflict'))

        args.append('--action')
        args.append(self.get_config('action'))

        if self.get_config('destination'):
            args.append('--output')
            args.append(self.get_config('destination'))
        else:
            args.append('--output')
            args.append(folder)

        if self.get_config('lang'):
            args.append('--lang')
            args.append(self.get_config('lang'))

        # start with all definitions:
        args.append('--def')

        if self.get_config('exec'):
            args.append('exec=' + self.get_config('exec'))

        if self.get_config('clean'):
            args.append('clean=' + self.get_config('clean'))

        args.append('skipExtract=y')

        if self.get_config('excludeList'):
            args.append('excludeList=' + self.get_config('excludeList'))

        if self.get_config('reperror'):
            args.append('reportError=' + self.get_config('reperror'))
        
        if self.get_config('storeReport'):
            args.append('storeReport=' + self.get_config('storeReport'))

        if self.get_config('artwork'):
            args.append('artwork=' + self.get_config('artwork'))

        if self.get_config('subtitles'):
            args.append('subtitles=' + self.get_config('subtitles'))

        if self.get_config('ignore'):
            args.append('ignore=' + self.get_config('ignore'))

        if self.get_config('movie'):
            args.append('movieFormat=' + self.get_config('movie'))

        if self.get_config('series'):
            args.append('seriesFormat=' + self.get_config('series'))

        if self.get_config('no-xattr') is True:
            args.append(" -no-xattr")

        if self.get_config('xbmc'):
            args.append('xbmc=' + self.get_config('xbmc'))
            
        if self.get_config('pushover'):
            args.append('pushover=' + self.get_config('pushover'))

        if self.get_config('pushbullet'):
            args.append('pushbullet=' + self.get_config('pushbullet'))

        if self.get_config('plex'):
            if self.get_config('plextoken'):
                plexToken = ":" + self.get_config('plextoken')
            else:
                plexToken = ""

            args.append('plex=' + self.get_config('plex') + plexToken)
            self.log_info('plex refreshed at ' + self.get_config('plex') + plexToken)


        if self.get_config('extras'):
            args.append('extras='+ self.get_config('extras'))

        args.append(folder)

        try:
            if self.get_config('output_to_log') is True:
                self.log_info('executed')
                proc=subprocess.Popen(args, stdout=subprocess.PIPE)
                for line in proc.stdout:
                    self.log_info(line.decode('utf-8').rstrip('\r|\n'))
                proc.wait()
                try:
                    if self.get_config('cleanfolder') is True:
                        self.log_info('cleaning')
                        proc=subprocess.Popen(['filebot -script fn:cleaner --def root=y ', folder], stdout=subprocess.PIPE)
                        for line in proc.stdout:
                            self.log_info(line.decode('utf-8').rstrip('\r|\n'))
                        proc.wait()
                except:
                    self.logInfo('kein Ordner zum cleanen vorhanden')
            else:
                self.logInfo('executed')
                subprocess.Popen(args, bufsize=-1)
                try:
                    if self.get_config('cleanfolder') is True:
                        self.log_info('cleaning')
                        subprocess.Popen(['filebot -script fn:cleaner --def root=y ', folder], bufsize=-1)
                except:
                    self.log_info('kein Ordner zum cleanen vorhanden')
        except Exception, e:
            self.log_error(str(e))

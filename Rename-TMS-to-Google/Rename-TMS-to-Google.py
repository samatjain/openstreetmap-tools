#!/usr/bin/env python

import os

# Determine valid TMS zoom levels available
zoomLevels = [z for z in xrange(0, 22) if os.path.isdir('%d' % z)]

# Creates two scripts
#  01 Rename old filenames to a temporary file. This is done to prevent
#     overwriting an old and new file that happen to share the same name
#  02 Rename temporary files to their new filenames
old_to_temp_script = file('01-Rename-Old-to-Temp.sh', 'w')
temp_to_new_script = file('02-Rename-Temp-to-New.sh', 'w')

for z in zoomLevels:
    for dirName, subDirs, files in os.walk('%d' % z):
        for file in files:
            y, extension = file.split('.')[0:2]

            if extension != 'png':
                continue

            # bug: need to add a check whether the filename is actually a TMS coordinate
            y = int(y)
            newy = ((2**z) - 1) - y
            old_to_temp_script.write('mv %s/%d.%s %s/%d.%s.tmp\n' % (
                    dirName, y, extension,
                    dirName, newy, extension))
            temp_to_new_script.write('mv %s/%d.%s.tmp %s/%d.%s\n' % (
                    dirName, newy, extension,
                    dirName, newy, extension))

old_to_temp_script.close()
temp_to_new_script.close()

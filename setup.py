from distutils.core import setup

setup(name='Silaty',
      version='1.0',
      description='A neat Prayer Time Reminder App. Simple and complete so no prayer is missed',
      author='Jesse W. Brandao',
      py_modules=['hijra', 'hijracal', 'home','options','prayertime','qiblacompass','sidebar', 'silaty','silatycal'],
      scripts=['silaty-indicator'],
      data_files=[('/usr/share/icons/hicolor/scalable/apps',['icons/hicolor/scalable/silaty-indicator.svg']),
                  ('/usr/share/icons/hicolor/scalable/apps/',['icons/hicolor/128x128/apps/silaty.svg']),
                  ('/usr/share/icons/hicolor/128x128/apps/',['icons/hicolor/128x128/apps/silaty.svg']),
                  ('/usr/share/icons/hicolor/48x48/apps/',['icons/hicolor/48x48/apps/silaty.svg']),
                  ('/usr/share/icons/hicolor/24x24/apps/',['icons/hicolor/24x24/apps/silaty.svg']),
                  ('/usr/share/applications',['silaty.desktop']),
                  ('/etc/xdg/autostart', ['silaty.desktop'])]
      )
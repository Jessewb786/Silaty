#!/bin/bash

if [ "$(id -u)" != "0" ]; then
echo “This script must be run as root” 2>&1
exit 1
fi

sh uninstall.sh

mkdir /usr/share/silaty
cp -R icons /usr/share/silaty/
cp -R audio /usr/share/silaty/
cp -R data /usr/share/silaty/

cp icons/hicolor/128x128/apps/silaty.svg /usr/share/icons/hicolor/scalable/apps/
chmod 644 /usr/share/icons/hicolor/scalable/apps/silaty.svg

cp icons/hicolor/128x128/apps/silaty.svg /usr/share/icons/hicolor/128x128/apps/
chmod 644 /usr/share/icons/hicolor/128x128/apps/silaty.svg

cp icons/hicolor/48x48/apps/silaty.svg /usr/share/icons/hicolor/48x48/apps/
chmod 644 /usr/share/icons/hicolor/48x48/apps/silaty.svg

cp icons/hicolor/24x24/apps/silaty.svg /usr/share/icons/hicolor/24x24/apps/
chmod 644 /usr/share/icons/hicolor/24x24/apps/silaty.svg

cp *.py /usr/share/silaty/
chmod 755 -R /usr/share/silaty/

cp silaty.desktop /etc/xdg/autostart/
chmod 755 /etc/xdg/autostart/silaty.desktop

cp silaty.desktop /usr/share/applications/
chmod 755 /usr/share/applications/silaty.desktop

ln -s /usr/share/silaty/silaty-indicator.py /usr/local/bin/silaty-indicator
chmod 755 /usr/local/bin/silaty-indicator

gtk-update-icon-cache

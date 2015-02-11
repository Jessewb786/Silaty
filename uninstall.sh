#!/bin/bash

if [ "$(id -u)" != "0" ]; then
echo “This script must be run as root” 2>&1
exit 1
fi

rm -rf /usr/share/silaty
rm -f /usr/share/applications/silaty.desktop
rm -f /etc/xdg/autostart/silaty.desktop
rm -f /usr/local/bin/silaty-indicator

rm -f /usr/share/icons/hicolor/128x128/apps/silaty.svg
rm -f /usr/share/icons/hicolor/48x48/apps/silaty.svg
rm -f /usr/share/icons/hicolor/24x24/apps/silaty.svg
rm -f /usr/share/icons/hicolor/scalable/apps/silaty.svg

rm -f /usr/share/icons/hicolor/scalable/apps/silaty-indicator.svg
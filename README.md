Silaty
======

A neat prayer reminder app in GTK

![screenshot](screenshots/Silaty.png)

## Test

Make sure that you have python3 installed using `python3 -V` cmd, then run: 
```bash
cd /path/to/silaty
python3 silaty-indicator.py
```

## Installation

To install open a terminal & run: 
```bash
cd /path/to/silaty
sudo ./install.sh
```

To uninstall run:
```bash
sudo ./uninstall.sh
```

## Changelog

### v1.1-beta

* LICENSE added.
* screenshots added @see [Add screenshots #3](https://github.com/Jessewb786/Silaty/issues/3).
* README updated.
* attempt to clean code.
* GTK warnings fixed.
* wrong time suffix (AM/PM) when using 12h clock format fixed.
* switching between sidebar tabs from indicator menu fixed.
* about tab added/implemented into sidebar.
* fixed a crash when closing the main window.
* [Settings won't open #2](https://github.com/Jessewb786/Silaty/issues/2) fixed.
* load notification icon from its path instead of using an icon name.
* use default layout size, instead of using a fixed window size.
* updates prayer times when changing clock format from settings.
* useless debug messages commented (especially those used in main loop).
* attempt to fix [installing error #4](https://github.com/Jessewb786/Silaty/issues/4) by ignoring pycompile cmd.

### v1.0

* first release

## ToDo

- [ ] add a button to test notification in settings.
- [ ] try to identify & fix settings issues (especially with Location settings, also some settings don't apply before closing the window).
- [ ] reduce code repetition.
- [ ] use a custom list to get/set location (@see Minbar Prayer Times).
- [ ] prayer time calculation don't seems to be correct when using a custom location (longitude/latitude).
- [ ] translate to other languages.

## Credits

- [Jessewb786](https://github.com/Jessewb786)

## License

Silaty is licensed under the [GPL license](LICENSE).

============
N64-Saveswap
============

A simple command-line utility for manipulating the endianness of (A.K.A.
byte-swapping) Nintendo 64 save data so it can be moved between various
cartridge-dumping tools, emulators, flash cartridges, etc.

Features:

* Supports multiple types of byte-swapping
* Codebase is *very* well-commented because I'd originally intended to offer it
  as a learning aid for moving to Python before I got carried away.
* Should run on any platform with a Python 2.7 or 3.x runtime
* Only dependency is the Python standard library
* Unit and functional test suite with 100% branch coverage

Also usable for swapping other formats if the ``--force-padding`` switch is
used to disable size checks. (With the caveat that it will load the entire file
into memory and make copies.)

Very loosely based on saturnu's
`ED64-Saveswap <http://krikzz.com/forum/index.php?topic=1396.0>`_ because I was
feeling wary about virus-scanner false positives and wanted something I didn't
have to run in Wine to use on Linux.

-----
Usage
-----

::

    usage: saveswap.py [-h] [--version] [-v] [-q]
                       [--swap-mode {both,bytes-only,words-only}]
                       [--force-padding NEW_SIZE]
                       [--no-backup]
                       path [path ...]

    A simple utility to translate among the SRAM/EEPROM/Flash dump formats for
    Nintendo 64 cartridges as supported by various dumpers, emulators, and flash
    cartridges.

    positional arguments:
      path                  One or more Nintendo 64 save memory dumps
                            to byte-swap

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -v, --verbose         Increase the verbosity. Use twice for extra effect.
      -q, --quiet           Decrease the verbosity. Use twice for extra effect.
      --swap-mode {both,bytes-only,words-only}
                            Set the type of byte-swapping to be performed.
      --force-padding NEW_SIZE
                            Override autodetected padding size. This also
                            disables the associated safety checks, allowing
                            this tool to be used on other types of files.
                            Specify 0 to disable padding entirely.
      --no-backup           Disable creation of an automatic backup. This is
                            intended to be used by scripts which want
                            more control over whether and where backups
                            are created.

    The swap modes behave as follows:
            both: 12 34 -> 43 21
      bytes-only: 12 34 -> 21 43
      words-only: 12 34 -> 34 12

    The valid padding sizes for N64 save dumps are as follows:
      ===== EEPROM =====
          512 (  4kbit)
         2048 ( 16kbit)
      ====== SRAM ======
        32768 (256kbit)
       131072 (  1Mbit)
      ===== Flash ======
       131072 (  1Mbit)

    For scripting purposes, the exit code will indicate the most
    serious error encountered, with the following meanings:
       0 = Success
      10 = Could not read file / Could not write backup
      20 = File is too large to be an N64 save dump
      30 = File size is not a multiple of the requested swap increment
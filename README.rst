=======================================
srttranslate - Subtitle file translator
=======================================

Automatic translation of .srt subtitle files using the DeepL_ API.

.. _DeepL: <https://www.deepl.com>
.. _DeepL site: <https://www.deepl.com/pro-api?cta=header-pro-api/>
.. _Pypi:  <https://pypi.org>

Installation
------------

Install straight from Pypi_::

    $ pip3 install --user srttranslate

Usage
-----

Once installed, translations can be made using the ``srttranslate`` command::

    $ srttranslate --help
    usage: srttranslate [-h] [--version] [--keyfile KEYFILE] [--output FILE] SUBFILE

    positional arguments:
      SUBFILE               Subtitle file to translate

    options:
      -h, --help            show this help message and exit
      --version, -v         Print version and exit
      --keyfile KEYFILE, -k KEYFILE
                            Name of file containing DeepL's API key
      --output FILE, -o FILE
                            Name of output subtitle file

To translate a subtitle file you must have a DeepL API key, which is
available at the `DeepL site`_.

You can specify a file containing the key (and nothing else) on the command line::

    $ srttranslate --keyfile=mykey.txt --output=Rififi.en.srt Rififi.fr.srt

The API Key can also be provided via the environment variable ``DEEPL_API_KEY``::

    $ DEEPL_API_KEY=5e3x..... srttranslate -o Rififi.en.srt Rififi.fr.srt

License
-------
This software is licensed under the terms of the **MIT license**. See the file ``LICENSE``.

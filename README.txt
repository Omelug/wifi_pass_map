Run:
   make install (to download external libraries)
   make run (You should see link to your instance in console)

Disclamer:
    Project in under development and is not well documented.

Motivation:
    Hi, this is minimalistic tool for display wifi map from multiple different sources. It is strong inspired
    (Ok, maybe better term would be that half of this projet was stolen) from pwnmap project:
    (https://github.com/JAKAMI99/pwnamap/tree/main) project.

Why dont use pwnmap for this?
    pwnmap is great tool for display pwnogotchi data sources during wiredriving, but this tool is for different purpose.
    I want simple way to add new data sources, display it on map and make tools for get more info from/aboput them.

Sources (*.py files in /map_app/sources):
    - every source shoud be singleton child of ./map_app/source_core/Source.py
    - working sources (27.5.2025): wpa-sec.py, handshakes.py
    - if you want know what plugin does, check __description__ in the source file
    - check __requirement__ in the source file, how install it is in ./doc/external_tools.txt
    - every source can define own tools (http://127.0.0.1:1337/tools)

For the future days:
    It would be nice have integraded cracking tools for it, but I am honestly not sure
    how time consuming it can be.


File system:

    /map_app/data/
        /raw/ input point for data sources
        /clean/ output point for tools

    /map_app/sources/config
        - config .ini files for source scripts
        - to make config file, just allow plugin (add it or rename it - delete .d at the end) and refresh map to reload
         plugins, it creates default config files

    p3wifi.py:
        - script to load data from p3wifi database what you need give to mysql database before

    ----------------------------------------------------------------------------------------------------------------
        Table_v0: next script have similar tables for more genric functions,
        test v0  is defined in map_app/source_core/Table_v0.py
    -----------------------------------------------------------------------------------------------------------------
    wpasec.py:
    handshakes.py:

Development:
    - TODO in the /doc/TODO.txt
    - changelog in the /doc/CHANGELOG.txt


Createing New Plugin:
    - copy ./map_app/sources/example.py.d to  ./map_app/sources/new_name_.py  (or more specific example_*.py.d)
    - if you want create param for tool,\
        use "GLOBAL" except of param name (dict key)
    - use __requirements__ to set requirements names (now it si only for description, will be later used for auto install)


Tests:
    - in /tests/
    - to run base  tests, run "make test" or commit (.git/hooks/pre-commit)
    - tests cover only part of code

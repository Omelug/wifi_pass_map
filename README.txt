Disclamer:
    Project in under development and is not well documented.

Motivation:
    Hi, this is minimalistic tool for display wifi map from multiple different sources. It is strong inspired
    (Ok, maybe better term would be that half of this projet was stolen) from pwnmap projekt:
    (https://github.com/JAKAMI99/pwnamap/tree/main) project.

Why dont use pwnmap?
    pwnmap is great tool for display pwnogotchi data sources during wardriving, but this tool is for different purpose.
    I want simple way to add new data sources, display it on map and make tools for get more info from/abput them.

So what is different?
    I deleted some features, because I don't need them:
        - multiple users/user security
        - separated map/exprorer map (I am thinking about different separation, but there is one map for now)
        - api key input form users
        - stats (This is feature I would like to add in future, but differently)

What I changed:
    * refactored some parts of code and deleted redundant code
    * sources are now .py files with dynamic data loading

But I have added some features! :O
    + few info for better debugging
    + new data sources like p3wifi


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

        sources.py:
            - help function for more generic functions

        p3wifi.py:
            - script to load data from p3wifi database what you need give to mysql database before

        ----------------------------------------------------------------------------------------------------------------
            Table_v0: next script have similar tables for more genric functions,
            test v0  is defined in map_app/tools/db.py
        -----------------------------------------------------------------------------------------------------------------

        wpasec.py:
            - script to get potfile from wpasec database

        handshakes.py:
            - requirements: hcxpcapngtool
                git clone https://github.com/ZerBea/hcxtools.git
                cd hcxtools
                make
                sudo make install

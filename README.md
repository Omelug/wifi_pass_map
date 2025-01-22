TLDR:
========
map for diaply wifi data from pwnagotchi and  p3wifi


Motivation:
========
Hi, this is minimalistic tool for display wifi map from multiple different sources. 
It is strong inspired 
(Ok, maybe better term would be that half of this projet was stolen)
by [pwnmap](https://github.com/JAKAMI99/pwnamap/tree/main) project. 





Why dont use pwnmap? pwnmap is great tool for display pwnogotchi data sources during wardriving,
but this tool is for different purpose.
I want easy import for new data sources on laptop.


So what is different?
========
I deleted some features, because I don't need them:<br>

\-  multiple users <br>
\- separated map/exprorer map<br>
\- api key input form users<br>
\- stats (This is feature I would like to add in future, but differently)

What I changed:<br>
\* refactored some parts of code and deleted redundant code
\* sources are now .py files with dynamic data loading ([interface.txt](map_app/sources/interface.txt)) 


But I WILL aslo added some feature~~s~~! xd<br>
\+ added few info for better debugging <br>
\+ TODO: add features  



**For the future days:**

It would be nice have integraded cracking tools for it, but I am honestly not sure 
how time consuming it can be.

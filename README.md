python-allegro-webapi
=====================
Python module designed to help me (and maybe some other people :) in dealing with allegro webapi service.

Usage
---------------------
Usage is simple - class acts as transparent layer between you and SUDS calls. First of all, it initializes new session and restarts it whenever it expires. Secondly, it helps you with some arguments like: sessionId, userLogin, countryCode. How? It fills them with proper values, so you can basically leave them empty, and class will make them working!

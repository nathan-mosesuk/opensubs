opensubs

==============================

Skills:

SQL
Python
HTML
BeautifulSoup
Regular expressions

==============================

Description:

A python script that retrieves the 40 latest subtitles info from opensubtitles.org (subtitle id, 
subtitle language, movie/episode name, year released) and stores that information in a txt file 
and also in a sqlite relational database. It calculates the percentage of every language found.

Note: with a simple while loop, this code has the potential to scrape the entire website
page by page and store all subtitles ever uploaded (at the moment around 10 million) but
to avoid overusing the website server this was not done. Also it could search for the latest
subtitles and store them and stop the search when it finds a subtitle already stored.

==============================

Running the code:

-From windows command prompt, execute the .py file by writing "python filename.py"

==============================

Requirements:

-Python 3.7.1 or superior installed
-BeautifulSoup: Copy the "bs4" folder to the folder where the .py file is.

==============================

Output:

-txt file (.txt) with the list of subtitles and language statistics
-sqlite relational database file (.sqlite) with a Subtitles table, a Language table, and a Year table

==============================

Website source: http://www.opensubtitles.org/en/search/sublanguageid-all

==============================

Files uploaded:

-python script: opensubs.py
-Output files (as example): subtitleslist.txt and subtitleslist.sqlite
-OPENSUBTITLES.ORG Pdf print of the website and screenshots at the moment of code execution
-HTML code screenshots with the searched tags
-Output: screenshots of sqlite database and txt file
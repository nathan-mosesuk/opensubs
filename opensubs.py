import urllib.request,urllib.parse,urllib.error
import sqlite3
import re
from bs4 import BeautifulSoup
# copy bs4 folder to the folder where the .py is

titlelist=[] # a list for storing the movie/series titles
languagelist=[] # a list for storing the movie/series languages
yearlist=[] # a list for storing the movie/series year
idlist=[] # a list for storing the subtitle id

languagedict={} # a dict for counting the languages in language list
languagelistord=[] # a list to store the different languages in order
subtitlelist=[] # a list for storing all info of the subtitle as a tuple
subtitlelistord=[] # a list for ordering subtitlelist

filestr='subtitleslist.txt'
filename=open(filestr,'w')

filesqlstr=filestr.replace('.txt','.sqlite')
filesqlcon=sqlite3.connect(filesqlstr)
filesql=filesqlcon.cursor()

url='http://www.opensubtitles.org/en/search/sublanguageid-all' # all subtitles website

urlh=urllib.request.urlopen(url) #url handle. This way is for analysing data with beautifulsoup. No need for decode()
urlhstr=urlh.read()
htmldata=BeautifulSoup(urlhstr,'html.parser')
anchortagsa=htmldata('a') # searches for all tags 'a' anchor tags inside the tree htmldata

print('Retrieving subtitles from opensubtitles.org...')

# SEARCH FOR TEXT VALUE AND LANGUAGE IN ANCHOR TAG

counttitle=0
countlang=0
for taga in anchortagsa:

   # SEARCH FOR THE MOVIE/SERIES TITLE (INCLUDES YEAR). Title and language are in different anchor tags.

   classname=taga.get('class',None) # if the attribute class is found, it returns a list with the values for class. Search <a class="bnone" for the movie name
   if classname is not None: # first ask if None wasn't returned
      if classname[0]=="bnone": # then classname will be a list
         textvalue=taga.text # extract the text of this anchor tag <a attributes....>TEXT</a>
         counttitle=counttitle+1
         titlesplit=textvalue.split('\n') # splits the title by the new line \n, title 'newline' (year)
         titlelist.append(titlesplit[0]) # the title
         yearlist.append(titlesplit[1][1:5]) # the year, removing the parethesis with slicing

         # SEARCH FOR SUBTITLE UNIQUE ID. The id is also in a tag <td id="main... but it is faster to search it here.

         hrefvalue=taga.get('href',None) # <a class="bnone"...href="/en/subtitles/..."
         if hrefvalue is not None:
            subid=re.findall('subtitles/([0-9]+)',hrefvalue)
            if len(subid)==1: # means it found only one number
               idlist.append(subid[0])
            else:
               idlist.append(None)

         continue # if the anchor tag has class 'bnone' it won't have the language so skip next part

   # SEARCH FOR THE MOVIE/SERIES LANGUAGE. If it found the movie/series title, it won't enter here...

   hrefvalue=taga.get('href',None)
   if hrefvalue is not None: # if href found, .get returns a string
      if hrefvalue.startswith('/en/search/sublanguageid-') is True: # <a title="LanguagenameX" href="/en/search/sublanguageid-....
         if hrefvalue.startswith('/en/search/sublanguageid-all') is False:
            langvalue=taga.get('title',None) # the language is stored under the attribute title
            languagelist.append(langvalue)
            countlang=countlang+1
         else: pass

urlh.close()

print('Subtitles found: ',counttitle)

lentitlelist=len(titlelist) # title, language, and year list should have the same length

# OUTPUT TXT FILE: WRITE SUBTITLES LIST

filename.write('Number - Subtitle_ID - Year - Language - Title\n\n')

i=0
while i<lentitlelist:
   if i<9: numtitle='0'+str(i+1) # starts numbers in 01,02,03 etc. 8 would be 9, the last one.
   else: numtitle=str(i+1)
   wordstempsubtitle=numtitle+' - '+idlist[i]+' - '+yearlist[i]+' - '+languagelist[i]+' - '+titlelist[i]+'\n'
   filename.write(wordstempsubtitle)
   i=i+1

# LANGUAGE COUNT AND DICTIONARY TO OBTAIN PERCETAGE OF EACH LANGUAGE

for lang in languagelist:
   languagedict[lang]=languagedict.get(lang,0)+1 # overwrite the value for the key lang. If it doesn't exist get returns 0.

for lang,count in languagedict.items():
   languagelistord.append((lang,count))
languagelistord=sorted(languagelistord) # orders the list of languages alphabetically

# OUTPUT TXT FILE: WRITE LANGUAGES PERCENTAGE AND HOW MANY FOUND

filename.write('\nLanguages percentage\n\n')

for lang,count in languagelistord:
   langperc=(count/lentitlelist)*100
   wordstemplangperc=lang+': '+str(langperc)+'%\n'
   filename.write(wordstemplangperc)

lenlanguagelistord=len(languagelistord)
wordstemplangperc='\nTotal languages: '+str(lenlanguagelistord)+'\n'
filename.write(wordstemplangperc)

print('Languages found: ',lenlanguagelistord)

# CREATE NEW LIST WITH LANGUAGE, TITLE, YEAR, ID

i=0
while i<lentitlelist:
   try: # the year field is writen by the subtitle uploader so it might be wrongly formatted. it's the only variable that might fail.
      yearint=int(yearlist[i]) # if the year is an number it will be able to convert it to int. If by mistake it's a string it will set it to 0.
   except:
      yearint=0
   subtitlelist.append((languagelist[i],titlelist[i],yearint,int(idlist[i]))) # appends a tuple.
   i=i+1

subtitlelistord=sorted(subtitlelist)

# SQL: CREATE RELATIONAL TABLE FOR EACH LANGUAGE AND INSERT SUBTITLE INFO (IF THE ROW EXISTS OMMIT INSERTING IT)

filesql.executescript('''CREATE TABLE IF NOT EXISTS Subtitle(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,subid INTEGER UNIQUE,title TEXT,
                                                             language_id INTEGER,year_id INTEGER);
                         CREATE TABLE IF NOT EXISTS Language(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,language TEXT UNIQUE);
                         CREATE TABLE IF NOT EXISTS Year(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,year INTEGER UNIQUE);''')

# SQL: INSERT DATA INTO TABLES. The subtitle info will be inserted in alphabetical order by language.

i=0 # moves with the count of a language
j=0 # moves with every language
for lang,count in languagelistord: # the ordered list with the languages and count

   # CLEAN THE LANGUAGE OF PARENTHESIS AND SPACES. E.g. "Chinese (simplified)" converted to "Chinese_simplified"

   langclean=lang.replace('(','_')
   langclean=langclean.replace(')','')
   langclean=langclean.replace(' ','')

   # INSERT LANGUAGE AND RETRIEVE PRIMARY KEY. Doing this here avoids doing it for every subtitle in the list. It's done only once per language.

   filesql.execute('INSERT OR IGNORE INTO Language(language) VALUES (?)',(langclean,)) # insert the language. if it already is there, ommit.
   filesql.execute('SELECT id FROM Language WHERE language=?',(langclean,)) # look for the id created, it is unknown and automatically created
   languageid=filesql.fetchone()[0]

   while i<count: # will insert all subtitles of the same language first, then the next language

      # INSERT YEAR AND RETRIEVE PRIMARY KEY.

      yearint=subtitlelistord[i+j][2] # subtitlelistord is the list with all subtitles, ordered by language alphabetically
      filesql.execute('INSERT OR IGNORE INTO Year(year) VALUES (?)',(yearint,))
      filesql.execute('SELECT id FROM Year WHERE year=?',(yearint,))
      yearid=filesql.fetchone()[0]

      # INSERT SUBTITLE INFO INTO SUBTITLE TABLE

      filesql.execute('INSERT OR IGNORE INTO Subtitle(subid,title,language_id,year_id) VALUES (?,?,?,?)',(subtitlelistord[i+j][3],subtitlelistord[i+j][1],languageid,yearid))
      i=i+1
   j=j+count
   i=0


filesqlcon.commit()
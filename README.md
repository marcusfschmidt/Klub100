# Klub100
 
alt virker

# How to sætte up

For at læse fra Google Sheets kræves autorisering vha. Google Sheets API. Det kræver, at du sletter filen "token.json", skriver en besked til mig og får en mail på en liste. Alternativt skal du oprette dit eget sheet og selv oprette din "Google App". Se link:
https://developers.google.com/sheets/api/quickstart/python

I filen "klub100sheets.py" er der på linje 15 et ID til det Sheets, der bliver brugt:
https://docs.google.com/spreadsheets/d/1JR03yrHEIwk8qJFmEM8Ev5kwxp4IRJydvggDLfpe5F0/edit#gid=1439957427


# How to køre kode

Der står en readme i generateKlub100.py ift. at bruge koden til at tilpasse sin klub100 modulært. Det er lidt tricky og skrevet elendigt, men det virker (sandsynligvis).
Det er i høj grad muligt at ødelægge koden. Beder man f.eks. om en Klub100 med en længde mindre end antallet af sange på det excelark, der læses fra, dør den. Der er en masse af den type skønhedsfejl, som jeg ikke gider fikse. 

Bare brug koden som den skal bruges :)


Thanks for checking out Tweemail!

This is a command line tool used to display or store twitter user data when they publicly tweet their
email along with a key term.  For basic use all you need to do is edit the source code with your
twitter API keys.  For MySQL storage you will need to edit the source with those credentials as well.
Tweemail is easy to configure as a cronjob for longterm harvesting.  Aditionally there is an
experimental TOR socks option to keep harvesting anonymous.

Usage:

Queries to the twitter search API are defined directly from the command line.

-q defines the query string.
./tweemail.py -q "query terms here"

MySQL storage requires you to provide credentials to a database within the programs source.  Username,
name, location, bio, tweet, email, time, followers, following and email will all be stored within a 
table called test.

-m to trigger MySql storage.
./tweemail.py -q "query terms here" -m

TOR tunneling requires the TOR browser to be running on it's default port of 9150.  This function is
still being tested so use it at your own peril.

-t to tunnel through TOR.
./tweemail.py -q "query terms here" -m

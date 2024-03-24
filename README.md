# ChanceBot
## Description:

### Initial idea: 

The dice function was the first one I wrote, thinking about tabletop games and chance; however, I am not a tabletop player, so the drive was not there to implement a whole bot around that concept. I was also mucking around with a Pokemon csv which is very useful to practice data manipulation. Again though, not the biggest fan, so didn't want to implement a whole Discord bot around it. While learning programming, I randomly listened to full albums considered widely popular/influential from various lists and found that, more often than not, it was a pretty good time even though I might not have listened to them of my own choice. 

### What ChanceBot does: 

I created ChanceBot to randomly suggest a movie, album or sci-fi/fantasy novel from popular lists OR for users in a server to create their own recommendations (up to 5). 

### project.py:

This contains the meat of the project. Most of the functions load required csv-based databases or access them. This was a design-choice I decided on early in the project: I wanted to practice using csv file manipulation, and the required data would not be too complex. If I were to scale this up, I would change only the recommendations to a proper database by adding a server-id column to it instead of having each server having its own csv file as is the current implementation.  

Now, I will discuss from the top of project.py to the bottom:

1. The discord bot is created and its commands listen for '!' before a message; the intents are the current methodology for passing various events and info to the bot

2. read_novel_data() & read_movie_data() & read_album_data() all serve the exact same function: they load in the data from their respective csv, and are saved into a variable for easy access

3. csv_check() is used by the bot on initialization (during on_ready()) to create a csv 'database' for each server it is currently in or confirm that one already exists. During on_ready(), each server(guild in Discord's documentation) is then printed to confirm it has a valid csv 'database'. The else should never print because of the logic of csv_check(), but it is here just in case.

4. class Roll and roll(number_of_dice, sides) work together based on Discord's docs. The commands.Converter alter the parameters in a specified way, and the context is what triggers a bot command. The ctx (context) appears throughout the code. This function requires a number of dice to roll and how many sides the dice have. A design descision was made to limit sides and number to 100 since as well as returning the total in the bot's output as well
***
**
if ctx.author == bot.user:
    return
**
This code ensures that a bot does not infinitely call something itself; I do not think it would have been an issue with my commands, but always good to be safe
***
5. coin_flip() and flip() work together to simulate a coin flip. Nothing too out of the ordinary here.

6. newnovel(),newmovie(), newalbum() are all bot commands which randomly return a selection from the loaded csv file that pertains to its name. The function first checks if the database variable exists or else it returns a bot message that there was a problem with its respective csv database.
***
#### The format for the csv 'database' is as follows:

-Named {server_id}.csv where the server_id is a unique instance for each Discord server, so naming conflicts will be avoided

-["UserId","First","Second","Third","Fourth","Fifth"] are the fieldnames for the columns. The UserId is used for a Discord user because, like the server_id, it is unique, no matter how many name changes happen within a server or globally

-I chose to allow only five recommendations per user per server at a time to prevent abuse. I also put a limit as to how long a recommendation could be for the same reasoning
***
7. class Recommends takes the argument provided by the user typing the bot command and uses the MemberConverter to go through a list of possible users based on a priority sequence (Discord has multiple names for every user, and users can change their name on a server to server basis); if no user is found in the server that matches the request, None is returned

8. recommends(user) requires a "member" object from Discord which is returned by Recommends. If there is no user in the server matching the input, the bot informs the one who called the command. Otherwise, search the csv database for that server's recommendations, and return any non-empty recommendations. If the user does not have a row in the csv or all of their recommendation slots are empty, let the person who entered the command know

9. addrecommend(slot, recommendation) needs two arguments. I made the design choice to accept an int for the recommendation slots to make for easier checks, but the trade-off was that I had to use a dicitonary to translate the numbers to the field-names in the csv file. I thought them being named was clearer, so I used this bit of logic to make it easier for a user to type the command while having it more readable behind the scenes. Also check for valid input in terms of value and length of recommendations. 

After opening the csv, it reads the previous data to a variable. Then it checks to see if the user being searched for has a row(entry) already, and updates a boolean that tracks that. The addition update works as an update as well since the logic is the same in either case. This variable is important since to make addition/update to the csv stick, it needs to re-create the csv from scratch with the updated data. 

Additionally, if this is the current user's first recommendation, it adds them to a new row based on their Discord id (immutable, as explained earlier). Re-writing the whole csv database was a trade-off for this approach, but as mentioned earlier, I wanted to dig into what csv could do for a smaller project like this. A more traditional database would have been easier to use, for sure, but I wanted to keep everything to a csv.

10. addrecommend_error() has a Discord wrapper to catch certain errors caused by user input. This gives the user feedback regarding those errors in Discord.

11. removerecommend(slot) adheres to the same logic as add, and was easy to implement after add had already been written. Now, it just replaces anything in the specified slot with an empty string to wipe it. If the user does not have a row in the database, it also accounts for that and creates an empty row with their id. 

12. removerecommend_error() works in the same way its add counterpart, using the Discord wrapper to catch specified errors and returning feedback to the user

13. roulette(*args) takes 2-20 items a user puts in and chooses one of them while checking to see if the input was valid before doing so
***
### main():
For this project, main loads the environmental variable 'DISCORD_TOKEN' which is needed for the bot using load_dotenv(). It then sets it to a variable and runs the bot which listens for commands using the '!' prefix in servers it is connected to 

### Tests:
For the pytests, I ran one test per group of 'like' functions. I document that out using comments in the test_project.py file



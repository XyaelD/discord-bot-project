import os
import random
import csv

import discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

def read_novel_data():
    novels = []
    try:
        with open("top_novels_2023.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                novels.append(row)       
        return novels
    except FileNotFoundError:
        print("Could not open the novels csv!")
        return
    
    
def read_movie_data():
    movies = []
    try:
        with open("top_movies_2023.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                movies.append(row)       
        return movies
    except FileNotFoundError:
        print("Could not open the movies csv!")
        return
 
def read_album_data():
    try:
        albums = []
        with open("albumlist.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                albums.append(row)       
        return albums 
    except FileNotFoundError:
        print("Could not open the albums csv!")
        return  


novel_data = read_novel_data()
movie_data = read_movie_data() 
album_data = read_album_data()  


def csv_check(server_id):
    try:
        with open(f"{server_id}.csv", "r") as _:
            return True
    except FileNotFoundError:
        header = ["UserId","First","Second","Third","Fourth","Fifth"]
        with open(f"{server_id}.csv", "a") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(header)
            return True 
    
    
@bot.event
async def on_ready():
    try:
        for guild in bot.guilds:
            if csv_check(f"{guild.id}"):
                print(f"{guild.id} has a valid csv file")
            else:
                print(f"{guild.id} DOES NOT have a valid csv file")
    except PermissionError:
        print("ChanceBot does not have the permissions needed to read the csv files")

       
class Roll(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            number_of_dice, sides = map(int, argument.split())
            if number_of_dice < 1 or number_of_dice > 100 or sides < 1 or sides > 100:
                return "Please enter a number of dice/sides between 1 and 100"
            results = [random.randint(1, sides) for _ in range(number_of_dice)]
            return f"{ctx.author.display_name} rolled: {results}, and the total is {sum(results)}"
        except ValueError:
            return "Please enter a number of dice/sides between 1 and 100"
    
   
@bot.command(name='roll', help='Rolls a specified number of x-sided dice', description="!roll <number_of_dice:int> <sides:int>")
async def roll(ctx, *, roll: Roll = commands.parameter(description="# of dice 1-100 then # of sides between 1-100")):
    if ctx.author == bot.user:
        return
    await ctx.send(roll)
    return


@roll.error
async def removerecommend_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('The format has to be !roll <number of dice> <sides>') 
        return
   
    
def coin_flip():
    try:
        sides = ["heads", "tails"]
        result = random.choice(sides)
        return result
    except NameError:
        print("Random module is not imported")
        return
    
  
@bot.command(name='flip', help='Flips a coin')
async def flip(ctx):
    if ctx.author == bot.user:
        return
    coin_result = coin_flip()
    await ctx.send(f"{ctx.author.display_name} flipped a coin and it landed on {coin_result}")    
    return

@bot.command(name='newnovel', help="Returns a random sci-fi/fantasy novel/series", description="Based on annual votes from readers")
async def newnovel(ctx):
    if ctx.author == bot.user:
        return
    if novel_data:
        random_novel = random.choice(novel_data)
        await ctx.send(f"{ctx.author.display_name}, your random novel/series is: {random_novel['Series']} by {random_novel['Author']}")
        return
    else:
        await ctx.send(f"Sorry {ctx.author.display_name}, the database for novels could not be reached!")
        return
        
@bot.command(name='newmovie', help="Returns a random movie", description="From IMDB's Top 1000 Movies")
async def newmovie(ctx):
    if ctx.author == bot.user:
        return
    if movie_data:    
        random_movie = random.choice(movie_data)
        await ctx.send(f"{ctx.author.display_name}, your random movie is: {random_movie['title']} directed by {random_movie['director']}")  
        return 
    else:
        await ctx.send(f"Sorry {ctx.author.display_name}, the database for movies could not be reached!")
        return

@bot.command(name='newalbum', help="Returns a random album", description="From The Rolling Stone's 500 Greatest Albums of All Time")
async def newalbum(ctx):
    if ctx.author == bot.user:
        return
    if album_data:    
        random_album = random.choice(album_data)
        await ctx.send(f"{ctx.author.display_name}, your random movie is: {random_album['Album']} by {random_album['Artist']}")
        return
    else:
        await ctx.send(f"Sorry {ctx.author.display_name}, the database for albums could not be reached!")
        return
      
class Recommends(commands.MemberConverter):
    async def convert(self, ctx, user):
        try:
            member = await super().convert(ctx, user)
        except discord.ext.commands.MemberNotFound:
            return None

        return member


@bot.command(name='recommends', help='Returns the recommendations of a specified user', description='!recommends <nickname/global_username/@user>')
async def recommends(ctx, *, user: Recommends = commands.parameter(description="Enter a nickname/global_username/@user")):
    if ctx.author == bot.user:
        return

    if user is None:
        await ctx.send("That user is not in this server!")
        return

    try:
        with open(f"{ctx.guild.id}.csv", "r") as file:
            reader = csv.DictReader(file)
            user_recommendations = next((row for row in reader if int(row['UserId']) == user.id), None)

            if user_recommendations:
                filled_recommendations = [value.strip() for key, value in user_recommendations.items() if key != 'UserId' and value is not None and value.strip() != ""]
                if not filled_recommendations:
                    await ctx.send(f"{user.display_name} does not have any recommendations currently")
                    return
                else:
                    await ctx.send(f"{user.display_name} recommends: {', '.join(filled_recommendations)}")
                    return
            else:
                await ctx.send(f"{user.display_name} does not have any recommendations currently")
                return
    except FileNotFoundError:
        await ctx.send("There was a problem with the database csv!")
        return

@bot.command(name='addrecommend', help='Adds a recommendation', description='!addrecommend <slot 1-5> <"recommendation">')
async def addrecommend(ctx, slot: int = commands.parameter(description="Between slots 1-5"), recommendation: str = commands.parameter(description='Use " " for multi-word choices like "Super Metroid"')):
    slots = {1 : "First", 2 : "Second", 3 : "Third", 4 : "Fourth", 5 : "Fifth"}
    if ctx.author == bot.user:
        return
    if slot < 1 or slot > 5:
        await ctx.send("You need to specify slot 1-5")
        return
    if len(recommendation) > 40:
        await ctx.send("The recommendation must be shorter than 40 characters")
        return
    
    
    id = ctx.author.id
    file_name = f"{ctx.guild.id}.csv"
    existing_recommendations = [] 
    
    
    try:
        with open(file_name, "r") as file:
            reader = csv.DictReader(file)
            existing_recommendations = list(reader)
    except FileNotFoundError:
        await ctx.send("There was a problem with the database csv!")
        return          
    
    
    user_exists = False
            
    for row in existing_recommendations:
        if row['UserId'] == str(id):
            row[slots[slot]] = recommendation
            user_exists = True
            break

    
    if not user_exists:
            new_user = {
            "UserId":f"{id}",
            "First": "",
            "Second": "",
            "Third": "",
            "Fourth": "",
            "Fifth": "",
            }
            new_user[slots[slot]] = recommendation
            existing_recommendations.append(new_user)
            
            
    with open(file_name, "w", newline="") as file:
        fieldnames = ["UserId", "First", "Second", "Third", "Fourth", "Fifth"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_recommendations)    
                        
    await ctx.send(f"{ctx.author.display_name}, your recommendation in slot {slot} has been updated!")   
    return    
        
@addrecommend.error
async def addrecommend_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('The format has to be !addrecommend <slot 1-5> <"title">')  
        return


@bot.command(name='removerecommend', help='Removes a recommendation in a given slot', description='!removerecommend <slot 1-5>')
async def removerecommend(ctx, slot: int = commands.parameter(description="Choose between slots 1-5 to delete")):
    slots = {1 : "First", 2 : "Second", 3 : "Third", 4 : "Fourth", 5 : "Fifth"}
    if ctx.author == bot.user:
        return
    if slot < 1 or slot > 5:
        await ctx.send("You need to specify slot 1-5")
        return
    
    
    id = ctx.author.id
    file_name = f"{ctx.guild.id}.csv"
    existing_recommendations = [] 
    
    
    try:
        with open(file_name, "r") as file:
            reader = csv.DictReader(file)
            existing_recommendations = list(reader)
    except FileNotFoundError:
        await ctx.send("There was a problem with the database csv!")          
        return
    
    user_exists = False
            
    for row in existing_recommendations:
        if row['UserId'] == str(id):
            if row[slots[slot]] == "":
                await ctx.send("That slot is already empty!")
                return
            row[slots[slot]] = ""
            user_exists = True
            break

    
    if not user_exists:
            new_user = {
            "UserId":"",
            "First": "",
            "Second": "",
            "Third": "",
            "Fourth": "",
            "Fifth": "",
            }
            existing_recommendations.append(new_user)
            
            
    with open(file_name, "w", newline="") as file:
        fieldnames = ["UserId", "First", "Second", "Third", "Fourth", "Fifth"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_recommendations)    
                        
    await ctx.send(f"{ctx.author.display_name}, your recommendation in slot {slot} has been removed!")   
    return 

@removerecommend.error
async def removerecommend_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('The format has to be !removerecommend <slot 1-5>') 
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('The format has to be !removerecommend <slot 1-5>') 
        return
    
    
@bot.command(name='roulette', help='Chooses something random from a list you give', description='Specify 2-20 items to choose between, and use " " for multi-word choices like "Super Metroid" as a space is the delimiter for a new item\n\
    ex: !roulette "Mario Kart" "Super Metroid" "Donkey Kong Country"')
async def roulette(ctx, *args):
    if not args:
        await ctx.send("Please give the roulette 2-20 items!")
        return
    choice_list = [*args]
    if len(choice_list) > 20 or len(choice_list) < 2:
        await ctx.send("Please make the roulette have 2-20 items")
        return  
    choice = random.choice(choice_list)
    await ctx.send(f"I have randomly picked: {choice}")
    return  
                 
                      
def main():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    bot.run(TOKEN)
    
    
if __name__ == "__main__":
    main()

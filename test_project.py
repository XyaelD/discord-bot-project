import pytest
import discord
import csv
import os
from discord.ext import commands
from project import newmovie, read_movie_data, coin_flip, flip, csv_check, recommends
from unittest.mock import AsyncMock, Mock, patch, MagicMock


# This decorator allows data/objects to be created for future tests, and the scope allows the same bot instance to be re-used
@pytest.fixture(scope="session")
def bot():
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='!', intents=intents)
    return bot

# This tells pytest this is to be an async test
@pytest.mark.asyncio
# Patching something in the code to always be mock data provided
# In this case, the random_choice should always get the same movie/director provided
@patch('random.choice')
# Define the patch argument as well as any fixtures needed for the test
async def test_newmovie(mock_choice, bot):
    
    # The mock data (could have been a fixture as well, in retrospect)
    mock_movie_data = [
    {"title": "The Shawshank Redemption", "director": "Frank Darabont"},
    ]
    
    # Set the patched function to the mock data
    mock_choice.return_value = mock_movie_data[0]
    # Mock the context for the discord bot as well as the async
    ctx = Mock()
    ctx.author = Mock()
    ctx.send = AsyncMock()

    # Await the results of the test
    await newmovie(ctx)

    # This is what the discord bot would send (always the same because of mock data)
    ctx.send.assert_called_once_with(f"{ctx.author}, your random movie is: The Shawshank Redemption directed by Frank Darabont")
    
# The album and novel functions work exactly the same, so if one works, the logic for all should be correct

# After learning from the first test, the second was easier to implement
@pytest.mark.asyncio
@patch('project.coin_flip')
async def test_flip(mock_flip, bot):
    mock_flip.return_value = "heads"
    ctx = Mock()
    ctx.author = Mock()
    ctx.send = AsyncMock() 
    
    await flip(ctx)
       
    ctx.send.assert_called_once_with(f"{ctx.author} flipped a coin and it landed on heads")
    

# Before the test, create a temporary csv file; request is used for setup and at the end of a fixture
# I had a lot of trial and error during these two tests; couldn't get the logic to behave properly using tmp
@pytest.fixture
def temp_csv_file(request):
    # Create a temporary CSV file for testing
    server_id = "1234567890"
    filename = f"{server_id}.csv"

    # Create the temporary csv file with the server id
    with open(filename, "w") as _:
        pass

    # The function request will use at the end to delete the temporary testfile
    def cleanup():
        # Delete the temporary CSV file after the test
        os.remove(filename)

    # Use request to call cleanup at the end to remove the created file
    request.addfinalizer(cleanup)
    return server_id


# I tested to make sure it behaved as expected by manually setting a return value of 'False' for the creation of a new csv file before switching back to the proper logic of 'True'
def test_csv_check(temp_csv_file):
    # Test the try block when the CSV file with the server id exists
    assert csv_check(temp_csv_file) is True
    # Test the except block when the a CSV file with the server id does not exist
    os.remove(f"{temp_csv_file}.csv")
    assert csv_check(temp_csv_file) is True
    
    
# Create a class to mock the ctx for this particular test case
class MockContext:
    def __init__(self, author, server_id):
        self.author = author
        self.guild = MagicMock(id=server_id)
        self.send = AsyncMock()
    
    
@pytest.mark.asyncio
async def test_recommends(request, bot):
    # Mock an existing user in the database
    existing_user = MagicMock()
    existing_user.id = 12345
    existing_user.display_name = "test"
    non_existing_user = MagicMock()
    non_existing_user.id = 67890
    non_existing_user.display_name = "test2"
    server_id = 123456789
    
    # Create ctx for each call test (the author who triggers the bot command does not matter here)
    ctx = MockContext(author = existing_user, server_id = server_id)
    ctx2 = MockContext(author = existing_user, server_id = server_id)
    filename = f"{server_id}.csv"

    # Create the temporary csv file with the server id and mock user data
    header = ["UserId","First","Second","Third","Fourth","Fifth"]
    mock_user_data = [existing_user.id, "Bloodborne", "", "", "", ""]
    with open(filename, "w") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(header)
            csv_writer.writerow(mock_user_data)
            
    # The function request will use at the end to delete the temporary testfile
    def cleanup():
        # Delete the temporary CSV file after the test
        os.remove(filename)

    # Use request to call cleanup at the end to remove the created file
    request.addfinalizer(cleanup)
    
    # Test that searching for the recommendations of an existing user in the csv returns the appropriate info
    await recommends(ctx, user=existing_user)
    ctx.send.assert_called_once_with(f"{existing_user.display_name} recommends: Bloodborne")
    # Test that searching for the recommendations of a non-existing user returns the appropriate bot message
    await recommends(ctx2, user=non_existing_user)
    ctx2.send.assert_called_once_with(f"{non_existing_user.display_name} does not have any recommendations currently")
    
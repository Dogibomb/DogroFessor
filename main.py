import time
from api_key import API_KEY
import requests
from clash import clash_info
from user import get_User_info_by_puuid, get_summoners_level, print_user_info, get_champions_info_by_puuid_without_input, get_puuid
from freechamps import get_champions_info, get_free_champions
from match_history import get_user_normal_match_history, get_user_ranked_match_history, convert_match_ids

user_input = ''

while(True):
    
    print("\n-------------------------------")

    print("DogoPedia - League of Legends API")
    print("For Summoner info press 1")
    print("For Clash info press 2")
    print("For User Match History press 3")
    print("For Free Champion info press 4")
    print("For Convert puuid to name press 5")
    print("To exit press x")

    print("-------------------------------\n")

    user_input = input("Enter your choice: ")

    print("-------------------------------")

    if user_input == "1":
        puuid = get_puuid()
        summoners_name, summoners_level, summoners_rank = get_summoners_level(puuid)
        print_user_info(summoners_name, summoners_level, puuid, summoners_rank)
        
    elif user_input == "2":
        clash_info()
    elif user_input == "3":
        print("For Normal matches press 1")
        print("For Ranked matches press 2")
        user_input2 = input("Enter your choice: ")
        if user_input2 == "1":
            convert_match_ids(get_user_normal_match_history())
        elif user_input2 == "2":
            convert_match_ids(get_user_ranked_match_history())
    elif user_input == "4":
        get_free_champions()
    elif user_input == "5":
        get_User_info_by_puuid()
    elif user_input == "x":
        break
    else:
        print("Wrong input")
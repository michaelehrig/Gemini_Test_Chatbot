import os
import pickle
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import model_name

def get_chat_list() -> list[str]:
    """
    Generates list of all .cht files in the directory.

    Returns
    -------
    list[str]
        list of all .cht file names in directory
    """
    chat_list = []
    directory_content = os.listdir(os.path.abspath('./'))
    for content in directory_content:
        content_source = os.path.join('./', content)
        if os.path.isfile(content_source):
            base, extension = os.path.splitext(content)
            if extension == '.cht':
                chat_list.append(content)
    return chat_list


def main():
    load_dotenv()
    
    # Obtain API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key == None:
        raise RuntimeError("Api key not found!")

    # Initiate gemini client
    client = genai.Client(api_key=api_key)

    chat_history = []
    
    # Checking whether old chat should be uploaded
    while True:
        answer = input('Do you want to load an old chat? (y/n) ')
        if answer == 'y':
            chat_list = get_chat_list()
            if chat_list == []:
                print('No chats available in the directory.')
                break
            else:
                while True:
                    print("Available chats:")
                    for i,chat in enumerate(chat_list):
                        print(f'{i}: {chat}')
                    number = input('Which chat file (input the number)? ')
                    if number.isdigit():
                        if 0 <= int(number) < len(chat_list):
                            chat_file = chat_list[int(number)]
                            break
                try:
                    with open(chat_file, "rb") as f:
                        chat_history = pickle.load(f)
                        break
                except:
                    print('Could not load file.')
                    break
        if answer == 'n':
            break

    # Initaite chat
    chat = client.chats.create(model=model_name,history=chat_history)
    
    print('\033[91m'+'--------'+'\033[0m')

    # Prompt for a new input
    while True:
        print('User: (\X exit, \S save chat history, \T dump history as JSON)')
        request = input('> ')
        
        # Exit on request
        if request == '\X':
            print('Exiting')
            break

        # Save as proper data structure (pickle file)
        elif request == '\S':
            chat_file = input('Name of the chat file: ')
            chat_file += '.cht'
            try:
                with open(chat_file, 'wb') as f:
                    pickle.dump(chat.get_history(), f)
            except:
                print('Could not save chat.')

        # Dump history in a json file
        elif request == '\T':
            chat_file = input('Name of the json file: ')
            chat_file += '.json'
            history_data = [content.model_dump() for content in chat.get_history()]
            try:
                with open(chat_file, 'w') as f:
                    json.dump(history_data, f, indent=2, ensure_ascii=False)
            except:
                print('Could not save chat.')
        else:
            response = chat.send_message(request)
            print('\033[91m'+'--------'+'\033[0m')
            print('Gemini:')
            print(f'{response.text}')
            print('\033[91m'+'--------'+'\033[0m')


if __name__ == "__main__":
    main()

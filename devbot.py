import google.generativeai as genai
from google.api_core import retry
import os
from random import randint
from typing import Iterable
features = []  # The in-progress order.
inprogress_features = []  # The confirmed, completed order.

project_notes=['the project is blank']
implemented_files=[]
kill_switch=False
import textwrap

def format_response(text):
  text = text.replace('•', '  *')
  return textwrap.indent(text, '> ', predicate=lambda _: True)

def say_goodbye()->None:
   """Use if the user wants to end the session"""
   global kill_switch
   kill_switch=True

def project_status()-> Iterable[tuple[int,str]]:
  """Returns notes on what the project is about"""
  return (project_notes,implemented_files)

def add_project_note(note: str)-> None:
  """Add a note about the project for context later"""
  project_notes.append(note)

def remove_project_note(n: int) -> str:
  """Remove the nth (one-based) note on the note list

  Returns:
    The item that was removed.
  """
  item = project_notes.pop(int(n) - 1)
  return item

def request_feature(title: str, description: str) -> None:
  """Add the specified feature to the list of requested features"""
  features.append((title,description))

def get_features() -> Iterable[tuple[str, str]]:
  """Returns the current feature request list"""
  return features

def remove_feature(n: int) -> str:
  """Remove the nth (one-based) feature on the feature request list

  Returns:
    The item that was removed.
  """
  item = features.pop(int(n) - 1)
  return item

def clear_features() -> None:
  """Removes all items from the feature request list"""
  features.clear()


def confirm_features() -> str:
  """Asks the user if the feature list is correct

  Returns:
    The user's free-text response.
  """

  print('Requested Features:')
  if not features:
    print('  (no items)')

  for title,desc in features:
    print(f'  {title} : {desc}')

  return input('Is this correct? ')


def add_to_file(filename: str,content: str) -> str:
    """Use to write content to the project into files
    Note: remember to include both a name and file extension
    Examples: 
        filename: main.py, templates/index.html, ect
        content: print('hello world')
    Returns:
        A status message about the file 
  """
    try:
        full_filepath = 'sandbox/' + filename
        print(content)
        with open(full_filepath, "w") as file:  # Use "w" for writing only
            file.write(content)  # Write the string directly
            implemented_files.append(filename)
        return f'{filename} was successfully written'
    except Exception as e:
       print(e)
       return 'file was not successfully archive'
    
def overwrite_file(n: int, content: str) -> str:
    """Overwrite the nth (one-based) file in the implemented_files list
    Note: remember to include both a name and file extension
    Examples: 
        main.py, templates/index.html, ect
    Returns:
        A status message about the file 
  """
    try:
        full_filepath = 'sandbox/' + implemented_files[(n-1)]
        with open(full_filepath, "w") as file:  # Use "w" for writing only
            file.writelines(content)  # Write the string directly
        return f'{implemented_files[(n-1)]} was successfully written'
    except:
       return 'file was not successfully archive' 
    

def delete_file(n: int) -> str:
    """Remove the nth (one-based) file in the implemented_files list

    Returns:
        The file that was removed.
    """
    file_path = implemented_files.pop(int(n) - 1)
    try:
        os.remove(f'sandbox/{file_path}')
        return f"File '{file_path}' deleted successfully."
    except FileNotFoundError:
        return f"File '{file_path}' not found."
    
def check_file_contents(n: int)->str:
    """Check on nth (one-based) file in the implemented_files list

    Returns:
        the fil;e contents
    """
    file_path = implemented_files.pop(int(n) - 1)
    try:
        full_filepath = 'sandbox/' + file_path
        with open(full_filepath, "w") as file:  # Use "w" for writing only
            contents=file.read()
        return contents
    except FileNotFoundError:
        return f"File '{file_path}' not found."
    

def run_bot(PROJECT_MANAGER_PROMPT):
    try:

        tools = [request_feature, get_features, remove_feature, clear_features, confirm_features,
                 add_to_file,overwrite_file,delete_file,check_file_contents,
                 project_status,add_project_note,remove_project_note,say_goodbye]

        # Toggle this to switch between Gemini 1.5 with a system instruction, or Gemini 1.0 Pro.
        use_sys_inst = False

        model_name = 'gemini-1.5-pro-latest' if use_sys_inst else 'gemini-1.0-pro-latest'

        if use_sys_inst:
            model = genai.GenerativeModel(
                model_name, tools=tools, system_instruction=PROJECT_MANAGER_PROMPT)
            convo = model.start_chat(enable_automatic_function_calling=True)

        else:
            model = genai.GenerativeModel(model_name, tools=tools)
            convo = model.start_chat(
                history=[
                    {'role': 'user', 'parts': [PROJECT_MANAGER_PROMPT]},
                    {'role': 'model', 'parts': ['OK I understand. I will do my best!']}
                    ],
                enable_automatic_function_calling=True)

        @retry.Retry(initial=30)
        def send_message(message):
            return convo.send_message(message)

        print('Welcome to Dev bot!\n\n')

        global kill_switch

        while kill_switch==False:
            response = send_message(input('> '))
            print(response.text)


        print('\n\n')
        print('[dev bot session over]')
        print()
        print('Requested Features:')
        print(f'  {inprogress_features}\n')
        print('- Thanks for using Dev Bot!')

    except:
       print("session terminate")
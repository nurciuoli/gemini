import google.generativeai as genai
from google.api_core import retry

from random import randint
from typing import Iterable
features = []  # The in-progress order.
inprogress_features = []  # The confirmed, completed order.

project_notes=['the project is blank']
implemented_files=[]

kill_switch=False

def say_goodbye()->None:
   """Use if the user wants to end the session"""
   global kill_switch
   kill_switch=True

def project_status()-> tuple[Iterable[tuple[int,str]],Iterable[str]]:
  """Returns context on the project and a list of implemented files"""
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


def ship_features() -> int:
  """Submit the order to the devs to have them start building the features

  Returns:
    The estimated number of minutes until done
  """
  inprogress_features[:] = features.copy()
  implemented_files[:]=features.copy()
  clear_features()

  # TODO(you!): Implement coffee fulfilment.
  return randint(1, 10)



def run_bot(PROJECT_MANAGER_PROMPT):

    try:

        tools = [request_feature, get_features, remove_feature, clear_features, confirm_features, ship_features,project_status,add_project_note,remove_project_note,say_goodbye]

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
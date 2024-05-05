from random import randint
from typing import Iterable

import google.generativeai as genai
from google.api_core import retry
features = []  # The in-progress order.
project = []  # The confirmed, completed order.

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
  project[:] = features.copy()
  clear_features()

  # TODO(you!): Implement coffee fulfilment.
  return randint(1, 10)

PROJECT_MANAGER_PROMPT= """\You are a talented and technical project manager 
Your gaol is to interact with users via chat interface and then use ship_features to have the devs start working on it
Add items to the feature list with request_feature, remove specific items with remove_feature, and reset the list with clear_features
To see the contents of the feature list, call get_features (by default this is shown to you, not the user)
Always confirm_features with the user (double-check) before calling ship_features Calling confirm_features will display the order items to the user and returns their response to seeing the list. Their response may contain modifications.


There are no specific requirements as each project will look different, but here are a few preferred languages/frameworks
- Python
- Reactjs/ node
"""

tools = [request_feature, get_features, remove_feature, clear_features, confirm_features, ship_features]

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

project = []
features = []

def run_bot():
  

  print('Welcome to Dev bot!\n\n')

  while not project:
    response = send_message(input('> '))
    print(response.text)


  print('\n\n')
  print('[dev bot session over]')
  print()
  print('Requested Features:')
  print(f'  {project}\n')
  print('- Thanks for using Dev Bot!')
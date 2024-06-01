import google.generativeai as genai
# agent class framework
from google.generativeai.types import file_types

import os
import pathlib
import mimetypes
from typing import Iterable
import logging
from itertools import islice

def upload_file(
    path: str | pathlib.Path | os.PathLike,
    *,
    mime_type: str | None = None,
    name: str | None = None,
    display_name: str | None = None,
    resumable: bool = True,
) -> file_types.File:
    """Calls the API to upload a file using a supported file service.

    Args:
        path: The path to the file to be uploaded.
        mime_type: The MIME type of the file. If not provided, it will be
            inferred from the file extension.
        name: The name of the file in the destination (e.g., 'files/sample-image').
            If not provided, a system generated ID will be created.
        display_name: Optional display name of the file.
        resumable: Whether to use the resumable upload protocol. By default, this is enabled.
    Returns:
        file_types.File: The response of the uploaded file.
    """

    path = pathlib.Path(os.fspath(path))

    if mime_type is None:
        mime_type, _ = mimetypes.guess_type(path)

    if name is not None and "/" not in name:
        name = f"files/{name}"

    if display_name is None:
        display_name = path.name

    response = genai.create_file(
        path=path, mime_type=mime_type, name=name, display_name=display_name, resumable=resumable
    )
    return file_types.File(response)


def list_files(page_size=100) -> Iterable[file_types.File]:
    """Calls the API to list files using a supported file service."""
    response = genai.list_files(genai.ListFilesRequest(page_size=page_size))
    for proto in response:
        yield file_types.File(proto)


def get_file(name) -> file_types.File:
    """Calls the API to retrieve a specified file using a supported file service."""
    return file_types.File(genai.get_file(name=name))


def delete_file(name):
    """Calls the API to permanently delete a specified file using a supported file service."""
    if isinstance(name, (file_types.File, genai.File)):
        name = name.name
    request = genai.DeleteFileRequest(name=name)
    genai.delete_file(request=request)


def clean(text: str):
    """Helper function for responses."""
    text = text.replace("\n", " ")
    return text

class Agent:
    def __init__(self,model='gemini-1.0-pro-latest',tools=None):
        self.response=None
        self.messages=None
        self.tools=tools
        try:
            if self.tools is not None:
                self.model=genai.GenerativeModel(model,tools=tools)
            else:
                self.model=genai.GenerativeModel(model)
        except:
            print('nope')

    def generate(self,user_msg):
        self.response = self.model.generate_content(user_msg)
        print(self.response.text)

    def chat(self,user_msg,auto_funct_call=False):
        if self.messages is None:
            self.messages=[]
            self.thread=self.model.start_chat(history=self.messages,enable_automatic_function_calling=auto_funct_call)
        self.response=self.thread.send_message([user_msg])
        print(self.response.text)
    
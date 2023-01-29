from inquirer import (List, prompt)
from prompt_toolkit import (HTML, PromptSession)

options = [
    {'name': 'Add new password', 'value': 'n'},
    {'name': 'Retrieve password', 'value': 'r'},
    {'name': 'Delete password', 'value': 'd'},
    {'name': 'Change password', 'value': 'c'},
    {'name': 'List all', 'value': 'l'},
    {'name': 'Quit', 'value': 'q'},
]

def get_name(opt):
    return f"({opt['value']}) {opt['name']}"

options = [get_name(opt) for opt in options]

session = PromptSession(style=HTML(
    '<style>'
    '{list-style-type: none;}'
    '</style>'
    '<b>{{ message }}</b>'
    '<ul>'
    '{% for choice in choices %}'
    '<li>'
    '<b>{{ choice.name }}</b>'
    '</li>'
    '{% endfor %}'
    '</ul>'
    ))

questions = [
    List(
        'Choose an option',
        choices=options,
    )
]

answer = session.prompt(questions)
choice = answer[1]
print("You selected: ", choice)

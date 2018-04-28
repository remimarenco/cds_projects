import os

from flask import render_template, request, send_from_directory, Flask
from cds_projects import app


@app.route('/helloworld')
def hello_world():
    return "Hello, World!"


class Entry():
    def __init__(self, name, path):
        self.name = name
        self.path = path


class Directory(Entry):
    def __init__(self, name, path, entries):
        Entry.__init__(self, name=name, path=path)
        self.entries = entries


class File(Entry):
    def __init__(self, name, path):
        Entry.__init__(self, name=name, path=path)


def make_tree(path, name):
    tree = Directory(name=name, path=path, entries=[])
    try:
        directory_content = os.listdir(path)
    except OSError:
        pass  # ignore errors
    else:
        for name in directory_content:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                new_entry = make_tree(path=fn, name=name)
            elif name.startswith('.'):
                continue
            else:
                cleaned_path = fn.replace('cds_projects/static/projects/', '')
                new_entry = File(name=name, path=cleaned_path)
            tree.entries.append(new_entry)
    return tree


@app.route('/')
def index():
    # Get content of projects folder
    root_tree = None
    root_tree = make_tree(path='cds_projects/static/projects/', name='projects')

    return render_template('index.html', title='Home', tree=root_tree)

@app.route('/<path:path>')
def send_html(path):
    return send_from_directory('projects', path)
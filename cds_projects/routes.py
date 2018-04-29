import json
import os
import subprocess

from flask import render_template, request, send_from_directory, Flask
from flask_restful import Resource, reqparse

from cds_projects import app, api


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
            if name.startswith('.'):
                continue
            elif os.path.isdir(fn):
                new_entry = make_tree(path=fn, name=name)
                # If new_entry directory contains file, we add it, otherwise we continue
                new_entry_file_entries = [entry for entry in new_entry.entries]
                if len(new_entry_file_entries) == 0:
                    continue
            # Now only files left, we filter out all not .html or .htm
            elif not name.endswith('.html') or name.endswith('.htm'):
                continue
            else:
                cleaned_path = fn.replace('cds_projects/static/projects/', '')
                new_entry = File(name=name, path=cleaned_path)
            tree.entries.append(new_entry)
    return tree


@app.route('/')
def index():
    # Get content of projects folder
    root_tree = make_tree(path='cds_projects/static/projects/', name='projects')

    return render_template('index.html', title='Home', tree=root_tree)


@app.route('/<path:path>')
def send_html(path):
    return send_from_directory('static/projects', path)


# API
project_dict = {
    "test_project_one": "https://github.com/remimarenco/test_project_one.git",
    "test_project_two": "https://github.com/remimarenco/test_project_two.git",
    "wrn": "https://rmarenco@stash.broadinstitute.org/scm/cpds/wrn.git"
}

parser = reqparse.RequestParser()
parser.add_argument("repository", type=dict)

class PostCommit(Resource):
    def post(self):
        # git pull origin master from project_one in /static/projects
        args = parser.parse_args()
        repo_dict = args['repository']
        project_name = repo_dict['name']
        return subprocess.call(['git', '-C', 'cds_projects/static/projects/' + project_name,
                         'pull', 'origin', 'master'])


api.add_resource(PostCommit, '/api/push')

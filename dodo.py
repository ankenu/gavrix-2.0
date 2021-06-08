import glob
from doit.tools import create_folder

# DOIT_CONFIG = {'default_tasks': ['all']}


def task_clean_docs():
    """Clean doc."""
    return {
        'actions': ['rm -rf doc/*'],
    }


def task_docs():
    """Generate new doc."""
    return {
        'actions': ['sphinx-build -M html "doc_src" "doc"', 'rm -rf html'],
    }


def task_pot():
    """Re-create .pot ."""
    return {
            'actions': ['pybabel extract -o translate/app.pot src'],
            'file_dep': glob.glob('src/*.py'),
            'targets': ['translate/app.pot'],
           }


def task_po():
    """Update translations."""
    return {
            'actions': ['pybabel update -D app -d translate -i translate/app.pot'],
            'file_dep': ['translate/app.pot'],
            'targets': ['translate/ru/LC_MESSAGES/app.po'],
           }


def task_mo():
    """Compile translations."""
    return {
            'actions': [
                (create_folder, ['src/ru/LC_MESSAGES']),
                'pybabel compile -l ru -D app -d src -i translate/ru/LC_MESSAGES/app.po'
                       ],
            'file_dep': ['translate/ru/LC_MESSAGES/app.po'],
            'targets': ['src/ru/LC_MESSAGES/app.mo'],
           }


def task_style():
    """Check style against flake8."""
    return {
            'actions': ['flake8 src']
           }


def task_docstyle():
    """Check docstrings against pydocstyle."""
    return {
            'actions': ['pydocstyle src']
           }


def task_all():
    """Perform all build task."""
    return {
            'actions': None,
            'task_dep': ['docs', 'mo'],
            }

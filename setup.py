from setuptools import setup

setup(name='django-rules',
      version='0.1',
      description='Dynamic rule handling',
      author='Anthony Tresontani',
      author_email='dev.tresontani@gmail.com',
      packages=['rules_engine', 'rules_engine.rules_handler'],
      install_requires = ['PEAK-Rules==0.5a1.dev-r2707']
     )

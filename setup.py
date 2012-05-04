from setuptools import setup, find_packages

setup(name='django-rules',
      version='0.1',
      description='Dynamic rule handling',
      author='Anthony Tresontani',
      author_email='dev.tresontani@gmail.com',
      packages=[find_package('rules_engines')],
      install_requires = ['PEAK-Rules==0.5a1.dev-r2707']
     )

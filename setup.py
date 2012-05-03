from distutils.core import setup

requires = ['PEAK-Rules']

setup(name='django-rules',
      version='0.1',
      description='Dynamic rule handling',
      author='Anthony Tresontani',
      author_email='dev.tresontani@gmail.com',
      packages=['rules.core'],
     )

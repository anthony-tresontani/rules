from distutils.core import setup

requires = ['PEAK-Rules==0.5a1.dev-r2707']

setup(name='django-rules',
      version='0.1',
      description='Dynamic rule handling',
      author='Anthony Tresontani',
      author_email='dev.tresontani@gmail.com',
      packages=['rules'],
     )

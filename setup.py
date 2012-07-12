from setuptools import setup

setup(name='django-rules',
      version='0.2.0',
      description='Dynamic rule handling',
      author='Anthony Tresontani',
      author_email='dev.tresontani@gmail.com',
      packages=['rules'],
      install_requires = ['PEAK-Rules==0.5a1.dev-r2707', 'django==1.2']
     )

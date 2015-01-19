# doppelgoogle

Installation instructions:

first install git, python 2.7, pip, and virtualenv. On a Unix system with a decent package manager this should be cake. Sorry Windows users!

Now in the directory where you want to store this project:

```bash
mkdir <PROJECT_NAME> && cd <PROJECT_NAME>
git clone git@github.com:jpoler/doppelgoogle.git
cd doppelgoogle
```
I have written a bash script to set up your virtualenv in a folder called env, activate the env, install all python dependencies, and to add the project directory to the PYTHONPATH so that you can import using package syntax.

To run, simply use

```bash
j setup
```

Now you should be free to run commands from the doppelgoogle directory, for instance:

```bash
python dg.py --crawl <SEED_URL>
```

or

```bash
python dg.py --server <HOSTNAME> <PORT>
```
If you want even easier, try the following commands using j, a convenience program that uses make to execute arbitrary commands from a makefile. Really useful!

This defaults to crawling with a seed of www.google.com
```bash
j crawl
```

or 

Eventually will start a server on localhost:8080
```bash
j server
```
Note: server is not implemented yet!


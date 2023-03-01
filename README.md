# Low-Code Data Analysis Platform

University of
Liverpool [2022/23 COMP208 Group Software Project](https://tulip.liv.ac.uk/mods/student/COMP208_202223.htm) - Team 16:
Project Source Code

### Welcome

This is the code repo of COMP208 Team 16.

## Reqirements

### git PUSH

<strong>Think twice before git PUSH. 三思而后行</strong>(Chinese) It may affect other contributors and the web server.

Please ensure that your push does not interfere with the normal function of the original. Please carry out tests first.

### ```requirements.txt```

>Python requirements files are a great way to keep track of the Python modules. It is a simple text file that saves a list of the modules and packages required by your project. By creating a Python requirements.txt file, you save yourself the hassle of having to track down and install all of the required modules manually.
[Reference](https://learnpython.com/blog/python-requirements-file/)

<strong>This is one of the key file for deployment.</strong>
Deployment fails if the package used is not in this list.
So make sure that you update the requirements.txt file when using new Python packages.
```shell
# install pipreqs if you don't have it
pip install pipreqs
```

```shell
# generate requirements.txt in the current directory
pipreqs . --encoding=utf8
```

All done!


## Documents

**Offical documents:**

* Flask: [English](https://flask.palletsprojects.com/en/latest/) | [简体中文](https://dormousehole.readthedocs.io/en/latest/)
* Flask-SQLAlchemy: [English](https://flask-sqlalchemy.palletsprojects.com/en/latest/)
* Flask-Email: [English](https://pythonhosted.org/Flask-Mail/)
* Vue: [English](https://vuejs.org/guide/introduction.html) | [简体中文](https://cn.vuejs.org/guide/introduction.html)
* Bootstrap: [English](https://getbootstrap.com/docs/5.3/getting-started/introduction/) | [简体中文](https://v5.bootcss.com/docs/getting-started/introduction/)
* MDBootstrap: [English](https://mdbootstrap.com/)

**Unofficial documents**

* Flask extension documentation: [简体中文](https://wizardforcel.gitbooks.io/flask-extension-docs/content/)

### Creating an environment from a yaml file

You can find the YAML file `environment.yml` [here](./misc/conda_env_config). Please refer to
the [instructions](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file)
to create the environment.

Alternatively, you can update your environment using:

```shell
conda env update --name COMP208 --file environment.yml --prune
```

Please remember
to [update the YAML file](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-file-manually)
after installing new python packages.

Maintaining YAML files manually instead of generating them automatically can ensure that the file is compatible with
both x86 and arm64 architectures.

### Install python packages use requirements.txt

**Please use conda first to install python packages.** Mixed use of conda and pip might cause some problems.
Chances are, some packages would only be available through pip.

Jetbrains IDEs will automatically detect the requirements.txt file. 
Click "Install" to install all the packages.
(Recommended)

Or you can use one of the following commands to install the packages:


```shell
# Use conda
conda install --yes --file requirements.txt
```

```shell
# Use pip
pip install -r requirements.txt
```

### Others

You can learn more about git from git-scm.com: [English](https://git-scm.com/book/en/v2)
| [简体中文](https://git-scm.com/book/zh/v2)

Or you can read “Flight rules for Git” for a more accessible
tutorial: [English](https://github.com/k88hudson/git-flight-rules/blob/master/README.md)
| [简体中文](https://github.com/k88hudson/git-flight-rules/blob/master/README_zh-CN.md)

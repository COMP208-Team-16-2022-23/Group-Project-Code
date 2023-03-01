# Low-Code Data Analysis Platform

University of
Liverpool [2022/23 COMP208 Group Software Project](https://tulip.liv.ac.uk/mods/student/COMP208_202223.htm) - Team 16:
Project Source Code

### Welcome

This is the code repo of COMP208 Team 16.

### Documents

**Offical documents:**

* Flask: [English](https://flask.palletsprojects.com/en/latest/) | [Simplified Chinese](https://dormousehole.readthedocs.io/en/latest/)
* Flask-SQLAlchemy: [English](https://flask-sqlalchemy.palletsprojects.com/en/latest/)
* Flask-Email: [English](https://pythonhosted.org/Flask-Mail/)
* Vue: [English](https://vuejs.org/guide/introduction.html) | [Simplified Chinese](https://cn.vuejs.org/guide/introduction.html)
* Bootstrap: [English](https://getbootstrap.com/docs/5.3/getting-started/introduction/) | [Simplified Chinese](https://v5.bootcss.com/docs/getting-started/introduction/)
* MDBootstrap: [English](https://mdbootstrap.com/)

**Unofficial documents**

* Flask extension documentation: [Simplified Chinese](https://wizardforcel.gitbooks.io/flask-extension-docs/content/)

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

**Please use conda first to install python packages.** Mixed use of conda and pip may cause some problems.

Jetbrains IDEs will automatically detect the requirements.txt file and install the packages with one click.

Or you can use the following command to install the packages:

```shell
conda install --yes --file requirements.txt
```    

Please remember to update the requirements.txt file when using new python packages.

```shell
# install pipreqs if you don't have it
conda install -c conda-forge pipreqs
# generate requirements.txt in the current directory
pipreqs . --encoding=utf8
```

### Advice

Think twice before git PUSH.

You can learn more about git from git-scm.com: [English](https://git-scm.com/book/en/v2)
| [Simplified Chinese](https://git-scm.com/book/zh/v2)

Or you can read “Flight rules for Git” for a more accessible
tutorial: [English](https://github.com/k88hudson/git-flight-rules/blob/master/README.md)
| [Simplified Chinese](https://github.com/k88hudson/git-flight-rules/blob/master/README_zh-CN.md)

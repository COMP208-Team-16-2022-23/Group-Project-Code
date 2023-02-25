# Low-Code Data Analysis Platform
University of
Liverpool [2022/23 COMP208 Group Software Project](https://tulip.liv.ac.uk/mods/student/COMP208_202223.htm) - Team 16:
Project Source Code

### Welcome

This is the code repo of COMP208 Team 16.

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
Jetbrains IDEs will automatically detect the requirements.txt file and install the packages with one click.

Or you can use the following command to install the packages:
```shell
pip install -r requirements.txt
```    
Please remember to update the requirements.txt file when using new python packages.
```shell
# install pipreqs
pip install pipreqs
 ```
 ```shell
# generate requirements.txt in the current directory
pipreqs . --encoding=utf8 --force
```

### Advice

Think twice before git PUSH.

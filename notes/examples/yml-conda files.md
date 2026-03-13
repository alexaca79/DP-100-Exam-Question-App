# What is a ``conda.yml`` file

It's a plain text file that lists all **packages/libraries/modules** that a program (in this case, a ML model) needs to work properly.

**NOTE** conda is a tool to create and manage *virtual environments and packages*. Think about it as a configuration language — it has its own rules and structure for deploying things on cloud services.

# What is it for?

When a model is deployed (e.g., as an Azure endpoint) we need to ensure that the *environment* has the **exact same libraries** that we used to train the model, such as ``scikit-learn, numpy, pandas`` and so on. The **conda.yml** file tells Azure (or the execution environment) "Hey, install these packages to ensure everything works correctly".

# What does it have?

Let's check out this simple example:

```yaml
name: my-environment
channels:
  - conda-forge # this is an open-source channel where most people publish packages for Python programs
dependencies:
  - python=3.8
  - numpy
  - pandas
  - scikit-learn
```

 * name: name of the environment we are going to create
 * channels: where the packages are going to be loaded from
 * dependencies: actual modules to install

# How to "program" it?

Well, it is not exactly code itself — we simply write down the libraries in a YAML (very readable and sorted way) and save it.

# How to use it in Azure?


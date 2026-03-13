# What is a ``conda.yml`` file

It's a plain text file that list all **pachages/libraries/modules** that a program (in this case, a ML model) needs to work properly.

**NOTE** conda is a tool to create and manage *virtual envoroment and packages*- Think about it as a git language or something like that. Has its own rules and structure but to deploy things on cloud services

# What is it for?

When a model is deployed (As in Azure endpoint) we need to assure that the *enviroment* has the **exactly same libraries** that we used the model to train it, such as ``scikit-learn, numpy, pandas`` and so on. And basically the **conda.yml** file talks directly to Azure (or the exucution enviroment "Hey, install this packages in order to assure that everything will work just fine").

# What does it have?

Let's checkout this simply example:

```yaml
name: mi-entorno
channels:
  - conda-forge # this is an open-source channel where most people will publish packages to our python programs
dependencies:
  - python=3.8
  - numpy
  - pandas
  - scikit-learn
```

 * name: name of the envuroment we are going to reate
 * channels: where the package are going to be loaded
 * dependencies: actual modules to charge

# How to "program" it?

Well, it is not exactly code it itself, we simply write down the libraries in a YAML (very readble and sorted way) and save it. Chat GPT easily could create a yaml file with that telling him the details required in our dev enviroment. 

# How to use it in Azure?


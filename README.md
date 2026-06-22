# StudentIsleWars
Isle Wars Game for Testing Student Code

Note that this code is (partially intentionally) bad and will crash or infinite loop depending on what your bot chooses to do.

When crashing during conquer, the conquered(SOURCE, TARGET). predicate will not be written to the agent info file. You can manually add it by looking at the last successful attack in the console log and creating the predicate yourself to test.

You will need to create a virtual environment and pip install embasp-python for this project. You must also, after pip installing embasp-python, go into the lib/specializations/dlv/dlv_filter_option.py and change the __init__() to have the code below instead of the append-to-options that exists there already:
```
super(DLVFilterOption, self).__init__()
super().add_option(initial_option)
```

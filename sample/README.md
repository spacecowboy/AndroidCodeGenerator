This project is already set up for the generated files.

Make sure you are in the base directory of the project,
same directory as __sample.py__. Then do

```
> python sample.py
```

This will generate the files and place them in the accurate
directories. All you need to then is build the project.
Either import in Eclipse and do what you usually do, or
just use ant to build and install directly (have your device
connected through usb or emulated running).

First line is only required the first time to point at the correct
location for you sdk. You might have to write the entire path
to android, like _/home/name/your/dir/android-sdk/tools/android_.

```
> android update project -p .
> ant debug; ant installd
```

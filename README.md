# pal
Your Personal Activity Log

Your activity log is a lightweight record of the low level tasks that you have performed
over time.

Stop fishing your `git log` and Slack messages to remember past activities.

## Quick Start

Run the `pal` executable to log the latest activities

```sh
$ pal
```

Run comes with a set of commands to manage your activities:

```sh
$ pal commit "Hey, This is a new activity"
```

And then you can see it with

```sh
$ pal log
```

Once you have already reported your current activity, you can mark them and they
will not appear in later `log`s.

```sh
$ pal report
```

```sh
$ pal log
```

(You can always show them again with the `-r/--include-reported` flag)

Once you finished with a project, you can cleanup the old entries: 

```sh
$ pal clean
```

See the [Usage Guide](#usage-guide) for more information and advanced usage.

## Installation

`pal` is distributed as a Python package. You can install it using `pip` at `pal-log`:

```sh
$ pip install pal-log
```

At this point you can start using `pal` normally.

```sh
$ pal
```

An alternative way is to use the github repo directly. For that, clone this repo and run: 

```sh
$ pip install .
```

And the `pal` executable should be ready for use.

## Development

For development you can use the `dev` extra, like so:

```sh
$ pip install -e '.[dev]'
```

Which will install `pal` with all the development dependencies.
This project has `pre-commit` for automated linting / formatting.

We recommed you install it and setup in this repo. For that, follow the [installation instructions](https://pre-commit.com/#installation), and then run the following command at the root of the repo:

```sh
$ pre-commit install
```

At this point, a set of automated checks will run before you can `git commit` your changes.

You can manually run the checks as well with: 

```sh
$ pre-commit run [--all-files]
```

## Usage Guide

Apart from the basic usage, PAL also contains other concepts that make it more
useful for more complex scenarios:

- It contains the notion of **author**: every entry is associated to an **author**. You can use `-a/--author` or the `PAL_AUTHOR` environment variable to change the author when commiting or displaying the entries.
- It contains the notion of **project**: every entry is associated to an **project**. You can use `-p/--project` or the `PAL_PROJECT` environment variable to change the project when commiting or displaying the entries.

These two act as namespaces that make it easy to use `pal` when working on multiple projects.
However, `pal` provides default values for those so that is easier to get started. 

- `author`: the default author is the OS username (`$USER` env variable). This is the one that you will be using most often. You can change it for instance to keep work and personal projects.
- `project`: the default project is `default`. You are encouraged to use as many as you like.

If you specify both an env variable and a CLI argument, the CLI argument will have priority.

The fact that these are controlled with environment variables make this specially interesting when combined with tools like [direnv](https://direnv.net/) or other tools that automatically change environments based on directory specific configurations.

You can have an entry so that your `PAL_PROJECT` is set to a given project and you can quickly 
log the activities for this particular project / repo. When you are ready for reporting your advances, you can just call:

```sh
$ pal
```

And the most recent (unreported) tasks will show up. 
Once you are done with them, mark them as reported: 

```sh
$ pal report
```

And continue working.


### Integrations

PAL is mainly intended as the final consumer of the information. 
However, you can request the log output as `--json`, which you can then feed 
to `jq` or other tools to build a pipeline.


```sh
$ pal log --json | jq .
[
  {
    "text": "Added new documentation",
    "author": "alvaro",
    "project": "default",
    "timestamp": "2023-10-20T23:23:58.985532",
    "reported": false,
    "created_at": "2023-10-20T23:23:58.985609+02:00",
    "updated_at": "2023-10-20T23:23:58.985609+02:00"
  },
  {
    "text": "Created a new feature",
    "author": "alvaro",
    "project": "default",
    "timestamp": "2023-10-20T23:23:42.937248",
    "reported": false,
    "created_at": "2023-10-20T23:23:42.937330+02:00",
    "updated_at": "2023-10-20T23:23:42.937330+02:00"
  },
  {
    "text": "Fixed a bug in the CLI",
    "author": "alvaro",
    "project": "default",
    "timestamp": "2023-10-20T23:23:32.699920",
    "reported": false,
    "created_at": "2023-10-20T23:23:32.700029+02:00",
    "updated_at": "2023-10-20T23:23:32.700029+02:00"
  },
  {
    "text": "Welcome to PAL",
    "author": "alvaro",
    "project": "default",
    "timestamp": "2023-10-20T23:23:07.721046",
    "reported": false,
    "created_at": "2023-10-20T23:23:07.721125+02:00",
    "updated_at": "2023-10-20T23:23:07.721125+02:00"
  }
]
```


## How it works

PAL is just a CLI to record timestamped entries on a log. 

Currently, the log is a simple SQLite database stored in your user files.
You can inspect it with any SQLite compatible tool:

```sh
$ sqlite3 $(pal --show-db) 
```

And start querying your database.

Each entry contains a `timestamp` and a `reported` boolean flag that control how
and if they are displayed with `pal log`.

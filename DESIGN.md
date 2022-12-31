# PAL Design

I imagine the UX being similar to how git works.

You would have a:

```sh
pal add
```

```sh
pal log
```

Command that would show a summary of your recent activities, in a git log like format.
Since we are using `rich`, we could maybe try to be a bit fancier with the formatting, while having
a mode for non-interactive users without the fancy formatting for scripting.

## Current Plan

Let's start with a very basic flat JSON file database, and move up from there.
Let's keep the JSON sorted so that we can just append new lines into the file
when adding.

Let's implement adding, which will

## Main Features

- [x] Write a log entry
- [x] List log entries
    - [x] Sorted by most recent
- [x] Read the author from an environment variable
    - [ ] We could default to the username...
- [ ] init command
    - [ ] Creates a palfile
    - [ ] Sets the project and default author name

## A Log Entry

A log entry should contain the following information:

- id (internal)
- author
- timestamp
- header
- body
- created_at
- updated_at


### Questions

- Does it make sense to have a date time and `created_at` and `updated_at`?
    - I think so... but not sure if this will lead to inconsistencies...

## Persistence

I see 2 main options:

1. A text file based structure, kind of like what git uses.
    - Pros:
        - Simplicity: 
        - Flexibility: I could allow for scripting with regular UNIX tools
        - You could even think of committing it to github
    - Cons:
        - We need to design it
        - We need to implement every feature on top of it
        - Probaly a larger storage requirements (not 100% sure though?)
        - Could incite fiddling with the storage files, which could corrupt the database
        - Performance
2. A proper DB with sqlite
    - Pros:
        - Not that complicated
        - Well known tools for handling it (SQL)
        - Can use the vast SQL language to implement other features (search, statistics, dates, etc)
    - Cons:
        - Another large dependency
            - Can we statically link it in the binary? Does python allow for that?
            - We would probably require a wheel building process, so more complication for maintaining it
        - Hard to script against
            - We would make it non-protected so that anyone could connect to the DB, but it's not that simple
            - We would need to offer more APIs for scripts

## Wishlist

- [ ] Global config file for setting author
- [ ] Editing an existing entry
- [ ] Integrating with $EDITOR
    - [ ] Follow a pattern similar to 
- [ ] A machine readable output for ease of automation (JSON?)
- [ ] Set of filters for limiting and searching through your log
- [ ] Project-like structure, so that you can store multiple independent logs
    - [ ] Use an env variable to know which project you are talking about
    - [ ] Read a .pal file in the pwd to use have a default project when working on a directory (e.g: work project A, personal project B)
- [ ] Basic markdown formatting support
- [ ] Linking to other entries
- [ ] Activity Graphs
    - [ ] Line plot
    - [ ] Bar plot
    - [ ] Github like calendar / mosaic plot
    - Do this in an `extra` (do not depend on heavy image dependencies by default?)

## Far Future Ideas

- [ ] Multi author log?
- [ ] Including media in the entries?

[![Python Tests](https://github.com/sopel-irc/sopel-bucket/actions/workflows/python-tests.yml/badge.svg?branch=master)](https://github.com/sopel-irc/sopel-bucket/actions/workflows/python-tests.yml)
[![PyPI version](https://badge.fury.io/py/sopel-bucket.svg)](https://badge.fury.io/py/sopel-bucket)

**Maintainer:** [@RustyBower](https://github.com/rustybower)

# sopel-bucket

A working re-implementation of the xkcd bucket bot for Sopel.

> **Note:** This package was previously published as `sopel-modules.bucket`.
> Please update your dependencies to use `sopel-bucket` instead.

# Requirements

apt-get install libmysqlclient-dev

# Usage
## Quotes
```
<User> Bot: random quote
<Bot> <User> Funny Quote
```

```
<User> Bot: random user
<Bot> <User> Another Funny Quote
```

```
<User> Bot: remember user2 word
<Bot> User: Remembered <User2> A Third Funny Quote
```

## Inventory
```
<User> Bot: you need new things
Bot drops all his inventory and picks up random things instead
```

```
<User> Bot: have an item
Bot takes an item but drops another item
```

```
<User> Bot: inventory
Bot is carrying an item, another item, a third item
```

[![Build Status](https://travis-ci.com/sopel-irc/sopel-bucket.svg?branch=master)](https://travis-ci.com/sopel-irc/sopel-bucket)
[![Maintainability](https://api.codeclimate.com/v1/badges/b0ce232ed04c6ff85e64/maintainability)](https://codeclimate.com/github/sopel-irc/sopel-bucket/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/b0ce232ed04c6ff85e64/test_coverage)](https://codeclimate.com/github/sopel-irc/sopel-bucket/test_coverage)

# Sopel Bucket

Sopel Bucket is a rewritten module from the old Bucket

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

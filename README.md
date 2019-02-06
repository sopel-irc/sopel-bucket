[![Build Status](https://travis-ci.com/RustyBower/sopel-bucket.svg?branch=master)](https://travis-ci.com/RustyBower/sopel-bucket)
[![Maintainability](https://api.codeclimate.com/v1/badges/43154ee379640b3e56a0/maintainability)](https://codeclimate.com/github/RustyBower/sopel-bucket/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/43154ee379640b3e56a0/test_coverage)](https://codeclimate.com/github/RustyBower/sopel-bucket/test_coverage)

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

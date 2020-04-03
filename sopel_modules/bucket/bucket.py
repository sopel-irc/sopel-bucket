# coding=utf-8
import re
from collections import deque
from random import seed
from time import time

from sopel.config.types import StaticSection, ValidatedAttribute
from sopel.module import rule, priority
from sopel.tools import Ddict
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy import create_engine, event, exc
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import Pool
from sqlalchemy.sql.functions import random


# Define a few global variables for database interaction
Base = declarative_base()


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()


# Define Bucket Items
class BucketItems(Base):
    __tablename__ = 'bucket_items'
    id = Column(Integer, primary_key=True)
    channel = Column(String(64))
    what = Column(String(96))
    user = Column(String(64))


# Define Bucket Facts
class BucketFacts(Base):
    __tablename__ = 'bucket_facts'
    id = Column(Integer, primary_key=True)
    fact = Column(String(96))
    tidbit = Column(Text)


# Define Bucket inventory
class Inventory():
    ''' Everything inventory related '''
    available_items = set()
    current_items = deque()

    def add(self, item, user, channel, bot):
        ''' Adds an item to the inventory'''
        dropped = False
        item = item.strip()
        if item.lower() not in [x.lower() for x in self.available_items]:
            session = bot.memory['session']
            try:
                new_item = BucketItems(channel=channel, what=item, user=user)
                session.add(new_item)
                session.commit()
                self.available_items.add(item)
            except:
                # bot.debug('bucket', 'IntegrityError in inventory code', 'warning')
                # bot.debug('bucket', str(e), 'warning')
                raise
            finally:
                session.close()
        if item in self.current_items:
            return '%ERROR% duplicate item %ERROR%'
        if len(self.current_items) >= int(bot.config.bucket.inv_size):
            dropped = self.current_items.pop()
        self.current_items.appendleft(item)
        return dropped

    def populate(self, bot):
        ''' Clears the inventory and fill it with random items '''
        self.current_items.clear()

        session = bot.memory['session']
        res = session.query(BucketItems.what).order_by(random()).limit(bot.config.bucket.inv_size).all()
        session.close()
        for item in res:
            self.current_items.append(item[0])
        return


# Define our Sopel Bucket configuration
class BucketSection(StaticSection):
    # TODO some validation rules maybe?
    db_host = ValidatedAttribute('db_host', str, default='localhost')
    db_user = ValidatedAttribute('db_user', str, default='bucket')
    db_pass = ValidatedAttribute('db_pass', str)
    db_name = ValidatedAttribute('db_name', str, default='bucket')
    inv_size = ValidatedAttribute('inv_size', default='15')


# Walk the user through defining variables required
def configure(config):
    config.define_section('bucket', BucketSection)
    config.bucket.configure_setting(
        'db_host',
        'Enter ip/hostname for MySQL server:'
    )
    config.bucket.configure_setting(
        'db_user',
        'Enter user for MySQL db:'
    )
    config.bucket.configure_setting(
        'db_pass',
        'Enter password for MySQL db:'
    )
    config.bucket.configure_setting(
        'db_name',
        'Enter name for MySQL db:'
    )


# Initial bot setup
def setup(bot):
    bot.config.define_section('bucket', BucketSection)

    db_host = bot.config.bucket.db_host
    db_user = bot.config.bucket.db_user
    db_pass = bot.config.bucket.db_pass
    db_name = bot.config.bucket.db_name

    engine = create_engine('mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4' % (db_user, db_pass, db_host, db_name), encoding='utf8')

    # Catch any errors connecting to MySQL
    try:
        engine.connect()
    except OperationalError:
        print("OperationalError: Unable to connect to MySQL database.")
        raise

    # Create MySQL tables
    Base.metadata.create_all(engine)

    # Initialize our RNG
    seed()

    # Ensure that required variables are in memory
    if not bot.memory.contains('inventory'):
        bot.memory['inventory'] = Inventory()
    if not bot.memory.contains('last_teach'):
        bot.memory['last_teach'] = {}
    if not bot.memory.contains('last_said'):
        bot.memory['last_said'] = {}
    if not bot.memory.contains('last_lines'):
        bot.memory['last_lines'] = Ddict(dict)  # For quotes.

    # Set up a session for database interaction
    session = scoped_session(sessionmaker())
    session.configure(bind=engine)
    bot.memory['session'] = session

    # Populate the bot's inventory
    bot.memory['inventory'].populate(bot)


def remove_punctuation(string):
    return re.sub(r"[,\.\!\?\;\:]", '', string)


def add_fact(bot, trigger, fact, tidbit):
    try:
        session = bot.memory['session']
        try:
            new_item = BucketFacts(fact=fact, tidbit=tidbit)
            session.add(new_item)
            session.commit()
        except:
            # bot.debug('bucket', 'IntegrityError in inventory code', 'warning')
            # bot.debug('bucket', str(e), 'warning')
            raise
        finally:
            session.close()
    except:
        raise
    finally:
        session.close()
    bot.memory['last_teach'][trigger.sender] = [fact, tidbit, trigger.nick]
    return True


@rule('$nick' '(take|have) (.*)')
def inv_give(bot, trigger):
    ''' Called when someone gives us an item '''
    inventory = bot.memory['inventory']
    item = (trigger.group(2))

    # Check to see if we actually got an item or an empty space
    if len(item) > 0:
        dropped = inventory.add(item.strip(), trigger.nick, trigger.sender, bot)
        if not dropped:
            # Query for 'takes item'
            bot.say("Oh, thanks, I'll keep %s safe" % item.strip())
        elif dropped == '%ERROR% duplicate item %ERROR%':
            # Query for 'duplicate item'
            bot.say("No thanks, I've already got %s" % item.strip())
        else:
            # Query for 'pickup full'
            bot.action('takes %s but drops %s' % (item.strip(), dropped))
    else:
        return

    return


@rule('$nick' 'inventory')
@priority('medium')
def get_inventory(bot, trigger):
    ''' get a human readable list of the bucket inventory '''
    inventory = bot.memory['inventory']
    if len(inventory.current_items) == 0:
        return bot.action('is carrying nothing')
    readable_item_list = '\x0F, '.join(inventory.current_items)
    bot.action('is carrying ' + readable_item_list)


@rule('$nick' 'you need new things')
@priority('medium')
def inv_populate(bot, trigger):
    # bucket_runtime_data.inhibit_reply = trigger
    inventory = bot.memory['inventory']
    bot.action('drops all his inventory and picks up random things instead')
    inventory.populate(bot)


@rule('$nick' 'remember (.*?) (.*)')
@priority('high')
def save_quote(bot, trigger):
    """Saves a quote"""
    quotee = trigger.group(1).lower()
    word = trigger.group(2).strip()
    fact = quotee + ' quotes'
    try:
        memory = bot.memory['last_lines'][trigger.sender][quotee]
    except KeyError:
        bot.say("Sorry, I don't remember what '%s' said about %s" % (quotee, word))
        return
    for line in memory:
        if remove_punctuation(word.lower()) in remove_punctuation(line[0].lower()):
            quotee = line[1]
            line = line[0]
            if line.startswith('\001ACTION'):
                line = line[len('\001ACTION '):-1]
                tidbit = '* %s %s' % (quotee, line)
            else:
                tidbit = '<%s> %s' % (quotee, line)
            result = add_fact(bot, trigger, fact, tidbit)
            if result:
                bot.reply("Remembered %s" % (tidbit))
            return
    bot.say("Sorry, I don't remember what %s said about %s" % (quotee, word))


@rule('$nick' 'random (.*)')
def random_quote(bot, trigger):
    choice = trigger.group(1)
    choice = choice.strip()
    ''' Called when someone wants a random quote '''
    if choice == 'quote':
        session = bot.memory['session']
        res = session.query(BucketFacts).order_by(random()).limit(1).one_or_none()
        session.close()
        if res:
            return bot.say(res.tidbit)
    else:
        session = bot.memory['session']
        res = session.query(BucketFacts).filter(BucketFacts.fact == '%s quotes' % choice.strip()).order_by(random()).limit(1).one_or_none()
        session.close()
        if res:
            return bot.say(res.tidbit)


@rule('(.*)')
@priority('medium')
def remember(bot, trigger):
    ''' Remember last 30 lines of each user, to use in the quote function '''
    memory = bot.memory['last_lines']
    nick = trigger.nick.lower()
    if nick not in memory[trigger.sender]:
        memory[trigger.sender][nick] = []
    fifo = deque(memory[trigger.sender][nick])
    if len(fifo) == 30:
        fifo.pop()
    fifo.appendleft([trigger.group(0), trigger.nick])
    memory[trigger.sender][trigger.nick.lower()] = fifo
    if not trigger.sender.is_nick():
        bot.memory['last_said'][trigger.sender] = time()

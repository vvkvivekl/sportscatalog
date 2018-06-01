from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Sport, Base, SportItem, User

engine = create_engine('sqlite:///sports.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Vivek Lingayat", email="vvk.vivek.v@gmail.com",
             picture='https://avatars1.githubusercontent.com/u/36252861')
session.add(User1)
session.commit()

# Kit for Soccer
sport1 = Sport(user_id=1, name="Soccer")

session.add(sport1)
session.commit()

SportItem1 = SportItem(user_id=1, name="Two shinguards", description="A shin guard or shin pad is a piece of equipment worn on the front of a player's shin to protect them from injury. These are commonly used in sports including association football, baseball, ice hockey, field hockey, lacrosse, cricket, and other sports. This is due to either being required by the rules/laws of the sport or worn voluntarily by the participants for protective measures.",
                     sport=sport1)

session.add(SportItem1)
session.commit()

SportItem2 = SportItem(user_id=1, name="Uniform", description="Most youth soccer leagues require a standard uniform for all players. This might range from a simple T-shirt to a complete soccer uniform with matching jersey, shorts and socks. Some leagues issue the uniform to players, while others require you to order the uniform yourself.",
                     sport=sport1)

session.add(SportItem2)
session.commit()

SportItem3 = SportItem(user_id=1, name="Practice clothes", description="Uniforms are typically reserved for wear in games only, so your little kicker needs comfortable athletic clothes for soccer practice. Choose clothes that allow a full range of motion. Sweat-wicking material keeps your child cool and dry during sweaty warm-weather practices.",
                     sport=sport1)

session.add(SportItem3)
session.commit()

SportItem4 = SportItem(user_id=1, name="Soccer cleats", description="When your child plays in an organized league, you likely need soccer-specific cleats. These shoes are designed for the sport to give your soccer player the support and traction necessary in the game.",
                     sport=sport1)

session.add(SportItem4)
session.commit()

SportItem5 = SportItem(user_id=1, name="Soccer socks", description="Just like your child needs special shoes, she also needs special socks designed for soccer. The long socks go up and over the shin guards.",
                     sport=sport1)

session.add(SportItem5)
session.commit()


# Kit for Basketball
sport2 = Sport(user_id=1, name="Basketball")

session.add(sport2)
session.commit()

SportItem1 = SportItem(user_id=1, name="The Ball", description="The most important thing for training is the ball. There are certain guidelines which one needs to follow when buying a basketball. For practicing, one can play with a rubber ball. For professional competitions, one needs to use an inflated ball made of leather.",
                     sport=sport2)

session.add(SportItem1)
session.commit()

SportItem2 = SportItem(user_id=1, name="Shoes", description="One needs specialized shoes when playing basketball. It should be able to give better support to the ankle as compared to running shoes. The basketball shoes should be high-tipped shoes and provide extra comfort during a game. These shoes are specially designed to maintain high traction on the basketball court.",
                     sport=sport2)

session.add(SportItem2)
session.commit()

SportItem3 = SportItem(user_id=1, name="Basketball Shooting Equipment", description="The hoop or basket is a horizontal metallic rim, circular in shape. This rim is attached to a net and helps one score a point. The rim is mounted about 4 feet inside the baseline and 10 feet above the court.",
                     sport=sport2)

session.add(SportItem3)
session.commit()

SportItem4 = SportItem(user_id=1, name="Basketball Court", description="The basketball court is the next important thing for shooting balls in this game. The court is usually made of wooden floorboard. The court size is about 28m x 17m according to the International standards. The National Basketball Association (NBA) regulation states the floor dimension as 29m x 15m. The standard court is rectangular in shape and has baskets placed on opposite ends.",
                     sport=sport2)

session.add(SportItem4)
session.commit()

SportItem5 = SportItem(user_id=1, name="Backboard", description="The backboard is the rectangular board that is placed behind the rim. It helps give better rebound to the ball. The backboard is about 1800mm in size horizontally and 1050mm vertically. Many times, backboards are made of acrylic, aluminum, steel or glass.",
                     sport=sport2)

session.add(SportItem5)
session.commit()


# Kit for Baseball
sport3 = Sport(user_id=1, name="Baseball")

session.add(sport3)
session.commit()


# Kit for Frisbee
sport4 = Sport(user_id=1, name="Frisbee")

session.add(sport4)
session.commit()


# Kit for Snowboarding
sport5 = Sport(user_id=1, name="Snowboarding")

session.add(sport5)
session.commit()


# Kit for Rock Climbing
sport6 = Sport(user_id=1, name="Rock Climbing")

session.add(sport6)
session.commit()


# Kit for Rock Football
sport7 = Sport(user_id=1, name="Football")

session.add(sport7)
session.commit()


# Kit for Skating
sport8 = Sport(user_id=1, name="Skating")

session.add(sport8)
session.commit()


# Kit for Rock Hokey
sport9 = Sport(user_id=1, name="Hockey")

session.add(sport9)
session.commit()


print "added Sport items!"

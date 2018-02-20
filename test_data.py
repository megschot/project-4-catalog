from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, CatalogItem

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Add user
User1 = User(name="Megan Scavello", email="megan.schottanes@gmail.com",
             picture='https://media.licdn.com/mpr/mpr/shrinknp_400_400/p/3/005/071/32c/0ee24fc.jpg')
session.add(User1)
session.commit()
print("User successfully added!")


def add_category(category_name):
    category = Category(user_id=1, name=category_name)
    session.add(category)
    session.commit()
    print("Added " + category_name + " category to your catalog.")

add_category("Elin Hilderbrand")

add_category("Nancy Thayer")

add_category("Dorothea Benton Frank")

add_category("Mary Kay Andrews")

add_category("Jill Shalvis")

add_category("Jenna Bush Hager")


def add_item(item_name, item_description, category_id):
    item = CatalogItem(name=item_name, description=item_description, category_id=category_id)
    session.add(item)
    session.commit()
    print("Added " + item_name + " item to category id: " + str(category_id))

add_item("The Identicals",
         "Identical twin sisters who couldn't look more alike...or live more differently. "
         "Two beautiful islands only eleven miles apart. One unforgettable summer that "
         "will change their lives forever.", 1)

add_item("Here's to Us",
         "An emotional, heartwarming story from New York Times bestselling author Elin "
         "Hilderbrand about a grieving family that finds solace where they least expect it.", 1)

add_item("The Perfect Couple",
         "From New York Times bestselling author Elin Hilderbrand, comes a novel about the"
         " many ways family can fill our lives with love...if they don't kill us first.", 1)

add_item("Secrets in Summer",
         "The queen of beach books (The Star-Ledger) returns to the shores of Nantucket "
         "in a novel about one memorable summer when flirtations flourish, family dramas "
         "play out, and scandalous secrets surface.", 2)

add_item("The Island House",
         "New York Times bestselling author Nancy Thayer evokes the shimmering seascape "
         "of Nantucket in a delightful novel that resonates with the heartache and hope "
         "of growing up, growing wise, and the bittersweet choices we must be brave "
         "enough to make.", 2)

add_item("Same Beach, Next Year",
         "New York Times bestselling author Dorothea Benton Frank returns to her magical "
         "Lowcountry of South Carolina in this bewitching story of marriage, love, "
         "family, and friendship that is infused with her warm and engaging earthy humor "
         "and generous heart.", 3)

add_item("All Summer Long",
         "Filled with her trademark wit, poignant themes, and rich characters, the "
         "perennial New York Times bestselling author returns with a sensational "
         "novel that follows the travels of one couple though a tumultuous summer.", 3)

add_item("The Weekenders",
         "Told with Mary Kay Andrews trademark blend of humor and warmth, and with "
         "characters and a setting that you can't help but fall for, the New York "
         "Times bestseller The Weekenders is the perfect summer escape.", 4)

add_item("Summer Rental",
         "Mary Kay Andrews's New York Times bestseller, Summer Rental, is a warm and "
         "humorous novel of four women, a month at the beach, and the healing power "
         "of friendship and second chances.", 4)

add_item("Lost and Found Sisters",
         "From New York Times bestselling author Jill Shalvis comes her first women's "
         "fiction novel-an unforgettable story of friendship, love, family, and "
         "sisterhood-perfect for fans of Colleen Hoover, Susan Mallery, "
         "and Kristan Higgins", 5)

add_item("Sisters First:Stories from Our Wild and Wonderful Life",
         "From New York Times bestselling author Jill Shalvis comes her first women's "
         "fiction novel-an unforgettable story of friendship, love, family, and "
         "sisterhood-perfect for fans of Colleen Hoover, Susan Mallery, "
         "and Kristan Higgins", 6)


print("Data has been added to the database.")

#import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:////tmp/test.db', echo=True)

Base = declarative_base()

class Menu(Base):
    __tablename__ = 'menus'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    visible = Column(Boolean, default=True)
    
class Page(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    order = Column(Integer)
    visible = Column(Boolean, default=True)

    menuId = Column(Integer, ForeignKey('menus.id'))

    def linkName(self):
        return self.title.lower().replace(' ','-')
        return 'fooage!'

class ImageTag(Base):
    __tablename__ = 'image_tags'

    id = Column(Integer, primary_key=True)
    hash = Column(String)
    tag = Column(String)
    path = Column(String)

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
dbSession = Session()

def initModels():
    Base.metadata.create_all(engine) 
    #try:
    #    Menu.createTable()
    #    Page.createTable()
    #except sqlobject.dberrors.OperationalError:
    #    pass

def getMenusWithPages():
    menusById = {}
    for menu, page in dbSession.query(Menu, Page).outerjoin(Page).order_by(Page.order): #.all():
        if menu.id not in menusById:
            menusById[menu.id] = { 
                'id' : menu.id,
                'title' : menu.title,
                'pages' : []
            }
        if page:
            menusById[menu.id]['pages'].append({
                'id' : page.id,
                'title' : page.title,
                'linkName' : page.linkName()
            })

    return menusById.values()

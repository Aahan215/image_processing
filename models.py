from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Request(Base):
    __tablename__ = 'requests'
    id = Column(String, primary_key=True, index=True)
    status = Column(String, index=True)
    products = relationship("Product", back_populates="request")

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, ForeignKey('requests.id'))
    product_name = Column(String)
    input_urls = Column(String)  # Comma-separated input URLs
    output_urls = Column(String)  # Comma-separated output URLs (initially empty)
    request = relationship("Request", back_populates="products")

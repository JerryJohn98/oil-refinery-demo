from pydantic import BaseModel


class MongoBaseSchema(BaseModel):
    pass


class BaseRequestSchema(BaseModel):
    """
    This is base schema for input requests to the Collection Class
    """

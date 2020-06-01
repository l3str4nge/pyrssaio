from pyrssaio import models


def register_model(model):
    setattr(models, 'Article', model)


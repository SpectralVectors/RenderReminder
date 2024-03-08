class Injectable:
    def inject(self, name, value):
        if hasattr(self, name):
            raise AttributeError("attribute '{}' already exists".format(name))
        setattr(self, name, value)
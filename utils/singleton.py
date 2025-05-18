class Singleton(object):
    def __new__(cls, *args, **kwargs):  # Accept any arguments
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance

class PluginInterface:
    @staticmethod
    def execute(preferences, context):
        raise NotImplementedError()

    @staticmethod
    def draw(parent, layout):
        raise NotImplementedError()

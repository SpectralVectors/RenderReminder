class PluginInterface:
    @staticmethod
    def execute(var: list):
        raise NotImplementedError()
    
    @staticmethod
    def draw(parent, layout):
        raise NotImplementedError()
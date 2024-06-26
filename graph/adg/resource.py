class Resource:
    def __init__(self, name, type, metadata=dict()):
        self.name = name
        self.type = type
        self.metadata = metadata
        self.dependencies = []
        self.trigger = None
        self.trigger_type = None

    def __str__(self) -> str:
        pass

    def __repr__(self) -> str:
        return self.name

    def add_dependency(self, resource):
        self.dependencies.append(resource)
        resource.trigger = self
        resource.trigger_type = self.type
    
    def visualize_dependencies(self):
        if self.dependencies == []:
            print(self.name)
        else:
            print(f"{self.name} -> {', '.join([r.name for r in self.dependencies])}")

        
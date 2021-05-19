class ResourceAlreadyImported(Exception):
    def __init(self, message="Resource Has Already been imported from integration"):
        self.message = message
        super().__init__(self.message)

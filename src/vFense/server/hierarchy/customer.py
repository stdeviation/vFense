from vFense.server.hierarchy import ViewKey


class View():

    def __init__(self, name, properties={}):

        self.view_name = name
        self.properties = properties

    def dict(self):

        return {
            ViewKey.ViewName: self.view_name,
            ViewKey.Properties: self.properties
        }

    def __repr__(self):

        return (
            "View(name=%r)"
            % (self.view_name)
        )

    def __eq__(self, other):

        try:

            return self.view_name == other.view_name

        except:

            return False

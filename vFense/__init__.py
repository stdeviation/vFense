class Base(object):
    """Used to represent an instance."""

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            self.__dict__[key] = val

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values."""
        pass

    def get_invalid_fields(self):
        """Check for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.
        """
        invalid_fields = []

        return invalid_fields

    def to_dict(self):
        """ Turn the fields into a dictionary."""
        return self.__dict__

    def to_dict_all(self):
        """ Turn all the fields into a dictionary."""
        return self.__dict__

    def to_dict_non_null(self):
        """ Use to get non None fields. Useful when
        filling out just a few fields to update the db with .

        Returns:
            (dict): a dictionary with the non None fields of this view.
        """
        data = self.to_dict_all()

        return {k:data[k] for k in data
                if data[k] != None}

    def __str__(self):
        return(repr(self.to_dict_all()))

    def __repr__(self):
        output = ''
        data = self.to_dict_all()
        for key, val in data.items():
            output += '%s=%s,' % (key, val)
        output = output.strip(',')

        return '%s(%r)' % (self.__class__.__name__, output)

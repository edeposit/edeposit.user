from plone.app.users.browser.personalpreferences import UserDataPanelAdapter

class EnhancedUserDataPanelAdapter(UserDataPanelAdapter):
    """
    """
    def get_firstname(self):
        return self.context.getProperty('firstname', '')
    def set_firstname(self, value):
        return self.context.setMemberProperties({'firstname': value})
    firstname = property(get_firstname, set_firstname)

    def get_lastname(self):
        return self.context.getProperty('lastname', '')
    def set_lastname(self, value):
        return self.context.setMemberProperties({'lastname': value})
    lastname = property(get_lastname, set_lastname)

    def get_street(self):
        return self.context.getProperty('street', '')
    def set_street(self, value):
        return self.context.setMemberProperties({'street': value})
    street = property(get_street, set_street)

    def get_city(self):
        return self.context.getProperty('city', '')
    def set_city(self, value):
        return self.context.setMemberProperties({'city': value})
    city = property(get_city, set_city)

    def get_country(self):
        return self.context.getProperty('country', '')
    def set_country(self, value):
        return self.context.setMemberProperties({'country': value})
    country = property(get_country, set_country)

    def get_phone(self):
        return self.context.getProperty('phone', '')
    def set_phone(self, value):
        return self.context.setMemberProperties({'phone': value})
    phone = property(get_phone, set_phone)

    def get_accept(self):
        return self.context.getProperty('accept', '')
    def set_accept(self, value):
        return self.context.setMemberProperties({'accept': value})
    accept = property(get_accept, set_accept)

    def get_agreement(self):
        return self.context.getProperty('agreement', '')
    def set_agreement(self, value):
        return self.context.setMemberProperties({'agreement': value})
    agreement = property(get_agreement, set_agreement)


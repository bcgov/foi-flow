from request_api.models.ProactiveDisclosureCategories import ProactiveDisclosureCategory

class proactivedisclosurecategoryservice:

    def getproactivedisclosurecategories(self):
        """ Returns the active Proactive Disclosure Categories
        """
        return ProactiveDisclosureCategory.getproactivedisclosurecategories()
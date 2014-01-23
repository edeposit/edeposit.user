from plone.testing import z2

from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE

from plone.app.testing import (
    PloneSandboxLayer,
    applyProfile,
    PLONE_FIXTURE,
    FunctionalTesting,
    IntegrationTesting
)

from zope.configuration import xmlconfig

class EDepositUserPolicy(PloneSandboxLayer):
    defaultBases=(PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import edeposit.policy
        xmlconfig.file('configure.zcml',
                       edeposit.policy,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal,'edeposit.policy:default')

EDEPOSIT_USER_FIXTURE = EDepositUserPolicy()

EDEPOSIT_USER_ROBOT_TESTING = FunctionalTesting(
    bases=(EDEPOSIT_USER_FIXTURE,
           AUTOLOGIN_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="E-Deposit User:Robot")

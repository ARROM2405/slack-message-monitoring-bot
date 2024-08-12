import factory

from slack_integration.models import DataSecurityPattern, DataLossMessage


class DataSecurityPatternFactory(factory.django.DjangoModelFactory):
    name = factory.sequence(lambda n: "pattern_name_%s" % n)
    pattern = factory.sequence(lambda n: "pattern_%s" % n)

    class Meta:
        model = DataSecurityPattern


class DataLossMessageFactory(factory.django.DjangoModelFactory):
    user_id = factory.sequence(lambda n: "user_id_%s" % n)
    text = factory.sequence(lambda n: "text_%s" % n)
    ts = factory.sequence(lambda n: "ts_%s" % n)
    channel = factory.sequence(lambda n: "channel_%s" % n)

    class Meta:
        model = DataLossMessage

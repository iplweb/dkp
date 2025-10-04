from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from .models import Role, OperatingRoom, Ward

@register(Role)
class RoleTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(OperatingRoom)
class OperatingRoomTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Ward)
class WardTranslationOptions(TranslationOptions):
    fields = ('name',)
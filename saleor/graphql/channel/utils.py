from django.core.exceptions import ValidationError
from django.utils.functional import SimpleLazyObject
from graphql.error import GraphQLError

from ...channel.exceptions import ChannelNotDefined, NoDefaultChannel
from ...channel.models import Channel
from ...channel.utils import get_default_channel


def get_default_channel_slug_or_graphql_error() -> SimpleLazyObject:
    """Return a default channel slug in lazy way or a GraphQL error.

    Utility to get the default channel in GraphQL query resolvers.
    """
    return SimpleLazyObject(lambda: get_default_channel_or_graphql_error().slug)


def get_default_channel_or_graphql_error() -> Channel:
    """Return a default channel or a GraphQL error.

    Utility to get the default channel in GraphQL query resolvers.
    """
    try:
        channel = get_default_channel()
    except (ChannelNotDefined, NoDefaultChannel) as e:
        raise GraphQLError(str(e))
    else:
        return channel


def validate_channel(
    channel_slug, error_for_channel_doesnt_exist, error_for_channel_inactive
):
    try:
        channel = Channel.objects.get(slug=channel_slug)
    except Channel.DoesNotExist:
        raise ValidationError(
            {
                "channel": ValidationError(
                    f"Channel with '{channel_slug}' slug does not exist.",
                    code=error_for_channel_doesnt_exist,
                )
            }
        )
    if not channel.is_active:
        raise ValidationError(
            {
                "channel": ValidationError(
                    f"Channel with '{channel_slug}' is inactive.",
                    code=error_for_channel_inactive,
                )
            }
        )
    return channel


def clean_channel(
    channel_slug,
    error_for_channel_doesnt_exist,
    error_for_channel_inactive,
    error_channel_not_defined,
):
    if channel_slug is not None:
        channel = validate_channel(
            channel_slug, error_for_channel_doesnt_exist, error_for_channel_inactive
        )
    else:
        try:
            channel = get_default_channel()
        except ChannelNotDefined:
            raise ValidationError(
                {
                    "channel": ValidationError(
                        "You need to provide channel slug.",
                        code=error_channel_not_defined,
                    )
                }
            )
    return channel

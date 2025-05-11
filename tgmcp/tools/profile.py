"""
Profile and account management tool functions for Telegram MCP.

Functions for managing user profile, privacy settings, etc.
"""

import json
from telethon.tl.functions.photos import GetUserPhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon import functions
from telethon.tl.types import User, Chat, Channel
from ..client import client, mcp, logger
from ..utils import log_and_format_error, format_entity

__all__ = [
    'get_me',
    'update_profile',
    'set_profile_photo',
    'delete_profile_photo',
    'get_privacy_settings',
    'set_privacy_settings',
    'get_user_photos',
    'get_user_status',
    'get_bot_info',
    'set_bot_commands'
]

@mcp.tool()
async def get_me() -> str:
    """
    Get your own user information.
    """
    try:
        me = await client.get_me()
        return json.dumps(format_entity(me), indent=2)
    except Exception as e:
        return log_and_format_error("get_me", e)


@mcp.tool()
async def update_profile(first_name: str = None, last_name: str = None, about: str = None) -> str:
    """
    Update your profile information (name, bio).
    """
    try:
        await client(
            functions.account.UpdateProfileRequest(
                first_name=first_name, last_name=last_name, about=about
            )
        )
        return "Profile updated."
    except Exception as e:
        return log_and_format_error(
            "update_profile", e, first_name=first_name, last_name=last_name, about=about
        )


@mcp.tool()
async def set_profile_photo(file_path: str) -> str:
    """
    Set a new profile photo.
    """
    try:
        await client(
            UploadProfilePhotoRequest(file=await client.upload_file(file_path))
        )
        return "Profile photo updated."
    except Exception as e:
        return log_and_format_error("set_profile_photo", e, file_path=file_path)


@mcp.tool()
async def delete_profile_photo() -> str:
    """
    Delete your current profile photo.
    """
    try:
        photos = await client(
            GetUserPhotosRequest(user_id="me", offset=0, max_id=0, limit=1)
        )
        if not photos.photos:
            return "No profile photo to delete."
        await client(functions.photos.DeletePhotosRequest(id=[photos.photos[0].id]))
        return "Profile photo deleted."
    except Exception as e:
        return log_and_format_error("delete_profile_photo", e)


@mcp.tool()
async def get_privacy_settings() -> str:
    """
    Get your privacy settings for last seen status.
    """
    try:
        # Import needed types directly
        from telethon.tl.types import InputPrivacyKeyStatusTimestamp

        try:
            settings = await client(
                functions.account.GetPrivacyRequest(key=InputPrivacyKeyStatusTimestamp())
            )
            return str(settings)
        except TypeError as e:
            if "TLObject was expected" in str(e):
                return "Error: Privacy settings API call failed due to type mismatch. This is likely a version compatibility issue with Telethon."
            else:
                raise
    except Exception as e:
        logger.exception("get_privacy_settings failed")
        return log_and_format_error("get_privacy_settings", e)


@mcp.tool()
async def set_privacy_settings(
    key: str, allow_users: list = None, disallow_users: list = None
) -> str:
    """
    Set privacy settings (e.g., last seen, phone, etc.).

    Args:
        key: The privacy setting to modify ('status' for last seen, 'phone', 'profile_photo', etc.)
        allow_users: List of user IDs to allow
        disallow_users: List of user IDs to disallow
    """
    try:
        # Import needed types
        from telethon.tl.types import (
            InputPrivacyKeyStatusTimestamp,
            InputPrivacyKeyPhoneNumber,
            InputPrivacyKeyProfilePhoto,
            InputPrivacyValueAllowUsers,
            InputPrivacyValueDisallowUsers,
            InputPrivacyValueAllowAll,
            InputPrivacyValueDisallowAll,
        )

        # Map the simplified keys to their corresponding input types
        key_mapping = {
            "status": InputPrivacyKeyStatusTimestamp,
            "phone": InputPrivacyKeyPhoneNumber,
            "profile_photo": InputPrivacyKeyProfilePhoto,
        }

        # Get the appropriate key class
        if key not in key_mapping:
            return f"Error: Unsupported privacy key '{key}'. Supported keys: {', '.join(key_mapping.keys())}"

        privacy_key = key_mapping[key]()

        # Prepare the rules
        rules = []

        # Process allow rules
        if allow_users is None or len(allow_users) == 0:
            # If no specific users to allow, allow everyone by default
            rules.append(InputPrivacyValueAllowAll())
        else:
            # Convert user IDs to InputUser entities
            try:
                allow_entities = []
                for user_id in allow_users:
                    try:
                        user = await client.get_entity(user_id)
                        allow_entities.append(user)
                    except Exception as user_err:
                        logger.warning(f"Could not get entity for user ID {user_id}: {user_err}")

                if allow_entities:
                    rules.append(InputPrivacyValueAllowUsers(users=allow_entities))
            except Exception as allow_err:
                logger.error(f"Error processing allowed users: {allow_err}")
                return log_and_format_error("set_privacy_settings", allow_err, key=key)

        # Process disallow rules
        if disallow_users and len(disallow_users) > 0:
            try:
                disallow_entities = []
                for user_id in disallow_users:
                    try:
                        user = await client.get_entity(user_id)
                        disallow_entities.append(user)
                    except Exception as user_err:
                        logger.warning(f"Could not get entity for user ID {user_id}: {user_err}")

                if disallow_entities:
                    rules.append(InputPrivacyValueDisallowUsers(users=disallow_entities))
            except Exception as disallow_err:
                logger.error(f"Error processing disallowed users: {disallow_err}")
                return log_and_format_error("set_privacy_settings", disallow_err, key=key)

        # Apply the privacy settings
        try:
            result = await client(
                functions.account.SetPrivacyRequest(key=privacy_key, rules=rules)
            )
            return f"Privacy settings for {key} updated successfully."
        except TypeError as type_err:
            if "TLObject was expected" in str(type_err):
                return "Error: Privacy settings API call failed due to type mismatch. This is likely a version compatibility issue with Telethon."
            else:
                raise
    except Exception as e:
        logger.exception(f"set_privacy_settings failed (key={key})")
        return log_and_format_error("set_privacy_settings", e, key=key)


@mcp.tool()
async def get_user_photos(user_id: int, limit: int = 10) -> str:
    """
    Get profile photos of a user.
    """
    try:
        user = await client.get_entity(user_id)
        photos = await client(
            GetUserPhotosRequest(user_id=user, offset=0, max_id=0, limit=limit)
        )
        return json.dumps([p.id for p in photos.photos], indent=2)
    except Exception as e:
        return log_and_format_error("get_user_photos", e, user_id=user_id, limit=limit)


@mcp.tool()
async def get_user_status(user_id: int) -> str:
    """
    Get the online status of a user.
    """
    try:
        user = await client.get_entity(user_id)
        return str(user.status)
    except Exception as e:
        return log_and_format_error("get_user_status", e, user_id=user_id)


@mcp.tool()
async def get_bot_info(bot_username: str) -> str:
    """
    Get information about a bot by username.
    """
    try:
        from ..utils import json_serializer
        
        entity = await client.get_entity(bot_username)
        if not entity:
            return f"Bot with username {bot_username} not found."

        result = await client(GetFullUserRequest(id=entity))

        # Create a more structured, serializable response
        if hasattr(result, "to_dict"):
            # Use custom serializer to handle non-serializable types
            return json.dumps(result.to_dict(), indent=2, default=json_serializer)
        else:
            # Fallback if to_dict is not available
            info = {
                "bot_info": {
                    "id": entity.id,
                    "username": entity.username,
                    "first_name": entity.first_name,
                    "last_name": getattr(entity, "last_name", ""),
                    "is_bot": getattr(entity, "bot", False),
                    "verified": getattr(entity, "verified", False),
                }
            }
            if hasattr(result, "full_user") and hasattr(result.full_user, "about"):
                info["bot_info"]["about"] = result.full_user.about

            return json.dumps(info, indent=2)
    except Exception as e:
        logger.exception(f"get_bot_info failed (bot_username={bot_username})")
        return log_and_format_error("get_bot_info", e, bot_username=bot_username)


@mcp.tool()
async def set_bot_commands(bot_username: str, commands: list) -> str:
    """
    Set bot commands for a bot you own.
    Note: This function can only be used if the Telegram client is a bot account.
    Regular user accounts cannot set bot commands.

    Args:
        bot_username: The username of the bot to set commands for.
        commands: List of command dictionaries with 'command' and 'description' keys.
    """
    try:
        # First check if the current client is a bot
        me = await client.get_me()
        if not getattr(me, "bot", False):
            return "Error: This function can only be used by bot accounts. Your current Telegram account is a regular user account, not a bot."

        # Import required types
        from telethon.tl.types import BotCommand, BotCommandScopeDefault
        from telethon.tl.functions.bots import SetBotCommandsRequest

        # Create BotCommand objects from the command dictionaries
        bot_commands = [
            BotCommand(command=c["command"], description=c["description"]) for c in commands
        ]

        # Get the bot entity
        bot = await client.get_entity(bot_username)

        # Set the commands with proper scope
        await client(
            SetBotCommandsRequest(
                scope=BotCommandScopeDefault(),
                lang_code="en",  # Default language code
                commands=bot_commands,
            )
        )

        return f"Bot commands set for {bot_username}."
    except ImportError as ie:
        logger.exception(f"set_bot_commands failed - ImportError: {ie}")
        return log_and_format_error("set_bot_commands", ie)
    except Exception as e:
        logger.exception(f"set_bot_commands failed (bot_username={bot_username})")
        return log_and_format_error("set_bot_commands", e, bot_username=bot_username)

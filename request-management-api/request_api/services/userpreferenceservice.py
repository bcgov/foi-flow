from request_api.models.FOIUserPreferences import FOIUserPreference


CURRENT_SCHEMA_VERSION = 1


class userpreferenceservice:
    """Manage server-backed preferences for the current FOI MOD user."""

    @staticmethod
    def _empty_document():
        return {
            "schemaVersion": CURRENT_SCHEMA_VERSION,
            "preferences": {}
        }

    @staticmethod
    def _validate_payload(payload):
        if not isinstance(payload, dict):
            raise ValueError("Preference payload must be a JSON object")

        schema_version = payload.get(
            "schemaVersion",
            CURRENT_SCHEMA_VERSION
        )

        if (
            not isinstance(schema_version, int)
            or isinstance(schema_version, bool)
        ):
            raise ValueError("schemaVersion must be an integer")

        if schema_version != CURRENT_SCHEMA_VERSION:
            raise ValueError(
                "Unsupported preference schemaVersion: "
                + str(schema_version)
            )

        preferences = payload.get("preferences", {})

        if not isinstance(preferences, dict):
            raise ValueError("preferences must be a JSON object")

        return schema_version, preferences

    def getpreferences(self, userid):
        if not userid:
            raise ValueError("Authenticated user id is required")

        preference = FOIUserPreference.getbyuserid(userid)

        if preference is None:
            return self._empty_document()

        return preference.asdict()

    def savepreferences(self, userid, payload):
        if not userid:
            raise ValueError("Authenticated user id is required")

        schema_version, preferences = self._validate_payload(payload)

        preference = FOIUserPreference.upsert(
            userid,
            preferences,
            schema_version
        )

        return preference.asdict()

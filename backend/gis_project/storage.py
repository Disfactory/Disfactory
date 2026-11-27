from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class FallbackManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """Serve static files under content-hashed names (`base.6b517d0d5813.css`).

    A new file content gives a new URL, so browsers can't keep using stale admin
    CSS after a Django upgrade (#716).

    Files missing from the manifest fall back to their plain name instead of raising.
    This covers `docx/export-word-docx.js`, which is copied into STATIC_ROOT by hand
    rather than collected, and lets pages render when `collectstatic` hasn't run (tests).
    """

    manifest_strict = True  # make the parent raise, so we can fall back below

    def stored_name(self, name):
        try:
            return super().stored_name(name)
        except ValueError:
            return name

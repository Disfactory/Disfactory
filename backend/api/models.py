from django.db import models

# TODO: Design and implement these models

class Factory:
    """Factories that are potential to be illegal.

    This table should store information of a factory,
    containing:
    - name
    - type: Enum, ref: https://g0v.hackmd.io/1w_44QhqTWKi2dcyzCitkA#%E5%B7%A5%E5%BB%A0%E5%88%86%E9%A1%9E
    - position(lat, long),
    - land index
    - status
    - reported_at (aka created_at)
    - etc...

    """
    # TODO: write a migration for data initialization, ref: https://docs.djangoproject.com/en/2.2/howto/initial-data/
    pass


class ReportRecord:
    """Report records send by users.

    This table should contain the report record after calling these API:
    - PUT /factories/{id}/{attribute}
    - POST /factories
    Necessary fields:
    - foreign key to Factory
    - foreign key to User (point to a null user at first)
    - created_at
    - etc...

    `ReportRecord` will be queried in advanced by admins from
    Citizen of the Earth, Taiwan. They will filter the most recent
    records out every a few weeks to catch the bad guys.
    """
    pass


class Image:
    """Images of factories that are uploaded by user

    We store the actual image files on Imgur, so this table
    should contains:
    - hashed uuid (would be returned to user after calling POST /images)
    - foreign key to `Factory`
    - imgur path

    Some optional fields:
    - foreign key to user:
    - foreign key to report record
    """
    pass

from app.repositories import ProfileRepository
from app.schemas import Profile, ProfileUpdate


class ProfileService:
    def __init__(self, profile: ProfileRepository) -> None:
        self.profile = profile

    def get(self) -> Profile | None:
        return self.profile.get()

    def update(self, changes: ProfileUpdate) -> Profile:
        """Merge the provided fields into the stored profile."""
        profile = self.profile.get() or Profile()
        data = changes.model_dump(exclude_none=True)
        if "skills" in data:
            # case-insensitive dedupe, keeping the first spelling given
            unique = {s.strip().lower(): s.strip() for s in reversed(data["skills"]) if s.strip()}
            data["skills"] = sorted(unique.values(), key=str.lower)
        profile = Profile.model_validate({**profile.model_dump(), **data})
        self.profile.save(profile)
        return profile

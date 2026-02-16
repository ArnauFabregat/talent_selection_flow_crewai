from enum import StrEnum


class EducationLevel(StrEnum):
    HIGHSCHOOL = "highschool"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    OTHER = "other"
    UNKNOWN = "unknown"

class ExperienceLevel(StrEnum):
    INTERN = "intern"
    ENTRY = "entry"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    OTHER = "other"
    UNKNOWN = "unknown"

class EmploymentType(StrEnum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    OTHER = "other"
    UNKNOWN = "unknown"

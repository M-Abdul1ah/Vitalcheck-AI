from src.site_content import SUPERVISOR, TEAM, initials


def test_team_has_four_members_with_unique_slugs():
    assert len(TEAM) == 4
    assert len({m["slug"] for m in TEAM}) == 4


def test_every_member_has_text_in_both_languages():
    for m in TEAM:
        for key in ("name", "role_en", "role_ur", "bio_en", "bio_ur"):
            assert m[key].strip(), (m["slug"], key)


def test_supervisor_name():
    assert SUPERVISOR["name"] == "Mam Saba Ramzan"


def test_initials():
    assert initials("Muhammad Abdullah Nawaz") == "MN"
    assert initials("M. Yousaf") == "MY"
    assert initials("Izhan") == "IZ"

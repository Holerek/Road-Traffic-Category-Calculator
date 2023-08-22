import project
import pytest


def test_set_f1():
    assert project.set_f1("1", "1") == 1.00
    assert project.set_f1("2", "1") == 0.90
    assert project.set_f1("3", "1") == 0.70
    assert project.set_f1("4", "1") == 0.70
    assert project.set_f1("5", "1") == 0.70
    assert project.set_f1("6+", "1") == 0.70
    assert project.set_f1("1", "2") == 1.00
    assert project.set_f1("2", "2") == 0.50
    assert project.set_f1("3", "2") == 0.50
    assert project.set_f1("4", "2") == 0.45
    assert project.set_f1("5", "2") == 0.45
    assert project.set_f1("6+", "2") == 0.35


def test_set_f2():
    assert project.set_f2(4.0) == 1.00
    assert project.set_f2(3.5) == 1.00
    assert project.set_f2(3.2) == 1.06
    assert project.set_f2(3.0) == 1.06
    assert project.set_f2(2.2123) == 1.25
    assert project.set_f2(2.83) == 1.13
    assert project.set_f2(2.75) == 1.13
    assert project.set_f2(2.74) == 1.25


def test_set_f3():
    assert project.set_f3(12) == 1.45
    assert project.set_f3(12.12) == 1.45
    assert project.set_f3(10) == 1.45
    assert project.set_f3(9.57) ==1.35
    assert project.set_f3(9.0) ==1.35
    assert project.set_f3(8.58) ==1.25
    assert project.set_f3(7) ==1.25
    assert project.set_f3(6.88) == 1.10
    assert project.set_f3(6) == 1.10
    assert project.set_f3(5.95) == 1


def test_get_years_valid():
    assert project.get_years("2020-2030") == {"start": "2020", "end": "2030"}
    assert project.get_years("2022-2052") == {"start": "2022", "end": "2052"}


def test_get_years_invalid():
    with pytest.raises(ValueError):
        assert project.get_years("2008-2030")

    with pytest.raises(ValueError):
        assert project.get_years("2020-2002")

    with pytest.raises(ValueError):
        assert project.get_years("2030-2025")

    with pytest.raises(ValueError):
        assert project.get_years("2030-2025b")

    with pytest.raises(ValueError):
        assert project.get_years("a2030-2025")

    with pytest.raises(ValueError):
        assert project.get_years("2030 2025")


def test_region_valid():
    project.initiate_GDPindexes()
    assert project.region("1") == 1
    assert project.region("60") == 60


def test_region_invalid():
    with pytest.raises(ValueError):
        assert project.region("0")

    with pytest.raises(ValueError):
        assert project.region("500")


def test_set_road():
    assert project.set_road("1") == "highway"
    assert project.set_road("2") == "state road"
    assert project.set_road("3") == "regional road"

    with pytest.raises(ValueError):
        assert project.set_road("")
    with pytest.raises(ValueError):
        assert project.set_road("a")
    with pytest.raises(ValueError):
        assert project.set_road("4")


def test_set_axle():
    assert project.set_axle("highway") == "115kN"
    assert project.set_axle("state road") == "115kN"
    assert project.set_axle("regional road", "1") == "115kN"
    assert project.set_axle("regional road", "2") == "100kN"

    with pytest.raises(ValueError):
        assert project.set_axle("regional road", "a")
    with pytest.raises(ValueError):
        assert project.set_axle("a")


def test_set_r():
    assert project.set_r("highway", "115kN") == (0.50, 1.95, 1.25)
    assert project.set_r("state road", "115kN") == (0.50, 1.80, 1.20)
    assert project.set_r("regional road", "115kN") == (0.45, 1.70, 1.15)
    assert project.set_r("regional road", "100kN") == (0.45, 1.60, 1.05)

    with pytest.raises(KeyError):
        assert project.set_r("highway", "100kN")
    with pytest.raises(KeyError):
        assert project.set_r("state road", "100kN")


def test_cumulate_ri():
    project.initiate_GDPindexes()
    assert project.accumulated_ri({"start": "2020", "end": "2020"}, 1) == {
        "trucks": pytest.approx([1.01155], rel=1e-4),
        "trucks_trailers": pytest.approx([1.0330], rel=1e-4),
        "buses": pytest.approx([1.0330], rel=1e-4),
        }
    assert project.accumulated_ri({"start": "2020", "end": "2021"}, 1) == {
        "trucks": pytest.approx([1.01155, 1.02323340], rel=1e-4),
        "trucks_trailers": pytest.approx([1.033, 1.067089], rel=1e-4),
        "buses": pytest.approx([1.033, 1.067089], rel=1e-4),
        }
    assert project.accumulated_ri({"start": "2033", "end": "2034"}, 5) == {
        "trucks": pytest.approx([1.0084, 1.01616468], rel=1e-4),
        "trucks_trailers": pytest.approx([1.024, 1.046528], rel=1e-4),
        "buses": pytest.approx([1.024, 1.046528], rel=1e-4),
        }

def test_total():
    assert project.total(10, [2, 3]) == 18250
    assert project.total(10, [1.1, 1.2]) == 8395
    assert project.total(10, [1.0084, 1.0162]) == pytest.approx(7389.79, rel=1e-1)


def test_category():
    assert project.category(0.04) == "KR1"
    assert project.category(0.09) == "KR1"
    assert project.category(0.2) == "KR2"
    assert project.category(0.5) == "KR2"
    assert project.category(1) == "KR3"
    assert project.category(2.5) == "KR3"
    assert project.category(4) == "KR4"
    assert project.category(7.3) == "KR4"
    assert project.category(8) == "KR5"
    assert project.category(22) == "KR5"
    assert project.category(36) == "KR6"
    assert project.category(52.0) == "KR6"
    assert project.category(52.1) == "KR7"
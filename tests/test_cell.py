"""Integration tests for Cell System — UDX addressing, storage, Cubes."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core_py.cell import (
    Cell,
    CellAddress,
    CellStore,
    Cube,
    layer_name,
    CELL_DIR,
    LAYER_GRID,
    LAYER_SPATIAL,
    LAYER_SNACK,
    LAYER_FEED,
    LAYER_META,
    LAYER_CHAR,
    LAYER_BINDER,
    LAYER_USXD,
    LAYER_CUBE,
    LAYER_USER,
)


class TestCellAddress:
    """UDX address parsing and formatting tests."""

    def test_parse_simple(self):
        addr = CellAddress.parse("L100-AA00-0000-0")
        assert addr is not None
        assert addr.band == 100
        assert addr.col == 0
        assert addr.row == 0
        assert addr.sub == 0
        assert addr.layer == 0
        assert addr.slot == 0
        assert addr.version == 0
        assert addr.x == 0
        assert addr.y == 0

    def test_parse_full(self):
        addr = CellAddress.parse("L500-ZZ99-4927-5")
        assert addr is not None
        assert addr.band == 500
        assert addr.col == 25  # Z = 25
        assert addr.row == 25  # Z = 25
        assert addr.sub == 99
        assert addr.layer == 4
        assert addr.slot == 927
        assert addr.version == 5

    def test_parse_invalid_format(self):
        assert CellAddress.parse("invalid") is None
        assert CellAddress.parse("L100") is None
        assert CellAddress.parse("L100-AA-0000-0") is None
        assert CellAddress.parse("") is None

    def test_parse_case_insensitive(self):
        addr = CellAddress.parse("l100-aa00-0000-0")
        assert addr is not None
        assert addr.band == 100

    def test_roundtrip_string(self):
        addr1 = CellAddress.parse("L200-BB01-1001-0")
        s = str(addr1)
        addr2 = CellAddress.parse(s)
        assert addr1 == addr2

    def test_equality(self):
        a1 = CellAddress.parse("L100-AA00-0000-0")
        a2 = CellAddress.parse("L100-AA00-0000-0")
        a3 = CellAddress.parse("L100-BB00-0000-0")
        assert a1 == a2
        assert a1 != a3

    def test_band_edges(self):
        addr = CellAddress.parse("L100-AA00-0000-0")
        assert addr.band == 100
        addr2 = CellAddress.parse("L899-AA00-0000-0")
        assert addr2.band == 899


class TestCell:
    """Cell data model tests."""

    def test_create_cell(self):
        addr = CellAddress.parse("L100-AA00-0000-0")
        cell = Cell(address=addr, data={"name": "test"})
        assert cell.address == addr
        assert cell.data["name"] == "test"
        assert cell.checksum != ""
        assert cell.created != ""

    def test_verify_integrity(self):
        addr = CellAddress.parse("L100-AA00-0000-0")
        cell = Cell(address=addr, data={"x": 1})
        assert cell.verify() is True

    def test_integrity_failure(self):
        addr = CellAddress.parse("L100-AA00-0000-0")
        cell = Cell(address=addr, data={"x": 1})
        cell.checksum = "tampered"
        assert cell.verify() is False

    def test_to_dict_roundtrip(self):
        addr = CellAddress.parse("L300-CC05-2323-2")
        cell = Cell(address=addr, data={"key": "value", "num": 42})
        d = cell.to_dict()
        cell2 = Cell.from_dict(d)
        assert cell.address == cell2.address
        assert cell.data == cell2.data
        assert cell.checksum == cell2.checksum

    def test_from_dict_invalid_address(self):
        import pytest
        try:
            Cell.from_dict({"address": "invalid"})
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


class TestCellStore:
    """Filesystem cell storage tests."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp(prefix="udox_cell_test_")
        self.store = CellStore(root_dir=self.tmpdir)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_write_and_read(self):
        addr = CellAddress.parse("L100-AA00-0000-0")
        cell = Cell(address=addr, data={"hello": "world"})
        self.store.write(cell)
        read = self.store.read("L100-AA00-0000-0")
        assert read is not None
        assert read.data == {"hello": "world"}
        assert read.checksum == cell.checksum

    def test_read_nonexistent(self):
        read = self.store.read("L999-AA00-0000-0")
        assert read is None

    def test_delete_existing(self):
        addr = CellAddress.parse("L100-AA00-0000-0")
        cell = Cell(address=addr, data={"x": 1})
        self.store.write(cell)
        assert self.store.delete("L100-AA00-0000-0") is True
        assert self.store.read("L100-AA00-0000-0") is None

    def test_delete_nonexistent(self):
        assert self.store.delete("L999-AA00-0000-0") is False

    def test_list_empty(self):
        assert len(self.store.list_cells()) == 0

    def test_list_after_writes(self):
        for i in range(3):
            addr = CellAddress.parse(f"L100-AA0{i}-0000-0")
            self.store.write(Cell(address=addr, data={"i": i}))
        cells = self.store.list_cells()
        assert len(cells) == 3

    def test_list_filter_by_band(self):
        for b in [100, 200]:
            addr = CellAddress.parse(f"L{b}-AA00-0000-0")
            self.store.write(Cell(address=addr, data={}))
        assert len(self.store.list_cells(band=100)) == 1
        assert len(self.store.list_cells(band=200)) == 1
        assert len(self.store.list_cells()) == 2

    def test_count(self):
        self.store.write(Cell(address=CellAddress.parse("L100-AA00-0000-0"), data={}))
        self.store.write(Cell(address=CellAddress.parse("L100-BB00-0000-0"), data={}))
        assert self.store.count() == 2
        assert self.store.count(band=100) == 2
        assert self.store.count(band=200) == 0

    def test_purge_band(self):
        for b in [100, 200]:
            addr = CellAddress.parse(f"L{b}-AA00-0000-0")
            self.store.write(Cell(address=addr, data={}))
        assert self.store.purge_band(100) == 1
        assert self.store.count() == 1

    def test_integrity_after_write_read(self):
        addr = CellAddress.parse("L100-AA00-0000-0")
        cell = Cell(address=addr, data={"secret": 42})
        self.store.write(cell)
        read = self.store.read("L100-AA00-0000-0")
        assert read.verify() is True

    def test_write_overwrites(self):
        addr = CellAddress.parse("L100-AA00-1111-0")
        c1 = Cell(address=addr, data={"v": 1})
        self.store.write(c1)
        c2 = Cell(address=addr, data={"v": 2})
        self.store.write(c2)
        read = self.store.read("L100-AA00-1111-0")
        assert read.data == {"v": 2}


class TestCube:
    """Cube (SnackBox packaging) tests."""

    def test_create_empty_cube(self):
        cube = Cube(id="test-cube")
        assert cube.id == "test-cube"
        assert cube.size() == 0

    def test_add_cell(self):
        cube = Cube(id="test")
        addr = CellAddress.parse("L100-AA00-0000-0")
        cell = Cell(address=addr, data={"x": 1})
        cube.add(cell)
        assert cube.size() == 1

    def test_get_cell(self):
        cube = Cube(id="test")
        addr = CellAddress.parse("L100-AA00-0000-0")
        cube.add(Cell(address=addr, data={"k": "v"}))
        cell = cube.get("L100-AA00-0000-0")
        assert cell is not None
        assert cell.data == {"k": "v"}

    def test_get_nonexistent(self):
        cube = Cube(id="test")
        assert cube.get("L999-AA00-0000-0") is None

    def test_remove_cell(self):
        cube = Cube(id="test")
        cube.add(Cell(address=CellAddress.parse("L100-AA00-0000-0"), data={}))
        cube.remove("L100-AA00-0000-0")
        assert cube.size() == 0

    def test_to_dict_roundtrip(self):
        cube = Cube(id="roundtrip")
        cube.add(Cell(address=CellAddress.parse("L100-AA00-0000-0"), data={"a": 1}))
        cube.add(Cell(address=CellAddress.parse("L200-BB01-1002-3"), data={"b": 2}))
        d = cube.to_dict()
        cube2 = Cube.from_dict(d)
        assert cube2.id == "roundtrip"
        assert cube2.size() == 2
        assert cube2.get("L100-AA00-0000-0") is not None
        assert cube2.get("L200-BB01-1002-3") is not None

    def test_metadata(self):
        cube = Cube(id="meta-test", metadata={"author": "test", "date": "2026"})
        assert cube.metadata["author"] == "test"

    def test_created_auto(self):
        cube = Cube(id="auto-ts")
        assert cube.created != ""


class TestLayerNames:
    """Layer name mapping tests."""

    def test_all_layer_names(self):
        assert layer_name(0) == "grid"
        assert layer_name(1) == "spatial"
        assert layer_name(2) == "snack"
        assert layer_name(3) == "feed"
        assert layer_name(4) == "meta"
        assert layer_name(5) == "char"
        assert layer_name(6) == "binder"
        assert layer_name(7) == "usxd"
        assert layer_name(8) == "cube"
        assert layer_name(9) == "user"

    def test_unknown_layer(self):
        assert layer_name(99) == "unknown"
        assert layer_name(-1) == "unknown"

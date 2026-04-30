#!/usr/bin/env python3
"""
uCode1 Cell CLI — Atomic storage units with UDX addressing.

Usage:
  ucode cell write <address> [--key <key> --value <value> | --data <json>]
  ucode cell read <address>
  ucode cell delete <address>
  ucode cell list [--band <band>]
  ucode cell count [--band <band>]
  ucode cell purge <band>
  ucode cell cube create <id> [--cell <address>]
  ucode cell cube add <cube-file> <address>
  ucode cell cube remove <cube-file> <address>
  ucode cell cube show <cube-file>
  ucode cell help
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core_py.cell import (
        CELL_DIR,
        LAYER_BINDER,
        LAYER_CHAR,
        LAYER_CUBE,
        LAYER_FEED,
        LAYER_GRID,
        LAYER_META,
        LAYER_SNACK,
        LAYER_SPATIAL,
        LAYER_USER,
        LAYER_USXD,
        Cell,
        CellAddress,
        CellStore,
        Cube,
        layer_name,
    )
    CORE_AVAILABLE = True
except ImportError as e:
    CORE_AVAILABLE = False
    _import_error = str(e)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ucode cell", description="Cell storage operations")
    sub = p.add_subparsers(dest="command")

    # write
    wp = sub.add_parser("write", help="Write data to a cell")
    wp.add_argument("address", help="UDX address (e.g. L100-AA00-0000-0)")
    wp.add_argument("--key", help="Data key")
    wp.add_argument("--value", help="Data value")
    wp.add_argument("--data", help="JSON data string")

    # read
    rp = sub.add_parser("read", help="Read a cell")
    rp.add_argument("address", help="UDX address")

    # delete
    dp = sub.add_parser("delete", help="Delete a cell")
    dp.add_argument("address", help="UDX address")

    # list
    lp = sub.add_parser("list", help="List cells")
    lp.add_argument("--band", type=int, help="Filter by layer band (100-899)")

    # count
    cp = sub.add_parser("count", help="Count cells")
    cp.add_argument("--band", type=int, help="Filter by layer band")

    # purge
    pp = sub.add_parser("purge", help="Delete all cells in a band")
    pp.add_argument("band", type=int, help="Layer band to purge")

    # cube
    cube_p = sub.add_parser("cube", help="Cube (SnackBox) operations")
    cube_sub = cube_p.add_subparsers(dest="cube_cmd")

    c_create = cube_sub.add_parser("create", help="Create a new Cube")
    c_create.add_argument("id", help="Cube ID")
    c_create.add_argument("--cell", action="append", help="Cell address to include")

    c_add = cube_sub.add_parser("add", help="Add a cell to a Cube")
    c_add.add_argument("cube_file", help="Cube JSON file path")
    c_add.add_argument("address", help="Cell address")

    c_rm = cube_sub.add_parser("remove", help="Remove a cell from a Cube")
    c_rm.add_argument("cube_file", help="Cube JSON file path")
    c_rm.add_argument("address", help="Cell address")

    c_show = cube_sub.add_parser("show", help="Show Cube contents")
    c_show.add_argument("cube_file", help="Cube JSON file path")

    return p


def main():
    p = build_arg_parser()
    args = p.parse_args()

    if not CORE_AVAILABLE:
        print(f"Error: core_py.cell not available: {_import_error}")
        sys.exit(1)

    store = CellStore()

    if args.command == "write":
        addr = CellAddress.parse(args.address)
        if not addr:
            print(f"❌ Invalid address: {args.address}")
            print("   Expected format: L<band>-<x><y>-<layer><slot>-<version>")
            print("   Example: L100-AA00-0000-0")
            sys.exit(1)

        data = {}
        if args.data:
            try:
                data = json.loads(args.data)
            except json.JSONDecodeError:
                data = {"value": args.data}
        elif args.key:
            data = {args.key: args.value or ""}
        else:
            # Default: store address info
            data = {
                "band": addr.band,
                "layer": addr.layer,
                "layer_name": layer_name(addr.layer),
                "slot": addr.slot,
                "x": addr.x,
                "y": addr.y,
            }

        cell = Cell(address=addr, data=data)
        store.write(cell)
        print(f"✅ Written cell: {addr}")
        print(f"   Layer: {layer_name(addr.layer)} ({addr.layer})")
        print(f"   Size: {len(json.dumps(data))} bytes")

    elif args.command == "read":
        cell = store.read(args.address)
        if not cell:
            print(f"❌ Cell not found: {args.address}")
            sys.exit(1)
        if not cell.verify():
            print(f"⚠️  Cell integrity check FAILED: {args.address}")

        print(f"Cell:      {cell.address}")
        print(f"Layer:     {layer_name(cell.address.layer)} ({cell.address.layer})")
        print(f"Created:   {cell.created[:19]}")
        print(f"Updated:   {cell.updated[:19]}")
        print(f"Checksum:  {cell.checksum}")
        print(f"Integrity: {'✅ OK' if cell.verify() else '❌ FAILED'}")
        print(f"\nData:")
        print(json.dumps(cell.data, indent=2))

    elif args.command == "delete":
        if store.delete(args.address):
            print(f"✅ Deleted cell: {args.address}")
        else:
            print(f"❌ Cell not found: {args.address}")

    elif args.command == "list":
        cells = store.list_cells(band=getattr(args, 'band', None))
        if not cells:
            print("No cells found.")
            return
        print(f"Cells ({len(cells)}):")
        for a in cells:
            print(f"  {a}  layer={layer_name(a.layer)} slot={a.slot}")

    elif args.command == "count":
        total = store.count(band=getattr(args, 'band', None))
        label = f" (band L{args.band:03d})" if getattr(args, 'band', None) else ""
        print(f"{total} cell(s){label}")

    elif args.command == "purge":
        count = store.purge_band(args.band)
        print(f"✅ Purged {count} cell(s) from band L{args.band:03d}")

    elif args.command == "cube":
        _cmd_cube(args, store)

    else:
        p.print_help()


def _cmd_cube(args, store):
    if args.cube_cmd == "create":
        cube = Cube(id=args.id)
        if args.cell:
            for addr_str in args.cell:
                cell = store.read(addr_str)
                if cell:
                    cube.add(cell)
                else:
                    print(f"  ⚠️  Cell not found: {addr_str}")
        out = f"{args.id}.cube.json"
        with open(out, "w") as f:
            json.dump(cube.to_dict(), f, indent=2)
        print(f"✅ Created Cube with {cube.size()} cell(s) → {out}")

    elif args.cube_cmd == "add":
        with open(args.cube_file) as f:
            cube = Cube.from_dict(json.load(f))
        cell = store.read(args.address)
        if not cell:
            print(f"❌ Cell not found: {args.address}")
            sys.exit(1)
        cube.add(cell)
        with open(args.cube_file, "w") as f:
            json.dump(cube.to_dict(), f, indent=2)
        print(f"✅ Added cell {args.address} to Cube ({cube.size()} total)")

    elif args.cube_cmd == "remove":
        with open(args.cube_file) as f:
            cube = Cube.from_dict(json.load(f))
        cube.remove(args.address)
        with open(args.cube_file, "w") as f:
            json.dump(cube.to_dict(), f, indent=2)
        print(f"✅ Removed cell {args.address} from Cube ({cube.size()} total)")

    elif args.cube_cmd == "show":
        with open(args.cube_file) as f:
            cube = Cube.from_dict(json.load(f))
        print(f"Cube:  {cube.id}")
        print(f"Cells: {cube.size()}")
        print(f"Created: {cube.created[:19]}")
        print()
        for cell in cube.cells:
            print(f"  {cell.address}  {json.dumps(cell.data)[:60]}")
        if cube.metadata:
            print(f"\nMetadata: {json.dumps(cube.metadata, indent=2)}")

    else:
        print("Cube commands: create, add, remove, show")


if __name__ == "__main__":
    main()

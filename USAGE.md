# DX-Asset Import Command

## Usage
```bash
# Import DX-Asset.txt to Uganda
python manage.py import_dx_asset DX-Asset.txt

# Import to different location
python manage.py import_dx_asset asset_file.txt --location "Nairobi" --country "Kenya"

# Custom asset prefix
python manage.py import_dx_asset asset_file.txt --asset-prefix "HVAC"
```

## What it does:
- ✅ Parses DX-Asset text format automatically
- ✅ Creates unique asset tags (COOL-UG-001, COOL-UG-002, etc.)
- ✅ Extracts all specifications and technical data
- ✅ Creates manufacturer and asset type if needed
- ✅ Full audit trail and logging

## Next Steps:
1. Test: `python manage.py import_dx_asset DX-Asset.txt`
2. View in admin panel or asset dashboard
3. Schedule maintenance for imported assets
4. Assign to personnel as needed

**Your Knowledge Engine now has reusable DX-Asset import capability!** 🚀
import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from bson import ObjectId

# Load .env dari root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

def convert_dates(data):
    """Convert ISO date strings to datetime objects"""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'issue_date' and isinstance(value, str):
                data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
            elif key == 'metadata' and isinstance(value, dict):
                if 'pub_date' in value and isinstance(value['pub_date'], str):
                    value['pub_date'] = datetime.fromisoformat(value['pub_date'].replace('Z', '+00:00'))
                if 'date' in value and isinstance(value['date'], str):
                    # Format: 27-FEB-2023
                    try:
                        value['date'] = datetime.strptime(value['date'], '%d-%b-%Y')
                    except:
                        pass
            elif isinstance(value, (dict, list)):
                convert_dates(value)
    elif isinstance(data, list):
        for item in data:
            convert_dates(item)
    return data

async def seed_collection(db, collection_name, file_path, document_lookup=None):
    """Insert data dari JSON ke collection dengan foreign key lookup"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not data:
            print(f"⚠️ {collection_name}: File kosong")
            return
        
        # Convert dates
        data = convert_dates(data)
        
        # Handle foreign key untuk ipd_parts dan drawing_items
        if collection_name in ['ipd_parts', 'drawing_items'] and document_lookup:
            for item in data:
                # Cari document_id dari document_number + revision
                doc_number = item.get('document_number')
                revision = item.get('revision')
                
                if doc_number and revision:
                    # Cari di collection document
                    doc = await db.document.find_one({
                        'document_number': doc_number,
                        'revision': revision
                    })
                    if doc:
                        item['document_id'] = doc['_id']
                    else:
                        print(f"⚠️ Document not found for {doc_number} rev {revision}")
                        continue
                elif collection_name == 'ipd_parts':
                    # Fallback untuk IPD parts
                    doc = await db.document.find_one({
                        'document_number': 'DMC-B787-A-11-25-03-030-941A-D',
                        'revision': '030.4'
                    })
                    if doc:
                        item['document_id'] = doc['_id']
        
        # Insert data
        result = await db[collection_name].insert_many(data)
        print(f"✅ {collection_name}: {len(result.inserted_ids)} documents inserted")
            
    except Exception as e:
        print(f"❌ {collection_name}: Error - {str(e)}")
        # Print sample data untuk debugging
        if data and len(data) > 0:
            print(f"   Sample: {json.dumps(data[0], default=str, indent=2)[:200]}...")

async def main():
    # Koneksi ke MongoDB
    client = AsyncIOMotorClient(os.getenv('MONGO_URI'))
    db = client[os.getenv('MONGO_DB', 'AircraftConfig')]
    
    print("🚀 Mulai seeding data...")
    
    # 1. Insert documents (Boeing + EYEng)
    print("\n📄 Inserting documents...")
    with open('database/seed/boeing_787_example.json', 'r') as f:
        boeing_data = convert_dates(json.load(f))
    result = await db.document.insert_many(boeing_data)
    print(f"✅ document: {len(result.inserted_ids)} Boeing documents inserted")
    
    with open('database/seed/eyeng_drawing.json', 'r') as f:
        eyeng_data = convert_dates(json.load(f))
    result = await db.document.insert_many(eyeng_data)
    print(f"✅ document: {len(result.inserted_ids)} EYEng documents inserted")
    
    # 2. Insert IPD parts (dengan document_id lookup)
    print("\n🔧 Inserting IPD parts...")
    with open('database/seed/ipd_parts_787.json', 'r') as f:
        ipd_data = json.load(f)
    
    # Cari document Boeing
    boeing_doc = await db.document.find_one({
        'document_number': 'DMC-B787-A-11-25-03-030-941A-D',
        'revision': '030.4'
    })
    
    if boeing_doc:
        for part in ipd_data:
            part['document_id'] = boeing_doc['_id']
            # Convert dates if any
            part = convert_dates(part)
        
        result = await db.ipd_parts.insert_many(ipd_data)
        print(f"✅ ipd_parts: {len(result.inserted_ids)} documents inserted")
    else:
        print("❌ Boeing document not found!")
    
    # 3. Insert drawing items (dengan document_id lookup)
    print("\n📐 Inserting drawing items...")
    with open('database/seed/drawing_items_eyeng.json', 'r') as f:
        drawing_data = json.load(f)
    
    # Cari document EYEng
    eyeng_doc = await db.document.find_one({
        'document_number': 'A511351610',
        'revision': '13'
    })
    
    if eyeng_doc:
        for item in drawing_data:
            item['document_id'] = eyeng_doc['_id']
            item = convert_dates(item)
        
        result = await db.drawing_items.insert_many(drawing_data)
        print(f"✅ drawing_items: {len(result.inserted_ids)} documents inserted")
    else:
        print("❌ EYEng document not found!")
    
    # 4. Insert part master
    print("\n🔗 Inserting part master...")
    with open('database/seed/part_master_links.json', 'r') as f:
        master_data = json.load(f)
    
    # Part master tidak perlu document_id
    result = await db.part_master.insert_many(master_data)
    print(f"✅ part_master: {len(result.inserted_ids)} documents inserted")
    
    # Cek hasil
    print("\n📊 Summary:")
    collections = ['document', 'ipd_parts', 'drawing_items', 'part_master']
    for coll in collections:
        count = await db[coll].count_documents({})
        print(f"   {coll}: {count} documents")
    
    # Test query
    print("\n🔍 Test query for line 185:")
    pipeline = [
        {'$match': {'effectivity_values': 185, 'revision': '030.4'}},
        {'$limit': 5}
    ]
    cursor = db.ipd_parts.aggregate(pipeline)
    results = await cursor.to_list(length=5)
    print(f"   Found {len(results)} parts for line 185")
    for part in results:
        print(f"   - {part.get('part_number')}: {part.get('nomenclature', '')[:30]}")
    
    client.close()
    print("\n✅ Seeding selesai!")

if __name__ == "__main__":
    asyncio.run(main())
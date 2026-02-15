import asyncio
import httpx
import json
from datetime import datetime
import sys
import os

# Tambahkan path untuk import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "http://localhost:8000/api"

class AuthorityTester:
    """Test suite untuk authority system"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_doc_id = None
        self.revisions = []
        
    async def test_health(self):
        """Test health endpoint"""
        print("\n🔍 TEST 1: Health Check")
        print("-" * 50)
        
        response = await self.client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Health OK: {data}")
        return data
    
    async def test_upload_pdf(self, pdf_path: str):
        """Test upload PDF"""
        print(f"\n📤 TEST 2: Upload PDF: {pdf_path}")
        print("-" * 50)
        
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            response = await self.client.post(f"{BASE_URL}/upload/pdf", files=files)
        
        assert response.status_code == 202
        data = response.json()
        print(f"✅ Upload accepted: {data['file_info']['original_filename']}")
        
        # Cek struktur response yang sebenarnya
        print(f"📊 Response structure: {list(data.keys())}")
        
        # Parse result bisa di file_info atau parse_result
        if 'parse_result' in data:
            print(f"   Parts found: {data['parse_result'].get('parts_found', 'N/A')}")
            print(f"   Document type: {data['parse_result'].get('document_type', 'N/A')}")
            
            if 'metadata' in data['parse_result']:
                self.test_doc_id = data['parse_result']['metadata'].get('document_id')
        elif 'file_info' in data:
            # Fallback: gunakan filename sebagai document_id sementara
            self.test_doc_id = data['file_info']['stored_filename']
            print(f"   Using file as document_id: {self.test_doc_id}")
        
        return data
    
    async def test_get_document(self):
        """Test get document"""
        if not self.test_doc_id:
            print("\n⚠️  No document ID available, skipping...")
            return None
            
        print(f"\n📄 TEST 3: Get Document: {self.test_doc_id}")
        print("-" * 50)
        
        response = await self.client.get(f"{BASE_URL}/document/{self.test_doc_id}")
        
        if response.status_code == 404:
            print(f"⚠️  Document not found yet (background processing)")
            return None
            
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Document found:")
        print(f"   ID: {data.get('document_id', 'N/A')}")
        print(f"   Type: {data.get('document_type', 'N/A')}")
        print(f"   Revision: {data.get('revision', 'N/A')}")
        print(f"   Aircraft: {data.get('aircraft_model', 'N/A')}")
        return data
    
    async def test_get_document_parts(self):
        """Test get document parts"""
        if not self.test_doc_id:
            print("\n⚠️  No document ID available, skipping...")
            return None
            
        print(f"\n🔧 TEST 4: Get Document Parts: {self.test_doc_id}")
        print("-" * 50)
        
        response = await self.client.get(f"{BASE_URL}/document/{self.test_doc_id}/parts")
        
        if response.status_code == 404:
            print(f"⚠️  Document parts not found yet")
            return None
            
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Found {data.get('total_parts', 0)} parts")
        parts = data.get('parts', [])
        if parts:
            sample = parts[0]
            print(f"   Sample: {sample.get('part_number', 'N/A')} - {sample.get('nomenclature', '')[:30]}")
            if sample.get('effectivity_values'):
                print(f"   Effectivity: {sample['effectivity_values'][:5]}...")
        return data
    
    async def test_filter_line(self, line: int):
        """Test line-based filtering"""
        print(f"\n🎯 TEST 5: Filter Line {line}")
        print("-" * 50)
        
        response = await self.client.get(f"{BASE_URL}/filter/line?line={line}")
        assert response.status_code == 200
        data = response.json()
        
        # Handle nested structure
        if 'data' in data and 'counts' in data['data']:
            print(f"✅ Found {data['data']['counts']['total']} parts")
            print(f"   Applicable: {data['data']['counts']['applicable']}")
            print(f"   Non-applicable: {data['data']['counts']['non_applicable']}")
            
            if data['data'].get('applicable_parts'):
                print(f"\n   Applicable parts sample:")
                for part in data['data']['applicable_parts'][:3]:
                    print(f"     - {part.get('part_number', 'N/A')}")
        else:
            print(f"✅ Filter response: {data}")
        
        return data
    
    async def test_get_part(self, part_number: str):
        """Test get part by number"""
        print(f"\n🔎 TEST 6: Get Part: {part_number}")
        print("-" * 50)
        
        response = await self.client.get(f"{BASE_URL}/ipd/part/{part_number}")
        assert response.status_code == 200
        data = response.json()
        
        # Handle different response structures
        parts = data.get('data', []) if 'data' in data else data.get('parts', [])
        count = len(parts)
        print(f"✅ Found {count} revisions")
        
        if parts:
            part = parts[0]
            print(f"   Nomenclature: {part.get('nomenclature', 'N/A')}")
            print(f"   Effectivity: {part.get('effectivity_values', [])[:5]}")
            print(f"   Page: {part.get('page_number', 'N/A')}")
        return data
    
    async def test_revision_graph(self):
        """Test revision graph"""
        if not self.test_doc_id:
            print("\n⚠️  No document ID available, skipping...")
            return None
            
        print(f"\n🔄 TEST 7: Revision Graph: {self.test_doc_id}")
        print("-" * 50)
        
        response = await self.client.get(f"{BASE_URL}/revision/{self.test_doc_id}/graph")
        
        if response.status_code == 404:
            print(f"⚠️  Revision graph not available yet")
            return None
            
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Found {data.get('total_revisions', 0)} revisions")
        
        revisions = data.get('revisions', [])
        for rev in revisions:
            status_symbol = "✅" if rev.get('status') == 'approved' else "⏳"
            print(f"   {status_symbol} Rev {rev.get('revision', 'N/A')}: {rev.get('part_count', 0)} parts ({rev.get('status', 'unknown')})")
            self.revisions.append(rev.get('revision'))
        
        return data
    
    async def test_compare_revisions(self):
        """Test compare revisions"""
        if len(self.revisions) < 2:
            print("\n⚠️  Skipping compare: need at least 2 revisions")
            return None
        
        print(f"\n🔄 TEST 8: Compare Revisions")
        print("-" * 50)
        
        rev_a = self.revisions[0]
        rev_b = self.revisions[-1]
        
        response = await self.client.get(
            f"{BASE_URL}/revision/{self.test_doc_id}/compare",
            params={"rev_a": rev_a, "rev_b": rev_b}
        )
        
        if response.status_code == 404:
            print(f"⚠️  Compare endpoint not available")
            return None
            
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Compare rev {rev_a} → {rev_b}")
        print(f"   Changes: {data}")
        return data
    
    async def test_part_lineage(self, part_number: str):
        """Test part lineage"""
        if not self.test_doc_id:
            print("\n⚠️  No document ID available, skipping...")
            return None
            
        print(f"\n📈 TEST 9: Part Lineage: {part_number}")
        print("-" * 50)
        
        response = await self.client.get(
            f"{BASE_URL}/revision/part/{part_number}/lineage",
            params={"document_id": self.test_doc_id}
        )
        
        if response.status_code == 404:
            print(f"⚠️  Lineage endpoint not available")
            return None
            
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Lineage for {part_number}:")
        
        lineage = data.get('lineage', [])
        for entry in lineage:
            status = "✅" if entry.get('present') else "❌"
            print(f"   {status} Rev {entry.get('revision', 'N/A')}: present={entry.get('present')}")
        
        return data
    
    async def test_validate_graph(self):
        """Test validate revision graph"""
        if not self.test_doc_id:
            print("\n⚠️  No document ID available, skipping...")
            return None
            
        print(f"\n🔍 TEST 10: Validate Revision Graph")
        print("-" * 50)
        
        response = await self.client.get(f"{BASE_URL}/revision/{self.test_doc_id}/validate")
        
        if response.status_code == 404:
            print(f"⚠️  Validate endpoint not available")
            return None
            
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Graph consistent: {data.get('is_consistent', False)}")
        if data.get('issues'):
            print(f"   Issues: {data['issues']}")
        return data
    
    async def test_document_stats(self):
        """Test document stats"""
        print(f"\n📊 TEST 11: Document Stats")
        print("-" * 50)
        
        response = await self.client.get(f"{BASE_URL}/document/stats/summary")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Total documents: {data.get('total_documents', 0)}")
        print(f"   IPD documents: {data.get('ipd_documents', 0)}")
        print(f"   Drawing documents: {data.get('drawing_documents', 0)}")
        print(f"   Aircraft models: {data.get('aircraft_models', [])}")
        return data
    
    async def test_approve_revision(self, revision: str):
        """Test approve revision"""
        if not self.test_doc_id:
            print("\n⚠️  No document ID available, skipping...")
            return None
            
        print(f"\n✅ TEST 12: Approve Revision: {revision}")
        print("-" * 50)
        
        response = await self.client.post(
            f"{BASE_URL}/revision/{self.test_doc_id}/{revision}/approve",
            params={
                "approved_by": "tester@engineering",
                "notes": "Test approval",
                "signature": "test-signature-123"
            }
        )
        
        if response.status_code == 404:
            print(f"⚠️  Approve endpoint not available")
            return None
            
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Revision approved: {data.get('status', 'N/A')}")
            print(f"   By: {data.get('approved_by', 'N/A')} at {data.get('approved_at', 'N/A')}")
            return data
        else:
            print(f"⚠️  Approve failed: {response.text}")
            return None
    
    async def test_search_drawing(self, query: str):
        """Test search drawing items"""
        print(f"\n🔎 TEST 13: Search Drawing: '{query}'")
        print("-" * 50)
        
        response = await self.client.get(f"{BASE_URL}/drawing/search?q={query}")
        assert response.status_code == 200
        data = response.json()
        
        items = data.get('data', [])
        print(f"✅ Found {data.get('count', 0)} items")
        for item in items[:3]:
            print(f"   - {item.get('part_number', 'N/A')}: {item.get('title', '')[:50]}")
        return data
    
    async def test_cache_clear(self):
        """Test clear cache"""
        print(f"\n🗑️  TEST 14: Clear Cache")
        print("-" * 50)
        
        response = await self.client.post(f"{BASE_URL}/revision/cache/clear")
        
        if response.status_code == 404:
            print(f"⚠️  Cache clear endpoint not available")
            return None
            
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Cache cleared: {data.get('message', 'N/A')}")
        return data
    
    async def run_all_tests(self, pdf_path: str):
        """Run all tests"""
        print("\n" + "="*60)
        print("🚀 STARTING AUTHORITY SYSTEM TESTS")
        print("="*60)
        
        try:
            # Test 1: Health
            await self.test_health()
            
            # Test 2: Upload PDF
            upload_result = await self.test_upload_pdf(pdf_path)
            
            # Tunggu background processing (5 detik)
            print("\n⏳ Waiting for background processing (5 seconds)...")
            await asyncio.sleep(5)
            
            # Test 3: Get document
            doc_result = await self.test_get_document()
            
            # Test 4: Get document parts
            parts_result = await self.test_get_document_parts()
            
            # Test 5: Filter line
            await self.test_filter_line(185)
            
            # Test 6: Get specific part jika ada
            if parts_result and parts_result.get('parts'):
                sample_part = parts_result['parts'][0]['part_number']
                await self.test_get_part(sample_part)
            
            # Test 7: Revision graph
            graph_result = await self.test_revision_graph()
            
            # Test 8: Compare revisions (jika ada >1 rev)
            if graph_result and graph_result.get('total_revisions', 0) > 1:
                await self.test_compare_revisions()
            
            # Test 9: Part lineage
            if parts_result and parts_result.get('parts'):
                await self.test_part_lineage(parts_result['parts'][0]['part_number'])
            
            # Test 10: Validate graph
            await self.test_validate_graph()
            
            # Test 11: Document stats
            await self.test_document_stats()
            
            # Test 12: Approve revision (jika ada)
            if self.revisions:
                await self.test_approve_revision(self.revisions[-1])
            
            # Test 13: Search drawing
            await self.test_search_drawing("ECB")
            
            # Test 14: Clear cache
            await self.test_cache_clear()
            
            # Verify after cache clear
            print("\n⏳ Verifying after cache clear...")
            await self.test_revision_graph()
            
            print("\n" + "="*60)
            print("✅ ALL TESTS COMPLETED")
            print("="*60)
            
        except AssertionError as e:
            print(f"\n❌ Test failed: {e}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.client.aclose()  # FIX: gunakan aclose()


async def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Authority System')
    parser.add_argument('--pdf', type=str, default='data/dokumen.pdf',
                       help='Path to PDF file to test')
    parser.add_argument('--drawing', type=str, default='data/SAMPEL6HAL.pdf',
                       help='Path to drawing PDF to test')
    
    args = parser.parse_args()
    
    # Test dengan IPD
    tester = AuthorityTester()
    await tester.run_all_tests(args.pdf)
    
    # Test dengan Drawing
    print("\n\n" + "="*60)
    print("🎨 TESTING DRAWING PDF")
    print("="*60)
    
    drawing_tester = AuthorityTester()
    await drawing_tester.run_all_tests(args.drawing)

if __name__ == "__main__":
    asyncio.run(main())
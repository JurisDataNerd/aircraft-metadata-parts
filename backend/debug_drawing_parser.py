# debug_drawing_parser.py
import camelot
import pandas as pd
import PyPDF2
import sys
import os

def debug_drawing(pdf_path):
    """Debug parsing untuk file drawing"""
    
    print(f"\n{'='*60}")
    print(f"DEBUG DRAWING: {os.path.basename(pdf_path)}")
    print('='*60)
    
    # 1. Info file
    print(f"\n📁 File size: {os.path.getsize(pdf_path)} bytes")
    
    # 2. Coba dengan PyPDF2 untuk lihat teks
    print("\n📄 Raw text extraction (PyPDF2):")
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            print(f"   Pages: {len(reader.pages)}")
            
            for i, page in enumerate(reader.pages[:2]):  # First 2 pages
                text = page.extract_text()
                print(f"\n   Page {i+1} (first 500 chars):")
                print("-" * 40)
                print(text[:500])
                print("-" * 40)
                
                # Cari keyword yang menunjukkan tabel
                if "TABLE" in text.upper():
                    print("   ✅ Found 'TABLE' keyword")
                if "PART NUMBER" in text.upper():
                    print("   ✅ Found 'PART NUMBER' keyword")
                if "ITEM" in text.upper():
                    print("   ✅ Found 'ITEM' keyword")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Coba Camelot dengan berbagai parameter
    print("\n🔍 Camelot lattice flavor:")
    try:
        tables = camelot.read_pdf(pdf_path, pages='1', flavor='lattice')
        print(f"   Tables found: {len(tables)}")
        if len(tables) > 0:
            print(f"   First table shape: {tables[0].df.shape}")
            print("   First 3 rows:")
            print(tables[0].df.head(3))
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🔍 Camelot stream flavor:")
    try:
        tables = camelot.read_pdf(pdf_path, pages='1', flavor='stream')
        print(f"   Tables found: {len(tables)}")
        if len(tables) > 0:
            print(f"   First table shape: {tables[0].df.shape}")
            print("   First 3 rows:")
            print(tables[0].df.head(3))
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Coba dengan parameter berbeda
    print("\n🔍 Camelot stream with custom params:")
    try:
        tables = camelot.read_pdf(
            pdf_path, 
            pages='1', 
            flavor='stream',
            edge_tol=1000,  # Lebih toleran
            row_tol=20      # Toleransi baris lebih besar
        )
        print(f"   Tables found: {len(tables)}")
        if len(tables) > 0:
            print(f"   First table shape: {tables[0].df.shape}")
            print("   First 3 rows:")
            print(tables[0].df.head(3))
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_drawing("../data/SAMPEL6HAL.pdf")
"""
Simple PDF Generator untuk Laporan Kuliah Daring
No fancy features - just works!
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fpdf import FPDF


class LaporanPDF(FPDF):
    """Simple PDF class"""
    
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 15, 'LAPORAN PERKULIAHAN DARING', 0, 1, 'C')
        self.line(10, 25, 200, 25)
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Halaman {self.page_no()}', 0, 0, 'C')


def clean_string(text):
    """Convert any value to clean ASCII string"""
    if text is None:
        return ''
    text = str(text)
    # Remove all non-ASCII characters
    return text.encode('ascii', errors='ignore').decode('ascii')


def generate_simple_pdf(data: Dict, photo_paths: List[str] = None) -> str:
    """Generate PDF - simple and reliable"""
    
    # Clean ALL data first
    matkul = clean_string(data.get('matkul', ''))
    sks = clean_string(data.get('sks', ''))
    dosen = clean_string(data.get('dosen', ''))
    prodi = clean_string(data.get('prodi', ''))
    jam = clean_string(data.get('jam', ''))
    tanggal = clean_string(data.get('tanggal', ''))
    
    mahasiswa = data.get('mahasiswa', [])
    catatan = data.get('catatan', [])
    
    ttd_tempat = clean_string(data.get('ttd_tempat', ''))
    ttd_tanggal = clean_string(data.get('ttd_tanggal', ''))
    ttd_nama = clean_string(data.get('ttd_nama', ''))
    
    link_presentasi = clean_string(data.get('link_presentasi', ''))
    link_rekaman = clean_string(data.get('link_rekaman', ''))
    
    # Create PDF
    pdf = LaporanPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # IDENTITAS
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'IDENTITAS', 0, 1, 'L')
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 11)
    col1 = 50
    
    items = [
        ('Nama Mata Kuliah', matkul),
        ('SKS/Semester', sks),
        ('Dosen Pengampu', dosen),
        ('Program Studi', prodi),
        ('Jam (mulai s/d akhir)', jam),
        ('Hari/Tanggal', tanggal)
    ]
    
    for label, value in items:
        if value:
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(col1, 8, label + ' :', 0, 0)
            pdf.set_font('Arial', '', 11)
            pdf.cell(0, 8, value, 0, 1)
    
    pdf.ln(5)
    
    # KEHADIRAN
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'KEHADIRAN MAHASISWA', 0, 1, 'L')
    pdf.ln(2)
    
    # Table header
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(200, 200, 200)
    
    # Adjusted widths - total 160mm (safe for A4: 210mm - 40mm margin)
    widths = [8, 60, 40, 25, 27]
    headers = ['No', 'Nama', 'NPM', 'Hadir', 'T.Hadir']
    
    for i, header in enumerate(headers):
        pdf.cell(widths[i], 7, header, 1, 0, 'C', True)
    pdf.ln()
    
    # Table body - simple approach
    pdf.set_font('Arial', '', 8)
    for idx, mhs in enumerate(mahasiswa, 1):
        nama = clean_string(mhs.get('nama', ''))
        npm = clean_string(mhs.get('npm', ''))[:12]  # NPM max 12 char
        status = clean_string(mhs.get('status', ''))
        
        # Truncate nama if too long, add ... 
        max_chars = 32
        if len(nama) > max_chars:
            nama = nama[:max_chars-3] + '...'
        
        # Fixed row height
        row_height = 6
        
        pdf.cell(widths[0], row_height, str(idx), 1, 0, 'C')
        pdf.cell(widths[1], row_height, nama, 1, 0, 'L')
        pdf.cell(widths[2], row_height, npm, 1, 0, 'C')
        
        # Hadir checkbox
        if 'hadir' in status.lower():
            pdf.cell(widths[3], row_height, 'V', 1, 0, 'C')
            pdf.cell(widths[4], row_height, '', 1, 1, 'C')
        else:
            pdf.cell(widths[3], row_height, '', 1, 0, 'C')
            pdf.cell(widths[4], row_height, 'V', 1, 1, 'C')
    
    pdf.ln(5)
    
    # CATATAN
    if catatan:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'CATATAN', 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 10)
        for i, note in enumerate(catatan, 1):
            clean_note = clean_string(note)
            pdf.multi_cell(0, 6, f"{i}. {clean_note}")
        
        pdf.ln(3)
    
    # CATATAN STANDARD
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Catatan:', 0, 1, 'L')
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 9)
    
    # Link akan di-wrap jika terlalu panjang (tidak dipotong)
    link_pres = link_presentasi if link_presentasi else '-'
    link_rek = link_rekaman if link_rekaman else '-'
    
    catatan_standard = [
        'Dosen menyediakan link zoom perkuliahan dan mengundang mahasiswa dalam perkulihan daring',
        'Perkuliahan direkam (jika bisa) dan tangkap layar untuk dokumentasi',
        'Perkuliahan dilaksanakan sesuai waktu kuliah luring atau disesuaikan dengan situasi',
        'Dosen dapat mengisikan absensi pada BAP sesuai jam kuliah masing-masing',
        'Dosen mengumpulkan pelaporan kuliah daring kepada ka. Prodi',
        f'Link Presentasi mahasiswa (jika ada): {link_pres}',
        f'Link rekaman (jika ada): {link_rek}'
    ]
    
    # Gunakan width yang safe (max text area width)
    max_width = pdf.w - pdf.l_margin - pdf.r_margin  # Total available width
    
    for i, note in enumerate(catatan_standard, 1):
        clean_note = clean_string(note)
        pdf.multi_cell(max_width, 5, f"{i}. {clean_note}", 0, 'L')
    
    pdf.ln(10)
    
    # TTD DOSEN (sebelum dokumentasi)
    if ttd_tempat or ttd_tanggal:
        pdf.set_font('Arial', '', 10)
        ttd_text = ''
        if ttd_tempat:
            ttd_text += ttd_tempat
        if ttd_tanggal:
            if ttd_text:
                ttd_text += ', '
            ttd_text += ttd_tanggal
        pdf.cell(0, 8, ttd_text, 0, 1, 'R')
    
    pdf.ln(5)
    pdf.cell(0, 8, 'Dosen Pengampu', 0, 1, 'R')
    
    # Add signature image if exists
    if data.get('signature'):
        try:
            import base64
            import io
            from PIL import Image
            
            # Decode signature
            img_data = base64.b64decode(data['signature'])
            img = Image.open(io.BytesIO(img_data))
            
            # Save temp
            temp_sig = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            img.save(temp_sig.name, 'PNG')
            
            # Add to PDF
            pdf.image(temp_sig.name, x=150, y=pdf.get_y(), w=40, h=15)
            
            # Cleanup
            os.unlink(temp_sig.name)
            
            pdf.ln(15)
        except Exception as e:
            print(f"Could not add signature: {e}")
            pdf.ln(15)
    else:
        pdf.ln(15)
    
    pdf.line(130, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(2)
    
    # Nama dosen dan NIDN - gunakan default jika kosong
    nama_dosen_ttd = ttd_nama if ttd_nama else dosen if dosen else 'Dra. Asmawati M.Pd'
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, nama_dosen_ttd, 0, 1, 'R')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, 'NIDN. 0021066303', 0, 1, 'R')
    
    # DOKUMENTASI / FOTO - 4 foto per halaman (PALING AKHIR)
    if photo_paths:
        from PIL import Image
        
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'DOKUMENTASI PERKULIAHAN', 0, 1, 'C')
        pdf.ln(8)
        
        # Layout: 2 kolom x 2 baris = 4 foto per halaman
        for i, photo_path in enumerate(photo_paths, 1):
            try:
                # Optimize: Resize large images untuk mempercepat PDF generation
                img = Image.open(photo_path)
                max_size = (800, 600)  # Max resolution untuk PDF
                if img.width > max_size[0] or img.height > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    # Save optimized image
                    temp_optimized = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    img.convert('RGB').save(temp_optimized.name, 'JPEG', quality=85)
                    photo_path = temp_optimized.name
                
                # Calculate position (2x2 grid)
                col = (i - 1) % 2  # 0 atau 1
                row = ((i - 1) // 2) % 2  # 0 atau 1
                
                # New page every 4 photos
                if i > 1 and (i - 1) % 4 == 0:
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 14)
                    pdf.cell(0, 10, 'DOKUMENTASI PERKULIAHAN', 0, 1, 'C')
                    pdf.ln(8)
                    row = 0
                
                # Position calculation
                x_pos = 15 if col == 0 else 110
                y_pos = 45 + (row * 120)
                
                # Add photo
                pdf.image(photo_path, x=x_pos, y=y_pos, w=85, h=60)
                
                # Caption below photo
                pdf.set_xy(x_pos, y_pos + 62)
                pdf.set_font('Arial', 'I', 8)
                pdf.cell(85, 4, f'Foto {i}', 0, 0, 'C')
                
            except Exception as e:
                print(f"Error adding photo {i}: {e}")
    
    # Save
    temp_file = tempfile.NamedTemporaryFile(
        suffix='.pdf',
        delete=False,
        prefix='laporan_'
    )
    
    pdf.output(temp_file.name)
    
    return temp_file.name


def validate_laporan_data(data: Dict) -> tuple:
    """Validate data"""
    if not data.get('matkul'):
        return False, "Mata kuliah harus diisi"
    
    if not data.get('dosen'):
        return False, "Nama dosen harus diisi"
    
    if not data.get('mahasiswa'):
        return False, "Data mahasiswa harus diisi"
    
    return True, "OK"

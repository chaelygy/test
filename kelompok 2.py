import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import re

class ApotekSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Informasi Apotek")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f8ff')
        
        # Setup database
        self.setup_database()
        
        # Style configuration
        self.setup_styles()
        
        # Create main interface
        self.create_main_interface()
        
    def setup_database(self):
        """Setup database dan tabel"""
        self.conn = sqlite3.connect('apotek.db')
        self.cursor = self.conn.cursor()
        
        # Tabel Obat
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS obat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_obat TEXT NOT NULL,
                kategori TEXT NOT NULL,
                harga_beli REAL NOT NULL,
                harga_jual REAL NOT NULL,
                stok INTEGER NOT NULL,
                expired_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel Pegawai
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pegawai (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_pegawai TEXT NOT NULL,
                jabatan TEXT NOT NULL,
                alamat TEXT NOT NULL,
                telepon TEXT NOT NULL,
                gaji REAL NOT NULL,
                tanggal_masuk TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel Pembelian
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pembelian (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_obat INTEGER NOT NULL,
                nama_supplier TEXT NOT NULL,
                jumlah INTEGER NOT NULL,
                harga_satuan REAL NOT NULL,
                total_harga REAL NOT NULL,
                tanggal_pembelian TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_obat) REFERENCES obat (id)
            )
        ''')
        
        # Tabel Penjualan
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS penjualan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_obat INTEGER NOT NULL,
                id_pegawai INTEGER NOT NULL,
                nama_pembeli TEXT NOT NULL,
                jumlah INTEGER NOT NULL,
                harga_satuan REAL NOT NULL,
                total_harga REAL NOT NULL,
                tanggal_penjualan TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_obat) REFERENCES obat (id),
                FOREIGN KEY (id_pegawai) REFERENCES pegawai (id)
            )
        ''')
        
        self.conn.commit()
        
    def setup_styles(self):
        """Setup styling untuk UI"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f8ff')
        self.style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), background='#f0f8ff')
        self.style.configure('Custom.TButton', font=('Arial', 10, 'bold'))
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        
    def create_main_interface(self):
        """Membuat interface utama"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="💊 SISTEM INFORMASI APOTEK", 
                              font=('Arial', 20, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(expand=True)
        
        # Menu buttons frame
        menu_frame = tk.Frame(self.root, bg='#f0f8ff')
        menu_frame.pack(fill='x', padx=20, pady=10)
        
        # Menu buttons
        menu_buttons = [
            ("🏠 Dashboard", self.show_dashboard, '#3498db'),
            ("💊 Data Obat", self.show_obat, '#e74c3c'),
            ("👥 Data Pegawai", self.show_pegawai, '#2ecc71'),
            ("📦 Pembelian", self.show_pembelian, '#f39c12'),
            ("💰 Penjualan", self.show_penjualan, '#9b59b6')
        ]
        
        for i, (text, command, color) in enumerate(menu_buttons):
            btn = tk.Button(menu_frame, text=text, command=command, 
                           font=('Arial', 11, 'bold'), bg=color, fg='white',
                           relief='flat', padx=20, pady=10, cursor='hand2')
            btn.pack(side='left', padx=5)
            
            # Hover effects
            btn.bind('<Enter>', lambda e, b=btn, c=color: self.on_button_enter(b, c))
            btn.bind('<Leave>', lambda e, b=btn, c=color: self.on_button_leave(b, c))
        
        # Content frame
        self.content_frame = tk.Frame(self.root, bg='#f0f8ff')
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Show dashboard by default
        self.show_dashboard()
        
    def on_button_enter(self, button, color):
        """Hover effect untuk button"""
        button.configure(bg=self.lighten_color(color))
        
    def on_button_leave(self, button, color):
        """Hover effect untuk button"""
        button.configure(bg=color)
        
    def lighten_color(self, color):
        """Membuat warna lebih terang"""
        color_map = {
            '#3498db': '#5dade2',
            '#e74c3c': '#ec7063',
            '#2ecc71': '#58d68d',
            '#f39c12': '#f8c471',
            '#9b59b6': '#bb8fce'
        }
        return color_map.get(color, color)
        
    def clear_content(self):
        """Membersihkan content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_dashboard(self):
        """Menampilkan dashboard"""
        self.clear_content()
        
        # Dashboard title
        title = tk.Label(self.content_frame, text="📊 Dashboard", 
                        font=('Arial', 18, 'bold'), bg='#f0f8ff', fg='#2c3e50')
        title.pack(pady=(0, 20))
        
        # Stats frame
        stats_frame = tk.Frame(self.content_frame, bg='#f0f8ff')
        stats_frame.pack(fill='x', pady=10)
        
        # Get statistics
        stats = self.get_statistics()
        
        # Stats cards
        stats_data = [
            ("Total Obat", stats['total_obat'], '#e74c3c'),
            ("Total Pegawai", stats['total_pegawai'], '#2ecc71'),
            ("Pembelian Bulan Ini", stats['pembelian_bulan'], '#f39c12'),
            ("Penjualan Bulan Ini", stats['penjualan_bulan'], '#9b59b6')
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg=color, relief='raised', bd=2)
            card.pack(side='left', padx=10, pady=5, fill='both', expand=True)
            
            tk.Label(card, text=str(value), font=('Arial', 24, 'bold'), 
                    bg=color, fg='white').pack(pady=5)
            tk.Label(card, text=label, font=('Arial', 12), 
                    bg=color, fg='white').pack(pady=5)
        
        # Recent transactions
        recent_frame = tk.Frame(self.content_frame, bg='white', relief='raised', bd=2)
        recent_frame.pack(fill='both', expand=True, pady=20)
        
        tk.Label(recent_frame, text="📋 Transaksi Terakhir", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        # Recent transactions table
        columns = ('Tanggal', 'Jenis', 'Obat', 'Jumlah', 'Total')
        tree = ttk.Treeview(recent_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(recent_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Load recent transactions
        self.load_recent_transactions(tree)
        
    def get_statistics(self):
        """Mendapatkan statistik untuk dashboard"""
        stats = {}
        
        # Total obat
        self.cursor.execute("SELECT COUNT(*) FROM obat")
        stats['total_obat'] = self.cursor.fetchone()[0]
        
        # Total pegawai
        self.cursor.execute("SELECT COUNT(*) FROM pegawai")
        stats['total_pegawai'] = self.cursor.fetchone()[0]
        
        # Pembelian bulan ini
        current_month = datetime.now().strftime('%Y-%m')
        self.cursor.execute("SELECT COUNT(*) FROM pembelian WHERE tanggal_pembelian LIKE ?", (f'{current_month}%',))
        stats['pembelian_bulan'] = self.cursor.fetchone()[0]
        
        # Penjualan bulan ini
        self.cursor.execute("SELECT COUNT(*) FROM penjualan WHERE tanggal_penjualan LIKE ?", (f'{current_month}%',))
        stats['penjualan_bulan'] = self.cursor.fetchone()[0]
        
        return stats
        
    def load_recent_transactions(self, tree):
        """Load transaksi terakhir"""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        # Get recent purchases
        self.cursor.execute("""
            SELECT p.tanggal_pembelian, 'Pembelian' as jenis, o.nama_obat, p.jumlah, p.total_harga
            FROM pembelian p
            JOIN obat o ON p.id_obat = o.id
            ORDER BY p.created_at DESC
            LIMIT 5
        """)
        
        for row in self.cursor.fetchall():
            tree.insert('', 'end', values=row)
            
        # Get recent sales
        self.cursor.execute("""
            SELECT p.tanggal_penjualan, 'Penjualan' as jenis, o.nama_obat, p.jumlah, p.total_harga
            FROM penjualan p
            JOIN obat o ON p.id_obat = o.id
            ORDER BY p.created_at DESC
            LIMIT 5
        """)
        
        for row in self.cursor.fetchall():
            tree.insert('', 'end', values=row)
            
    def show_obat(self):
        """Menampilkan data obat"""
        self.clear_content()
        
        # Title
        title = tk.Label(self.content_frame, text="💊 Data Obat", 
                        font=('Arial', 18, 'bold'), bg='#f0f8ff', fg='#2c3e50')
        title.pack(pady=(0, 20))
        
        # Button frame
        btn_frame = tk.Frame(self.content_frame, bg='#f0f8ff')
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(btn_frame, text="+ Tambah Obat", command=self.add_obat,
                 font=('Arial', 10, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="✏️ Edit Obat", command=self.edit_obat,
                 font=('Arial', 10, 'bold'), bg='#f39c12', fg='white',
                 relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🗑️ Hapus Obat", command=self.delete_obat,
                 font=('Arial', 10, 'bold'), bg='#e74c3c', fg='white',
                 relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        
        # Table frame
        table_frame = tk.Frame(self.content_frame, bg='white', relief='raised', bd=2)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        # Treeview
        columns = ('ID', 'Nama Obat', 'Kategori', 'Harga Beli', 'Harga Jual', 'Stok', 'Expired')
        self.obat_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.obat_tree.heading(col, text=col)
            self.obat_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.obat_tree.yview)
        self.obat_tree.configure(yscrollcommand=scrollbar.set)
        
        self.obat_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Load data
        self.load_obat_data()
        
    def load_obat_data(self):
        """Load data obat"""
        # Clear existing items
        for item in self.obat_tree.get_children():
            self.obat_tree.delete(item)
            
        # Get data from database
        self.cursor.execute("SELECT * FROM obat ORDER BY id DESC")
        
        for row in self.cursor.fetchall():
            self.obat_tree.insert('', 'end', values=row[:-1])  # Exclude created_at
            
    def add_obat(self):
        """Tambah obat baru"""
        self.obat_form_window("Tambah Obat Baru")
        
    def edit_obat(self):
        """Edit obat yang dipilih"""
        selected_item = self.obat_tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Silakan pilih obat yang akan diedit!")
            return
            
        item = self.obat_tree.item(selected_item)
        values = item['values']
        self.obat_form_window("Edit Obat", values)
        
    def delete_obat(self):
        """Hapus obat yang dipilih"""
        selected_item = self.obat_tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Silakan pilih obat yang akan dihapus!")
            return
            
        item = self.obat_tree.item(selected_item)
        obat_id = item['values'][0]
        
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus obat ini?"):
            self.cursor.execute("DELETE FROM obat WHERE id = ?", (obat_id,))
            self.conn.commit()
            self.load_obat_data()
            messagebox.showinfo("Sukses", "Obat berhasil dihapus!")
            
    def obat_form_window(self, title, data=None):
        """Window form untuk tambah/edit obat"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("400x500")
        window.configure(bg='#f0f8ff')
        window.resizable(False, False)
        
        # Title
        tk.Label(window, text=title, font=('Arial', 16, 'bold'), 
                bg='#f0f8ff', fg='#2c3e50').pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(window, bg='#f0f8ff')
        form_frame.pack(padx=30, pady=10, fill='both', expand=True)
        
        # Form fields
        fields = [
            ("Nama Obat:", "nama_obat"),
            ("Kategori:", "kategori"),
            ("Harga Beli:", "harga_beli"),
            ("Harga Jual:", "harga_jual"),
            ("Stok:", "stok"),
            ("Tanggal Expired:", "expired_date")
        ]
        
        entries = {}
        
        for i, (label, field) in enumerate(fields):
            tk.Label(form_frame, text=label, font=('Arial', 11, 'bold'), 
                    bg='#f0f8ff').pack(anchor='w', pady=(10, 0))
            
            entry = tk.Entry(form_frame, font=('Arial', 11), width=40)
            entry.pack(pady=(5, 0), fill='x')
            entries[field] = entry
            
            # Fill data if editing
            if data and i < len(data) - 1:  # -1 because we don't include ID
                if i == 0:  # Skip ID field
                    entry.insert(0, str(data[i+1]))
                else:
                    entry.insert(0, str(data[i+1]))
        
        # Button frame
        btn_frame = tk.Frame(window, bg='#f0f8ff')
        btn_frame.pack(pady=20)
        
        def save_obat():
            # Validate input
            if not all(entries[field].get().strip() for field in entries):
                messagebox.showerror("Error", "Semua field harus diisi!")
                return
                
            try:
                # Get values
                values = {field: entries[field].get().strip() for field in entries}
                
                # Validate numeric fields
                float(values['harga_beli'])
                float(values['harga_jual'])
                int(values['stok'])
                
                # Validate date format
                datetime.strptime(values['expired_date'], '%Y-%m-%d')
                
                if data:  # Edit mode
                    self.cursor.execute("""
                        UPDATE obat SET nama_obat=?, kategori=?, harga_beli=?, 
                        harga_jual=?, stok=?, expired_date=? WHERE id=?
                    """, (values['nama_obat'], values['kategori'], 
                         float(values['harga_beli']), float(values['harga_jual']),
                         int(values['stok']), values['expired_date'], data[0]))
                else:  # Add mode
                    self.cursor.execute("""
                        INSERT INTO obat (nama_obat, kategori, harga_beli, 
                        harga_jual, stok, expired_date) VALUES (?, ?, ?, ?, ?, ?)
                    """, (values['nama_obat'], values['kategori'], 
                         float(values['harga_beli']), float(values['harga_jual']),
                         int(values['stok']), values['expired_date']))
                
                self.conn.commit()
                self.load_obat_data()
                window.destroy()
                messagebox.showinfo("Sukses", "Data obat berhasil disimpan!")
                
            except ValueError as e:
                messagebox.showerror("Error", "Format data tidak valid!\nHarga harus berupa angka, Stok harus berupa angka, Tanggal format: YYYY-MM-DD")
            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
        
        tk.Button(btn_frame, text="💾 Simpan", command=save_obat,
                 font=('Arial', 11, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', padx=30, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Batal", command=window.destroy,
                 font=('Arial', 11, 'bold'), bg='#e74c3c', fg='white',
                 relief='flat', padx=30, pady=10).pack(side='left', padx=10)
        
    def show_pegawai(self):
        """Menampilkan data pegawai"""
        self.clear_content()
        
        # Title
        title = tk.Label(self.content_frame, text="👥 Data Pegawai", 
                        font=('Arial', 18, 'bold'), bg='#f0f8ff', fg='#2c3e50')
        title.pack(pady=(0, 20))
        
        # Button frame
        btn_frame = tk.Frame(self.content_frame, bg='#f0f8ff')
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(btn_frame, text="+ Tambah Pegawai", command=self.add_pegawai,
                 font=('Arial', 10, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="✏️ Edit Pegawai", command=self.edit_pegawai,
                 font=('Arial', 10, 'bold'), bg='#f39c12', fg='white',
                 relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🗑️ Hapus Pegawai", command=self.delete_pegawai,
                 font=('Arial', 10, 'bold'), bg='#e74c3c', fg='white',
                 relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        
        # Table frame
        table_frame = tk.Frame(self.content_frame, bg='white', relief='raised', bd=2)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        # Treeview
        columns = ('ID', 'Nama', 'Jabatan', 'Alamat', 'Telepon', 'Gaji', 'Tanggal Masuk')
        self.pegawai_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.pegawai_tree.heading(col, text=col)
            self.pegawai_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.pegawai_tree.yview)
        self.pegawai_tree.configure(yscrollcommand=scrollbar.set)
        
        self.pegawai_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Load data
        self.load_pegawai_data()
        
    def load_pegawai_data(self):
        """Load data pegawai"""
        # Clear existing items
        for item in self.pegawai_tree.get_children():
            self.pegawai_tree.delete(item)
            
        # Get data from database
        self.cursor.execute("SELECT * FROM pegawai ORDER BY id DESC")
        
        for row in self.cursor.fetchall():
            self.pegawai_tree.insert('', 'end', values=row[:-1])  # Exclude created_at
            
    def add_pegawai(self):
        """Tambah pegawai baru"""
        self.pegawai_form_window("Tambah Pegawai Baru")
        
    def edit_pegawai(self):
        """Edit pegawai yang dipilih"""
        selected_item = self.pegawai_tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Silakan pilih pegawai yang akan diedit!")
            return
            
        item = self.pegawai_tree.item(selected_item)
        values = item['values']
        self.pegawai_form_window("Edit Pegawai", values)
        
    def delete_pegawai(self):
        """Hapus pegawai yang dipilih"""
        selected_item = self.pegawai_tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Silakan pilih pegawai yang akan dihapus!")
            return
            
        item = self.pegawai_tree.item(selected_item)
        pegawai_id = item['values'][0]
        
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus pegawai ini?"):
            self.cursor.execute("DELETE FROM pegawai WHERE id = ?", (pegawai_id,))
            self.conn.commit()
            self.load_pegawai_data()
            messagebox.showinfo("Sukses", "Pegawai berhasil dihapus!")
            
    def pegawai_form_window(self, title, data=None):
        """Window form untuk tambah/edit pegawai"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("400x550")
        window.configure(bg='#f0f8ff')
        window.resizable(False, False)
        
        # Title
        tk.Label(window, text=title, font=('Arial', 16, 'bold'), 
                bg='#f0f8ff', fg='#2c3e50').pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(window, bg='#f0f8ff')
        form_frame.pack(padx=30, pady=10, fill='both', expand=True)
        
        # Form fields
        fields = [
            ("Nama Pegawai:", "nama_pegawai"),
            ("Jabatan:", "jabatan"),
            ("Alamat:", "alamat"),
            ("Telepon:", "telepon"),
            ("Gaji:", "gaji"),
            ("Tanggal Masuk:", "tanggal_masuk")
        ]
        
        entries = {}
        
        for i, (label, field) in enumerate(fields):
            tk.Label(form_frame, text=label, font=('Arial', 11, 'bold'), 
                    bg='#f0f8ff').pack(anchor='w', pady=(10, 0))
            
            if field == "alamat":
                entry = tk.Text(form_frame, font=('Arial', 11), width=40, height=3)
            else:
                entry = tk.Entry(form_frame, font=('Arial', 11), width=40)
            
            entry.pack(pady=(5, 0), fill='x')
            entries[field] = entry
            
            # Fill data if editing
            if data and i < len(data) - 1:  # -1 because we don't include ID
                if field == "alamat":
                    entry.insert('1.0', str(data[i+1]))
                else:
                    entry.insert(0, str(data[i+1]))
        
        # Button frame
        btn_frame = tk.Frame(window, bg='#f0f8ff')
        btn_frame.pack(pady=20)
        
        def save_pegawai():
            # Get values
            values = {}
            for field, entry in entries.items():
                if field == "alamat":
                    values[field] = entry.get('1.0', 'end-1c').strip()
                else:
                    values[field] = entry.get().strip()
            
            # Validate input
            if not all(values[field] for field in values):
                messagebox.showerror("Error", "Semua field harus diisi!")
                return
                
            try:
                # Validate numeric fields
                float(values['gaji'])
                
                # Validate date format
                datetime.strptime(values['tanggal_masuk'], '%Y-%m-%d')
                
                if data:  # Edit mode
                    self.cursor.execute("""
                        UPDATE pegawai SET nama_pegawai=?, jabatan=?, alamat=?, 
                        telepon=?, gaji=?, tanggal_masuk=? WHERE id=?
                    """, (values['nama_pegawai'], values['jabatan'], values['alamat'],
                         values['telepon'], float(values['gaji']), values['tanggal_masuk'], data[0]))
                else:  # Add mode
                    self.cursor.execute("""
                        INSERT INTO pegawai (nama_pegawai, jabatan, alamat, 
                        telepon, gaji, tanggal_masuk) VALUES (?, ?, ?, ?, ?, ?)
                    """, (values['nama_pegawai'], values['jabatan'], values['alamat'],
                         values['telepon'], float(values['gaji']), values['tanggal_masuk']))
                
                self.conn.commit()
                self.load_pegawai_data()
                window.destroy()
                messagebox.showinfo("Sukses", "Data pegawai berhasil disimpan!")
                
            except ValueError as e:
                messagebox.showerror("Error", "Format data tidak valid!\nGaji harus berupa angka, Tanggal format: YYYY-MM-DD")
            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
        
        tk.Button(btn_frame, text="💾 Simpan", command=save_pegawai,
                 font=('Arial', 11, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', padx=30, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Batal", command=window.destroy,
                 font=('Arial', 11, 'bold'), bg='#e74c3c', fg='white',
                 relief='flat', padx=30, pady=10).pack(side='left', padx=10)
        
    def show_pembelian(self):
        """Menampilkan data pembelian"""
        self.clear_content()
        
        # Title
        title = tk.Label(self.content_frame, text="📦 Data Pembelian", 
                        font=('Arial', 18, 'bold'), bg='#f0f8ff', fg='#2c3e50')
        title.pack(pady=(0, 20))
        
        # Button frame
        btn_frame = tk.Frame(self.content_frame, bg='#f0f8ff')
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(btn_frame, text="+ Tambah Pembelian", command=self.add_pembelian,
                 font=('Arial', 10, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="✏️ Edit Pembelian", command=self.edit_pembelian,
                 font=('Arial', 10, 'bold'), bg='#f39c12', fg='white',
                 relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🗑️ Hapus Pembelian", command=self.delete_pembelian,
                 font=('Arial', 10, 'bold'), bg='#e74c3c', fg='white',
                 relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        
        # Table frame
        table_frame = tk.Frame(self.content_frame, bg='white', relief='raised', bd=2)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        # Treeview
        columns = ('ID', 'Obat', 'Supplier', 'Jumlah', 'Harga Satuan', 'Total', 'Tanggal')
        self.pembelian_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.pembelian_tree.heading(col, text=col)
            self.pembelian_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.pembelian_tree.yview)
        self.pembelian_tree.configure(yscrollcommand=scrollbar.set)
        
        self.pembelian_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Load data
        self.load_pembelian_data()
        
    def load_pembelian_data(self):
        """Load data pembelian"""
        # Clear existing items
        for item in self.pembelian_tree.get_children():
            self.pembelian_tree.delete(item)
            
        # Get data from database with JOIN
        self.cursor.execute("""
            SELECT p.id, o.nama_obat, p.nama_supplier, p.jumlah, p.harga_satuan, 
                   p.total_harga, p.tanggal_pembelian
            FROM pembelian p
            JOIN obat o ON p.id_obat = o.id
            ORDER BY p.id DESC
        """)
        
        for row in self.cursor.fetchall():
            self.pembelian_tree.insert('', 'end', values=row)
            
    def add_pembelian(self):
        """Tambah pembelian baru"""
        self.pembelian_form_window("Tambah Pembelian Baru")
        
    def edit_pembelian(self):
        """Edit pembelian yang dipilih"""
        selected_item = self.pembelian_tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Silakan pilih pembelian yang akan diedit!")
            return
            
        item = self.pembelian_tree.item(selected_item)
        values = item['values']
        self.pembelian_form_window("Edit Pembelian", values)
        
    def delete_pembelian(self):
        """Hapus pembelian yang dipilih"""
        selected_item = self.pembelian_tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Silakan pilih pembelian yang akan dihapus!")
            return
            
        item = self.pembelian_tree.item(selected_item)
        pembelian_id = item['values'][0]
        
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus pembelian ini?"):
            self.cursor.execute("DELETE FROM pembelian WHERE id = ?", (pembelian_id,))
            self.conn.commit()
            self.load_pembelian_data()
            messagebox.showinfo("Sukses", "Pembelian berhasil dihapus!")
            
    def pembelian_form_window(self, title, data=None):
        """Window form untuk tambah/edit pembelian"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("400x450")
        window.configure(bg='#f0f8ff')
        window.resizable(False, False)
        
        # Title
        tk.Label(window, text=title, font=('Arial', 16, 'bold'), 
                bg='#f0f8ff', fg='#2c3e50').pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(window, bg='#f0f8ff')
        form_frame.pack(padx=30, pady=10, fill='both', expand=True)
        
        # Get obat list for dropdown
        self.cursor.execute("SELECT id, nama_obat FROM obat")
        obat_list = self.cursor.fetchall()
        
        # Obat selection
        tk.Label(form_frame, text="Pilih Obat:", font=('Arial', 11, 'bold'), 
                bg='#f0f8ff').pack(anchor='w', pady=(10, 0))
        
        obat_var = tk.StringVar()
        obat_combo = ttk.Combobox(form_frame, textvariable=obat_var, font=('Arial', 11), width=37)
        obat_combo['values'] = [f"{obat[0]} - {obat[1]}" for obat in obat_list]
        obat_combo.pack(pady=(5, 0), fill='x')
        
        # Other fields
        fields = [
            ("Nama Supplier:", "nama_supplier"),
            ("Jumlah:", "jumlah"),
            ("Harga Satuan:", "harga_satuan"),
            ("Tanggal Pembelian:", "tanggal_pembelian")
        ]
        
        entries = {}
        
        for i, (label, field) in enumerate(fields):
            tk.Label(form_frame, text=label, font=('Arial', 11, 'bold'), 
                    bg='#f0f8ff').pack(anchor='w', pady=(10, 0))
            
            entry = tk.Entry(form_frame, font=('Arial', 11), width=40)
            entry.pack(pady=(5, 0), fill='x')
            entries[field] = entry
        
        # Total harga (read-only)
        tk.Label(form_frame, text="Total Harga:", font=('Arial', 11, 'bold'), 
                bg='#f0f8ff').pack(anchor='w', pady=(10, 0))
        
        total_entry = tk.Entry(form_frame, font=('Arial', 11), width=40, state='readonly')
        total_entry.pack(pady=(5, 0), fill='x')
        
        # Calculate total when jumlah or harga_satuan changes
        def calculate_total(*args):
            try:
                jumlah = float(entries['jumlah'].get()) if entries['jumlah'].get() else 0
                harga_satuan = float(entries['harga_satuan'].get()) if entries['harga_satuan'].get() else 0
                total = jumlah * harga_satuan
                
                total_entry.config(state='normal')
                total_entry.delete(0, 'end')
                total_entry.insert(0, f"{total:,.2f}")
                total_entry.config(state='readonly')
            except ValueError:
                total_entry.config(state='normal')
                total_entry.delete(0, 'end')
                total_entry.insert(0, "0.00")
                total_entry.config(state='readonly')
        
        entries['jumlah'].bind('<KeyRelease>', calculate_total)
        entries['harga_satuan'].bind('<KeyRelease>', calculate_total)
        
        # Fill data if editing
        if data:
            # Find and select obat
            for i, (obat_id, obat_name) in enumerate(obat_list):
                if obat_name == data[1]:  # data[1] is obat name
                    obat_combo.current(i)
                    break
            
            # Fill other fields
            field_values = [data[2], data[3], data[4], data[6]]  # supplier, jumlah, harga_satuan, tanggal
            for i, field in enumerate(['nama_supplier', 'jumlah', 'harga_satuan', 'tanggal_pembelian']):
                entries[field].insert(0, str(field_values[i]))
            
            calculate_total()
        
        # Button frame
        btn_frame = tk.Frame(window, bg='#f0f8ff')
        btn_frame.pack(pady=20)
        
        def save_pembelian():
            # Validate input
            if not obat_var.get() or not all(entries[field].get().strip() for field in entries):
                messagebox.showerror("Error", "Semua field harus diisi!")
                return
                
            try:
                # Get obat ID
                obat_id = int(obat_var.get().split(' - ')[0])
                
                # Get values
                values = {field: entries[field].get().strip() for field in entries}
                
                # Validate numeric fields
                jumlah = int(values['jumlah'])
                harga_satuan = float(values['harga_satuan'])
                total_harga = jumlah * harga_satuan
                
                # Validate date format
                datetime.strptime(values['tanggal_pembelian'], '%Y-%m-%d')
                
                if data:  # Edit mode
                    self.cursor.execute("""
                        UPDATE pembelian SET id_obat=?, nama_supplier=?, jumlah=?, 
                        harga_satuan=?, total_harga=?, tanggal_pembelian=? WHERE id=?
                    """, (obat_id, values['nama_supplier'], jumlah, harga_satuan, 
                         total_harga, values['tanggal_pembelian'], data[0]))
                else:  # Add mode
                    self.cursor.execute("""
                        INSERT INTO pembelian (id_obat, nama_supplier, jumlah, 
                        harga_satuan, total_harga, tanggal_pembelian) VALUES (?, ?, ?, ?, ?, ?)
                    """, (obat_id, values['nama_supplier'], jumlah, harga_satuan, 
                         total_harga, values['tanggal_pembelian']))
                    
                    # Update stok obat
                    self.cursor.execute("UPDATE obat SET stok = stok + ? WHERE id = ?", (jumlah, obat_id))
                
                self.conn.commit()
                self.load_pembelian_data()
                window.destroy()
                messagebox.showinfo("Sukses", "Data pembelian berhasil disimpan!")
                
            except ValueError as e:
                messagebox.showerror("Error", "Format data tidak valid!\nJumlah harus berupa angka, Harga harus berupa angka, Tanggal format: YYYY-MM-DD")
            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
        
        tk.Button(btn_frame, text="💾 Simpan", command=save_pembelian,
                 font=('Arial', 11, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', padx=30, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Batal", command=window.destroy,
                 font=('Arial', 11, 'bold'), bg='#e74c3c', fg='white',
                 relief='flat', padx=30, pady=10).pack(side='left', padx=10)
        
    def show_penjualan(self):
        """Menampilkan data penjualan"""
        self.clear_content()
        
        # Title
        title = tk.Label(self.content_frame, text="💰 Data Penjualan", 
                        font=('Arial', 18, 'bold'), bg='#f0f8ff', fg='#2c3e50')
        title.pack(pady=(0, 20))
        
        # Button frame
        btn_frame = tk.Frame(self.content_frame, bg='#f0f8ff')
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(btn_frame, text="+ Tambah Penjualan", command=self.add_penjualan,
                 font=('Arial', 10, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="✏️ Edit Penjualan", command=self.edit_penjualan,
                 font=('Arial', 10, 'bold'), bg='#f39c12', fg='white',
                 relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🗑️ Hapus Penjualan", command=self.delete_penjualan,
                 font=('Arial', 10, 'bold'), bg='#e74c3c', fg='white',
                 relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        
        # Table frame
        table_frame = tk.Frame(self.content_frame, bg='white', relief='raised', bd=2)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        # Treeview
        columns = ('ID', 'Obat', 'Pegawai', 'Pembeli', 'Jumlah', 'Harga Satuan', 'Total', 'Tanggal')
        self.penjualan_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.penjualan_tree.heading(col, text=col)
            self.penjualan_tree.column(col, width=110)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.penjualan_tree.yview)
        self.penjualan_tree.configure(yscrollcommand=scrollbar.set)
        
        self.penjualan_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Load data
        self.load_penjualan_data()
        
    def load_penjualan_data(self):
        """Load data penjualan"""
        # Clear existing items
        for item in self.penjualan_tree.get_children():
            self.penjualan_tree.delete(item)
            
        # Get data from database with JOIN
        self.cursor.execute("""
            SELECT p.id, o.nama_obat, pg.nama_pegawai, p.nama_pembeli, p.jumlah, 
                   p.harga_satuan, p.total_harga, p.tanggal_penjualan
            FROM penjualan p
            JOIN obat o ON p.id_obat = o.id
            JOIN pegawai pg ON p.id_pegawai = pg.id
            ORDER BY p.id DESC
        """)
        
        for row in self.cursor.fetchall():
            self.penjualan_tree.insert('', 'end', values=row)
            
    def add_penjualan(self):
        """Tambah penjualan baru"""
        self.penjualan_form_window("Tambah Penjualan Baru")
        
    def edit_penjualan(self):
        """Edit penjualan yang dipilih"""
        selected_item = self.penjualan_tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Silakan pilih penjualan yang akan diedit!")
            return
            
        item = self.penjualan_tree.item(selected_item)
        values = item['values']
        self.penjualan_form_window("Edit Penjualan", values)
        
    def delete_penjualan(self):
        """Hapus penjualan yang dipilih"""
        selected_item = self.penjualan_tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Silakan pilih penjualan yang akan dihapus!")
            return
            
        item = self.penjualan_tree.item(selected_item)
        penjualan_id = item['values'][0]
        
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus penjualan ini?"):
            self.cursor.execute("DELETE FROM penjualan WHERE id = ?", (penjualan_id,))
            self.conn.commit()
            self.load_penjualan_data()
            messagebox.showinfo("Sukses", "Penjualan berhasil dihapus!")
            
    def penjualan_form_window(self, title, data=None):
        """Window form untuk tambah/edit penjualan"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("400x500")
        window.configure(bg='#f0f8ff')
        window.resizable(False, False)
        
        # Title
        tk.Label(window, text=title, font=('Arial', 16, 'bold'), 
                bg='#f0f8ff', fg='#2c3e50').pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(window, bg='#f0f8ff')
        form_frame.pack(padx=30, pady=10, fill='both', expand=True)
        
        # Get obat and pegawai lists for dropdown
        self.cursor.execute("SELECT id, nama_obat, harga_jual, stok FROM obat WHERE stok > 0")
        obat_list = self.cursor.fetchall()
        
        self.cursor.execute("SELECT id, nama_pegawai FROM pegawai")
        pegawai_list = self.cursor.fetchall()
        
        # Obat selection
        tk.Label(form_frame, text="Pilih Obat:", font=('Arial', 11, 'bold'), 
                bg='#f0f8ff').pack(anchor='w', pady=(10, 0))
        
        obat_var = tk.StringVar()
        obat_combo = ttk.Combobox(form_frame, textvariable=obat_var, font=('Arial', 11), width=37)
        obat_combo['values'] = [f"{obat[0]} - {obat[1]} (Rp {obat[2]:,.0f}) - Stok: {obat[3]}" for obat in obat_list]
        obat_combo.pack(pady=(5, 0), fill='x')
        
        # Pegawai selection
        tk.Label(form_frame, text="Pilih Pegawai:", font=('Arial', 11, 'bold'), 
                bg='#f0f8ff').pack(anchor='w', pady=(10, 0))
        
        pegawai_var = tk.StringVar()
        pegawai_combo = ttk.Combobox(form_frame, textvariable=pegawai_var, font=('Arial', 11), width=37)
        pegawai_combo['values'] = [f"{pegawai[0]} - {pegawai[1]}" for pegawai in pegawai_list]
        pegawai_combo.pack(pady=(5, 0), fill='x')
        
        # Other fields
        fields = [
            ("Nama Pembeli:", "nama_pembeli"),
            ("Jumlah:", "jumlah"),
            ("Tanggal Penjualan:", "tanggal_penjualan")
        ]
        
        entries = {}
        
        for i, (label, field) in enumerate(fields):
            tk.Label(form_frame, text=label, font=('Arial', 11, 'bold'), 
                    bg='#f0f8ff').pack(anchor='w', pady=(10, 0))
            
            entry = tk.Entry(form_frame, font=('Arial', 11), width=40)
            entry.pack(pady=(5, 0), fill='x')
            entries[field] = entry
        
        # Harga satuan (read-only)
        tk.Label(form_frame, text="Harga Satuan:", font=('Arial', 11, 'bold'), 
                bg='#f0f8ff').pack(anchor='w', pady=(10, 0))
        
        harga_entry = tk.Entry(form_frame, font=('Arial', 11), width=40, state='readonly')
        harga_entry.pack(pady=(5, 0), fill='x')
        
        # Total harga (read-only)
        tk.Label(form_frame, text="Total Harga:", font=('Arial', 11, 'bold'), 
                bg='#f0f8ff').pack(anchor='w', pady=(10, 0))
        
        total_entry = tk.Entry(form_frame, font=('Arial', 11), width=40, state='readonly')
        total_entry.pack(pady=(5, 0), fill='x')
        
        # Update harga when obat changes
        def update_harga(*args):
            if obat_var.get():
                try:
                    harga_jual = float(obat_var.get().split('(Rp ')[1].split(')')[0].replace(',', ''))
                    
                    harga_entry.config(state='normal')
                    harga_entry.delete(0, 'end')
                    harga_entry.insert(0, f"{harga_jual:,.2f}")
                    harga_entry.config(state='readonly')
                    
                    calculate_total()
                except:
                    pass
        
        obat_var.trace('w', update_harga)
        
        # Calculate total when jumlah changes
        def calculate_total(*args):
            try:
                jumlah = float(entries['jumlah'].get()) if entries['jumlah'].get() else 0
                harga_satuan = float(harga_entry.get().replace(',', '')) if harga_entry.get() else 0
                total = jumlah * harga_satuan
                
                total_entry.config(state='normal')
                total_entry.delete(0, 'end')
                total_entry.insert(0, f"{total:,.2f}")
                total_entry.config(state='readonly')
            except ValueError:
                total_entry.config(state='normal')
                total_entry.delete(0, 'end')
                total_entry.insert(0, "0.00")
                total_entry.config(state='readonly')
        
        entries['jumlah'].bind('<KeyRelease>', calculate_total)
        
        # Fill data if editing
        if data:
            # Find and select obat
            for i, obat in enumerate(obat_list):
                if obat[1] == data[1]:  # data[1] is obat name
                    obat_combo.current(i)
                    break
            
            # Find and select pegawai
            for i, pegawai in enumerate(pegawai_list):
                if pegawai[1] == data[2]:  # data[2] is pegawai name
                    pegawai_combo.current(i)
                    break
            
            # Fill other fields
            entries['nama_pembeli'].insert(0, str(data[3]))
            entries['jumlah'].insert(0, str(data[4]))
            entries['tanggal_penjualan'].insert(0, str(data[7]))
            
            update_harga()
        
        # Button frame
        btn_frame = tk.Frame(window, bg='#f0f8ff')
        btn_frame.pack(pady=20)
        
        def save_penjualan():
            # Validate input
            if not obat_var.get() or not pegawai_var.get() or not all(entries[field].get().strip() for field in entries):
                messagebox.showerror("Error", "Semua field harus diisi!")
                return
                
            try:
                # Get IDs
                obat_id = int(obat_var.get().split(' - ')[0])
                pegawai_id = int(pegawai_var.get().split(' - ')[0])
                
                # Get values
                values = {field: entries[field].get().strip() for field in entries}
                
                # Validate numeric fields
                jumlah = int(values['jumlah'])
                harga_satuan = float(harga_entry.get().replace(',', ''))
                total_harga = jumlah * harga_satuan
                
                # Check stok
                self.cursor.execute("SELECT stok FROM obat WHERE id = ?", (obat_id,))
                current_stok = self.cursor.fetchone()[0]
                
                if not data and jumlah > current_stok:
                    messagebox.showerror("Error", f"Stok tidak mencukupi! Stok tersedia: {current_stok}")
                    return
                
                # Validate date format
                datetime.strptime(values['tanggal_penjualan'], '%Y-%m-%d')
                
                if data:  # Edit mode
                    self.cursor.execute("""
                        UPDATE penjualan SET id_obat=?, id_pegawai=?, nama_pembeli=?, jumlah=?, 
                        harga_satuan=?, total_harga=?, tanggal_penjualan=? WHERE id=?
                    """, (obat_id, pegawai_id, values['nama_pembeli'], jumlah, harga_satuan, 
                         total_harga, values['tanggal_penjualan'], data[0]))
                else:  # Add mode
                    self.cursor.execute("""
                        INSERT INTO penjualan (id_obat, id_pegawai, nama_pembeli, jumlah, 
                        harga_satuan, total_harga, tanggal_penjualan) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (obat_id, pegawai_id, values['nama_pembeli'], jumlah, harga_satuan, 
                         total_harga, values['tanggal_penjualan']))
                    
                    # Update stok obat
                    self.cursor.execute("UPDATE obat SET stok = stok - ? WHERE id = ?", (jumlah, obat_id))
                
                self.conn.commit()
                self.load_penjualan_data()
                window.destroy()
                messagebox.showinfo("Sukses", "Data penjualan berhasil disimpan!")
                
            except ValueError as e:
                messagebox.showerror("Error", "Format data tidak valid!\nJumlah harus berupa angka, Tanggal format: YYYY-MM-DD")
            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
        
        tk.Button(btn_frame, text="💾 Simpan", command=save_penjualan,
                 font=('Arial', 11, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', padx=30, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Batal", command=window.destroy,
                 font=('Arial', 11, 'bold'), bg='#e74c3c', fg='white',
                 relief='flat', padx=30, pady=10).pack(side='left', padx=10)

def main():
    root = tk.Tk()
    app = ApotekSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()
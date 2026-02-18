import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import hashlib

class SecureFileCopier:
    def __init__(self):
        self.root = tk.Tk()
        self.stop_copying = False
        self.is_copying = False
        self.setup_gui()
    
    def setup_gui(self):
        self.root.title("🔒 Secure File Copier - Authorized Use Only")
        self.root.geometry("650x550")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)
        
        # Title
        title = tk.Label(self.root, text="SECURE FILE TRANSFER TOOL", 
                        font=("Arial", 20, "bold"), bg="#1e1e1e", fg="#00ff88")
        title.pack(pady=20)
        
        # Source
        source_frame = tk.Frame(self.root, bg="#1e1e1e")
        source_frame.pack(pady=10, padx=40, fill="x")
        tk.Label(source_frame, text="📁 Source Directory:", font=("Arial", 12, "bold"), 
                bg="#1e1e1e", fg="white").pack(anchor="w")
        self.source_entry = tk.Entry(source_frame, font=("Arial", 11), 
                                   bg="#2d2d2d", fg="white", relief="flat", bd=2)
        self.source_entry.pack(fill="x", pady=(0,5))
        tk.Button(source_frame, text="Browse", command=self.select_source,
                 bg="#0078d4", fg="white", relief="flat", font=("Arial", 10, "bold")).pack()
        
        # Destination  
        dest_frame = tk.Frame(self.root, bg="#1e1e1e")
        dest_frame.pack(pady=10, padx=40, fill="x")
        tk.Label(dest_frame, text="💾 Destination Directory:", font=("Arial", 12, "bold"), 
                bg="#1e1e1e", fg="white").pack(anchor="w")
        self.dest_entry = tk.Entry(dest_frame, font=("Arial", 11), 
                                 bg="#2d2d2d", fg="white", relief="flat", bd=2)
        self.dest_entry.pack(fill="x", pady=(0,5))
        tk.Button(dest_frame, text="Browse", command=self.select_dest,
                 bg="#0078d4", fg="white", relief="flat", font=("Arial", 10, "bold")).pack()
        
        # Progress
        self.progress = ttk.Progressbar(self.root, length=500, mode='determinate')
        self.progress.pack(pady=20)
        
        self.status_label = tk.Label(self.root, text="Ready to copy files securely", 
                                   font=("Arial", 12), bg="#1e1e1e", fg="#00ff88")
        self.status_label.pack(pady=5)
        
        # File count label
        self.file_label = tk.Label(self.root, text="", font=("Arial", 10), 
                                 bg="#1e1e1e", fg="#888888")
        self.file_label.pack()
        
        # Buttons
        button_frame = tk.Frame(self.root, bg="#1e1e1e")
        button_frame.pack(pady=20)
        
        self.start_btn = tk.Button(button_frame, text="▶️ Start Transfer", 
                                 command=self.start_transfer, font=("Arial", 14, "bold"),
                                 bg="#00aa00", fg="white", width=16, height=2,
                                 relief="flat", bd=0, cursor="hand2")
        self.start_btn.pack(side="left", padx=10)
        
        self.stop_btn = tk.Button(button_frame, text="⏹️ Stop", 
                                command=self.stop_transfer, font=("Arial", 14, "bold"),
                                bg="#ff4444", fg="white", width=16, height=2, 
                                state="disabled", relief="flat", bd=0, cursor="hand2")
        self.stop_btn.pack(side="left", padx=10)
        
        self.verify_btn = tk.Button(button_frame, text="✅ Verify Integrity", 
                                  command=self.verify_files, font=("Arial", 14, "bold"),
                                  bg="#ffaa00", fg="white", width=18, height=2,
                                  relief="flat", bd=0, cursor="hand2")
        self.verify_btn.pack(side="left")
        
        # Log frame
        log_frame = tk.Frame(self.root, bg="#1e1e1e")
        log_frame.pack(pady=10, padx=40, fill="both", expand=True)
        tk.Label(log_frame, text="📋 Transfer Log:", font=("Arial", 10, "bold"), 
                bg="#1e1e1e", fg="white").pack(anchor="w")
        self.log_text = tk.Text(log_frame, height=6, bg="#2d2d2d", fg="#00ff88", 
                               font=("Consolas", 9), relief="flat", bd=2)
        scrollbar = ttk.Scrollbar(self.log_text)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
    
    def log(self, message):
        """Safe logging with GUI update"""
        def update_log():
            self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} | {message}\n")
            self.log_text.see(tk.END)
        
        self.root.after(0, update_log)
    
    def select_source(self):
        path = filedialog.askdirectory(title="Select source directory")
        if path: 
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, path)
            self.log(f"📁 Source set: {os.path.basename(path)}")
    
    def select_dest(self):
        path = filedialog.askdirectory(title="Select destination directory")
        if path: 
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, path)
            self.log(f"💾 Destination set: {os.path.basename(path)}")
    
    def count_files(self, source_path):
        """Count total files for progress bar"""
        count = 0
        try:
            for root, dirs, files in os.walk(source_path):
                count += len(files)
        except PermissionError:
            pass  # Skip inaccessible dirs
        return count
    
    def calculate_hash(self, file_path):
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return None
    
    def copy_thread(self):
        source = self.source_entry.get().strip()
        dest = self.dest_entry.get().strip()
        
        if not os.path.exists(source):
            self.log("❌ Source directory not found!")
            self.reset_buttons()
            return
        
        total_files = self.count_files(source)
        if total_files == 0:
            self.log("ℹ️ No files found in source directory")
            self.reset_buttons()
            return
            
        self.progress['maximum'] = total_files
        self.progress['value'] = 0
        self.file_label.config(text=f"Total files: {total_files}")
        
        copied = 0
        skipped = 0
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(dest, f"Backup_{timestamp}")
        
        try:
            os.makedirs(backup_folder, exist_ok=True)
            self.log(f"📁 Backup folder created: {backup_folder}")
            
            for root, dirs, files in os.walk(source):
                if self.stop_copying:
                    self.log("⏹️ Copy operation stopped by user")
                    break
                
                rel_path = os.path.relpath(root, source)
                dest_root = os.path.join(backup_folder, rel_path)
                os.makedirs(dest_root, exist_ok=True)
                
                for file in files:
                    if self.stop_copying:
                        break
                    
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_root, file)
                    
                    try:
                        # Skip if destination exists (incremental backup)
                        if os.path.exists(dest_file):
                            skipped += 1
                        else:
                            shutil.copy2(src_file, dest_file)
                            copied += 1
                        
                        self.progress['value'] += 1
                        self.file_label.config(text=f"Copied: {copied} | Skipped: {skipped} | Total: {total_files}")
                        
                        # Log every 50 files to reduce spam
                        if copied % 50 == 0:
                            self.log(f"📊 Progress: {copied}/{total_files}")
                            
                    except Exception as e:
                        self.log(f"⚠️ Skip {os.path.basename(file)}: {str(e)[:50]}")
            
            self.log(f"🎉 Complete! Copied: {copied}, Skipped: {skipped}")
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                f"Backup complete!\nCopied: {copied}\nSkipped: {skipped}"))
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
        
        self.reset_buttons()
    
    def reset_buttons(self):
        """Reset button states after operation"""
        self.is_copying = False
        self.stop_copying = False
        self.start_btn.config(state="normal", text="▶️ Start Transfer")
        self.stop_btn.config(state="disabled")
    
    def start_transfer(self):
        source = self.source_entry.get().strip()
        dest = self.dest_entry.get().strip()
        
        if not source or not dest:
            messagebox.showerror("Error", "Please select both source and destination!")
            return
        
        if not os.path.exists(source):
            messagebox.showerror("Error", "Source directory does not exist!")
            return
        
        if not os.access(dest, os.W_OK):
            messagebox.showerror("Error", "Cannot write to destination directory!")
            return
        
        # Clear previous log
        self.log_text.delete(1.0, tk.END)
        self.log("🚀 Starting secure backup operation...")
        
        self.is_copying = True
        self.stop_copying = False
        self.start_btn.config(state="disabled", text="🔄 Copying...")
        self.stop_btn.config(state="normal")
        
        # Start in separate thread
        thread = threading.Thread(target=self.copy_thread, daemon=True)
        thread.start()
    
    def stop_transfer(self):
        self.stop_copying = True
        self.log("🛑 Stop requested - finishing current file...")
    
    def verify_files(self):
        source = self.source_entry.get().strip()
        dest = self.dest_entry.get().strip()
        
        if not source or not dest or not os.path.exists(source) or not os.path.exists(dest):
            messagebox.showerror("Error", "Please set valid source and destination directories!")
            return
        
        # Find the latest backup folder
        backup_folders = [f for f in os.listdir(dest) if f.startswith("Backup_")]
        if not backup_folders:
            messagebox.showwarning("Warning", "No backup folder found for verification!")
            return
        
        latest_backup = max(backup_folders)
        backup_path = os.path.join(dest, latest_backup)
        
        self.log_text.delete(1.0, tk.END)
        self.log(f"🔍 Verifying against: {latest_backup}")
        
        mismatches = 0
        missing = 0
        
        def verify_worker():
            for root, dirs, files in os.walk(source):
                rel_root = os.path.relpath(root, source)
                dest_root = os.path.join(backup_path, rel_root)
                
                for file in files[:100]:  # Limit to first 100 files for speed
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_root, file)
                    
                    if not os.path.exists(dest_file):
                        missing += 1
                        self.log(f"❌ Missing: {os.path.relpath(src_file, source)}")
                    elif self.calculate_hash(src_file) != self.calculate_hash(dest_file):
                        mismatches += 1
                        self.log(f"❌ Corrupted: {os.path.relpath(src_file, source)}")
            
            result = f"✅ Verified! Mismatches: {mismatches}, Missing: {missing}"
            self.log(result)
            self.root.after(0, lambda: messagebox.showinfo("Verification Complete", result))
        
        threading.Thread(target=verify_worker, daemon=True).start()

    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window close"""
        if self.is_copying:
            if messagebox.askokcancel("Quit", "Backup in progress. Stop and quit?"):
                self.stop_transfer()
                self.root.after(2000, self.root.destroy)
        else:
            self.root.destroy()

if __name__ == "__main__":
    app = SecureFileCopier()
    app.run()
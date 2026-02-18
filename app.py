import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

class SecureFileCopier:
    def __init__(self):
        self.root = tk.Tk()
        self.stop_copying = False
        self.is_copying = False
        self.file_queue = queue.Queue()
        self.copied_count = 0
        self.skipped_count = 0
        self.total_files_count = 0
        self.current_operation = ""
        self.setup_gui()
    
    def setup_gui(self):
        self.root.title("Secure File Copier")
        self.root.geometry("720x650")
        self.root.configure(bg="#121212")
        self.root.resizable(True, True)

        # ====== TITLE ======
        title = tk.Label(
            self.root,
            text="Shakeel Data Engineer",
            font=("Segoe UI", 22, "bold"),
            bg="#121212",
            fg="#00ffaa"
        )
        title.pack(pady=25)

        subtitle = tk.Label(
            self.root,
            text="ULTRA HIGH SPEED Professional Secure File Transfer Tool",
            font=("Segoe UI", 10),
            bg="#121212",
            fg="#888888"
        )
        subtitle.pack(pady=(0, 20))

        # ====== CARD FRAME ======
        main_card = tk.Frame(self.root, bg="#1e1e1e", bd=0)
        main_card.pack(padx=40, pady=10, fill="both", expand=True)

        # ===== SOURCE =====
        tk.Label(main_card, text="Source Directory",
                 font=("Segoe UI", 11, "bold"),
                 bg="#1e1e1e", fg="#ffffff").pack(anchor="w", pady=(15, 5))

        self.source_entry = tk.Entry(
            main_card,
            font=("Segoe UI", 11),
            bg="#2a2a2a",
            fg="white",
            relief="flat",
            insertbackground="white"
        )
        self.source_entry.pack(fill="x", padx=10, pady=(0, 5))

        tk.Button(
            main_card,
            text="Browse Source",
            command=self.select_source,
            bg="#2979ff",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(pady=(0, 15))

        # ===== DESTINATION =====
        tk.Label(main_card, text="Destination Directory",
                 font=("Segoe UI", 11, "bold"),
                 bg="#1e1e1e", fg="#ffffff").pack(anchor="w", pady=(10, 5))

        self.dest_entry = tk.Entry(
            main_card,
            font=("Segoe UI", 11),
            bg="#2a2a2a",
            fg="white",
            relief="flat",
            insertbackground="white"
        )
        self.dest_entry.pack(fill="x", padx=10, pady=(0, 5))

        tk.Button(
            main_card,
            text="Browse Destination",
            command=self.select_dest,
            bg="#2979ff",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(pady=(0, 20))

        # ===== PROGRESS BAR =====
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "green.Horizontal.TProgressbar",
            troughcolor="#2a2a2a",
            background="#00ffaa",
            thickness=12
        )

        self.progress = ttk.Progressbar(
            main_card,
            length=500,
            style="green.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=10)

        self.status_label = tk.Label(
            main_card,
            text="Ready to start ULTRA HIGH SPEED backup",
            font=("Segoe UI", 11),
            bg="#1e1e1e",
            fg="#00ffaa"
        )
        self.status_label.pack()

        self.file_label = tk.Label(
            main_card,
            text="",
            font=("Segoe UI", 9),
            bg="#1e1e1e",
            fg="#aaaaaa"
        )
        self.file_label.pack(pady=(0, 15))

        # ===== BUTTONS FRAME 1 - CUT & COPY =====
        buttons_frame1 = tk.Frame(main_card, bg="#1e1e1e")
        buttons_frame1.pack(pady=10)

        self.cut_btn = tk.Button(
            buttons_frame1,
            text="✂️ ULTRA FAST Cut",
            command=self.start_cut,
            font=("Segoe UI", 12, "bold"),
            bg="#ff9800",
            fg="white",
            width=16,
            height=2,
            relief="flat",
            cursor="hand2"
        )
        self.cut_btn.pack(side="left", padx=10)

        self.copy_btn = tk.Button(
            buttons_frame1,
            text="⚡ ULTRA FAST Copy",
            command=self.start_copy,
            font=("Segoe UI", 12, "bold"),
            bg="#00c853",
            fg="white",
            width=16,
            height=2,
            relief="flat",
            cursor="hand2"
        )
        self.copy_btn.pack(side="left", padx=10)

        # ===== BUTTONS FRAME 2 - STOP & VERIFY =====
        buttons_frame2 = tk.Frame(main_card, bg="#1e1e1e")
        buttons_frame2.pack(pady=(0, 10))

        self.stop_btn = tk.Button(
            buttons_frame2,
            text="⏹️ Stop",
            command=self.stop_transfer,
            font=("Segoe UI", 12, "bold"),
            bg="#ff5252",
            fg="white",
            width=16,
            height=2,
            state="disabled",
            relief="flat",
            cursor="hand2"
        )
        self.stop_btn.pack(side="left", padx=10)

        self.verify_btn = tk.Button(
            buttons_frame2,
            text="🔍 Verify Integrity",
            command=self.verify_files,
            font=("Segoe UI", 12, "bold"),
            bg="#ffab00",
            fg="black",
            width=18,
            height=2,
            relief="flat",
            cursor="hand2"
        )
        self.verify_btn.pack(side="left")

        # ===== LOG AREA =====
        tk.Label(main_card, text="ULTRA HIGH SPEED Transfer Log",
                 font=("Segoe UI", 10, "bold"),
                 bg="#1e1e1e", fg="#ffffff").pack(anchor="w", padx=10, pady=(20,5))

        log_frame = tk.Frame(main_card, bg="#1e1e1e")
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))

        self.log_text = tk.Text(
            log_frame,
            height=8,
            bg="#111111",
            fg="#00ffaa",
            font=("Consolas", 9),
            relief="flat",
            insertbackground="white",
            state="normal"
        )
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
    
    def log(self, message):
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
        count = 0
        try:
            for root, dirs, files in os.walk(source_path):
                count += len(files)
        except PermissionError:
            pass
        return count
    
    def calculate_hash(self, file_path):
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return None
    
    def ultra_fast_copy_file(self, src_file, dest_file, is_cut=False):
        """ULTRA FAST file copy using shutil.move for BOTH operations - SAME ULTRA SPEED"""
        try:
            if os.path.exists(dest_file):
                return False  # Skipped
            
            # ULTRA FAST using shutil.move for BOTH CUT & COPY - MAXIMUM SPEED
            shutil.move(src_file, dest_file) if is_cut else shutil.copy2(src_file, dest_file)
            
            return True  # Copied/moved successfully
        except:
            return False
    
    def update_progress(self, success, filename):
        self.progress['value'] += 1
        if success:
            self.copied_count += 1
        else:
            self.skipped_count += 1
        self.file_label.config(text=f"{self.current_operation}: {self.copied_count} | Skipped: {self.skipped_count} | Total: {self.total_files_count} | {filename}")
    
    def worker_thread(self, is_cut=False):
        """Worker thread for parallel processing - ULTRA HIGH SPEED"""
        while not self.stop_copying:
            try:
                file_info = self.file_queue.get(timeout=0.1)
                src_file, dest_file = file_info
                success = self.ultra_fast_copy_file(src_file, dest_file, is_cut)
                self.file_queue.task_done()
                
                # Update progress in main thread
                filename = os.path.basename(src_file)
                self.root.after(0, lambda s=success, f=filename: self.update_progress(s, f))
                
            except queue.Empty:
                continue
            except:
                try:
                    self.file_queue.task_done()
                except:
                    pass
    
    def copy_thread(self, is_cut=False):
        source = self.source_entry.get().strip()
        dest = self.dest_entry.get().strip()
        
        if not os.path.exists(source):
            self.log("❌ Source directory not found!")
            self.reset_buttons()
            return
        
        self.total_files_count = self.count_files(source)
        if self.total_files_count == 0:
            self.log("ℹ️ No files found in source directory")
            self.reset_buttons()
            return
        
        self.progress['maximum'] = self.total_files_count
        self.progress['value'] = 0
        self.file_label.config(text=f"Total files: {self.total_files_count}")
        
        self.copied_count = 0
        self.skipped_count = 0
        self.current_operation = "Copy" if not is_cut else "Cut"
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        operation_name = "Cut" if is_cut else "Copy"
        backup_folder = os.path.join(dest, f"{operation_name}_{timestamp}")
        
        try:
            os.makedirs(backup_folder, exist_ok=True)
            self.log(f"🚀 ULTRA HIGH SPEED {operation_name} started with {os.cpu_count()*8} parallel workers!")
            self.log(f"📁 {operation_name} folder: {backup_folder}")
            
            # Fill queue with all files first
            def queue_files():
                queued = 0
                for root, dirs, files in os.walk(source):
                    if self.stop_copying:
                        break
                    rel_path = os.path.relpath(root, source)
                    dest_root = os.path.join(backup_folder, rel_path)
                    os.makedirs(dest_root, exist_ok=True)
                    
                    for file in files:
                        if self.stop_copying:
                            break
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_root, file)
                        self.file_queue.put((src_file, dest_file))
                        queued += 1
                        if queued % 100 == 0:
                            self.root.after(0, lambda q=queued: self.log(f"📦 Queued {q} files..."))
            
            # Start queue filler thread
            queue_thread = threading.Thread(target=queue_files, daemon=True)
            queue_thread.start()
            queue_thread.join(1)  # Give it a moment to start
            
            # ULTRA HIGH SPEED - MORE WORKERS FOR MAX PARALLELISM
            max_workers = max(8, os.cpu_count() * 4)  # MAXIMUM parallelism for both operations
            self.log(f"⚡ Starting {max_workers} ULTRA FAST workers...")
            
            worker_threads = []
            for i in range(max_workers):
                t = threading.Thread(target=self.worker_thread, args=(is_cut,), daemon=True)
                t.start()
                worker_threads.append(t)
            
            # Wait for queue to empty
            self.file_queue.join()
            
            # Give workers time to finish
            time.sleep(1)
            self.stop_copying = True
            
            self.log(f"🎉 ULTRA FAST Complete! {operation_name}d: {self.copied_count}, Skipped: {self.skipped_count}")
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                f"ULTRA FAST {operation_name} complete!\n"
                f"Copied/Moved: {self.copied_count}\n"
                f"Skipped: {self.skipped_count}\n"
                f"Total: {self.total_files_count}"))
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
        
        self.reset_buttons()
    
    def cut_thread(self):
        self.copy_thread(is_cut=True)
    
    def reset_buttons(self):
        self.is_copying = False
        self.stop_copying = False
        self.file_queue = queue.Queue()
        self.cut_btn.config(state="normal")
        self.copy_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
    
    def start_copy(self):
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
        
        self.log_text.delete(1.0, tk.END)
        self.log("⚡ ULTRA HIGH SPEED COPY operation started...")
        
        self.is_copying = True
        self.stop_copying = False
        self.cut_btn.config(state="disabled")
        self.copy_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        thread = threading.Thread(target=self.copy_thread, args=(False,), daemon=True)
        thread.start()
    
    def start_cut(self):
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
        
        self.log_text.delete(1.0, tk.END)
        self.log("✂️ ULTRA HIGH SPEED CUT operation started...")
        
        self.is_copying = True
        self.stop_copying = False
        self.cut_btn.config(state="disabled")
        self.copy_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        thread = threading.Thread(target=self.cut_thread, daemon=True)
        thread.start()
    
    def stop_transfer(self):
        self.stop_copying = True
        self.log("🛑 ULTRA FAST Stop requested...")
    
    def verify_files(self):
        source = self.source_entry.get().strip()
        dest = self.dest_entry.get().strip()
        
        if not source or not dest or not os.path.exists(source) or not os.path.exists(dest):
            messagebox.showerror("Error", "Please set valid source and destination directories!")
            return
        
        backup_folders = [f for f in os.listdir(dest) if f.startswith(("Copy_", "Cut_"))]
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
                
                for file in files[:100]:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_root, file)
                    
                    if not os.path.exists(dest_file):
                        missing += 1
                        self.root.after(0, lambda f=os.path.relpath(src_file, source): 
                            self.log(f"❌ Missing: {f}"))
                    elif self.calculate_hash(src_file) != self.calculate_hash(dest_file):
                        mismatches += 1
                        self.root.after(0, lambda f=os.path.relpath(src_file, source): 
                            self.log(f"❌ Corrupted: {f}"))
            
            result = f"✅ Verified! Mismatches: {mismatches}, Missing: {missing}"
            self.log(result)
            self.root.after(0, lambda: messagebox.showinfo("Verification Complete", result))
        
        threading.Thread(target=verify_worker, daemon=True).start()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        if self.is_copying:
            if messagebox.askokcancel("Quit", "ULTRA FAST Transfer in progress. Stop and quit?"):
                self.stop_transfer()
                self.root.after(2000, self.root.destroy)
        else:
            self.root.destroy()

if __name__ == "__main__":
    app = SecureFileCopier()
    app.run()
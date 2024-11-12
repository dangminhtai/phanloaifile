import os
import shutil
import json
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox

# Đặt đường dẫn lưu trữ backup trong thư mục tạm thời
backup_temp_dir = tempfile.gettempdir()
backup_file_name = "backup.json"
backup_file_path = os.path.join(backup_temp_dir, backup_file_name)

def load_backup(backup_file):
    """Tải dữ liệu từ tệp JSON nếu có"""
    if os.path.exists(backup_file):
        try:
            with open(backup_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu từ tệp: {e}")
    return []

def save_backup(data, backup_file):
    """Lưu dữ liệu phân loại vào tệp JSON trong thư mục tạm"""
    try:
        with open(backup_file, 'w') as f:
            json.dump(data, f)
        print(f"Lưu backup vào: {backup_file}")
    except Exception as e:
        print(f"Lỗi khi ghi tệp: {e}")
        messagebox.showerror("Lỗi", "Không thể ghi vào tệp backup.json")

def choose_folder():
    folder_selected = filedialog.askdirectory(title="Chọn thư mục đầu vào")
    if folder_selected:
        entry_folder.delete(0, tk.END)
        entry_folder.insert(0, folder_selected)

def unique_name(destination, filename):
    """Tạo tên tệp duy nhất nếu tệp đã tồn tại"""
    name, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(destination, filename)):
        filename = f"{name}({counter}){ext}"
        counter += 1
    return filename

def classify_files():
    input_folder = entry_folder.get()
    if not input_folder:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn thư mục đầu vào!")
        return

    output_folder = os.path.join(input_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    file_backup = []

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if root.startswith(output_folder):
                continue  # Bỏ qua thư mục output trong quá trình duyệt

            ext = os.path.splitext(file)[1][1:].upper()  # Lấy đuôi file viết hoa
            if ext:
                ext_folder = os.path.join(output_folder, ext)
            else:
                ext_folder = os.path.join(output_folder, "NO_EXTENSION")

            os.makedirs(ext_folder, exist_ok=True)

            source_path = os.path.join(root, file)
            unique_filename = unique_name(ext_folder, file)
            dest_path = os.path.join(ext_folder, unique_filename)

            # Lưu thông tin vào file_backup
            file_backup.append({"original": source_path, "moved": dest_path})

            shutil.move(source_path, dest_path)

    # Lưu trạng thái phân loại vào tệp JSON trong thư mục tạm
    save_backup(file_backup, backup_file_path)

    # Xóa các thư mục con trong thư mục gốc (ngoại trừ thư mục 'output')
    for dir in os.listdir(input_folder):
        dir_path = os.path.join(input_folder, dir)
        if os.path.isdir(dir_path) and dir != "output":
            shutil.rmtree(dir_path)

    messagebox.showinfo("Hoàn tất", f"Phân loại tệp đã hoàn tất trong thư mục: {output_folder}")

def undo():
    input_folder = entry_folder.get()
    if not input_folder:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn thư mục đầu vào!")
        return

    output_folder = os.path.join(input_folder, "output")

    file_backup = load_backup(backup_file_path)
    if not file_backup:
        messagebox.showwarning("Cảnh báo", "Không có thao tác nào để hoàn tác!")
        return

    for entry in file_backup:
        original_path = entry["original"]
        moved_path = entry["moved"]

        if os.path.exists(moved_path):
            dest_folder = os.path.dirname(original_path)
            os.makedirs(dest_folder, exist_ok=True)
            shutil.move(moved_path, original_path)

    # Xóa các thư mục con trong output nhưng giữ lại thư mục 'output' chính
    for dir in os.listdir(output_folder):
        dir_path = os.path.join(output_folder, dir)
        if os.path.isdir(dir_path) and dir != "output":
            shutil.rmtree(dir_path)

    open(backup_file_path, 'w').close()  # Xóa nội dung của backup.json
    messagebox.showinfo("Hoàn tác", "Thao tác phân loại đã được hoàn tác thành công.")

# Giao diện
root = tk.Tk()
root.title("Phân loại tệp theo đuôi")

label_folder = tk.Label(root, text="Chọn thư mục đầu vào:")
label_folder.pack(pady=5)

entry_folder = tk.Entry(root, width=50)
entry_folder.pack(pady=5)

btn_choose_folder = tk.Button(root, text="Chọn thư mục", command=choose_folder)
btn_choose_folder.pack(pady=5)

btn_classify = tk.Button(root, text="Phân loại", command=classify_files)
btn_classify.pack(pady=5)

btn_undo = tk.Button(root, text="Undo", command=undo)
btn_undo.pack(pady=20)

root.mainloop()

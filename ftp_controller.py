import os
from os import listdir
from os.path import isfile, join
import shutil
import sys
from ftplib import FTP


class ftp_controller:  
    #/!\ Although the comments and variable names say 'file_name'/'file_anything' it inculdes folders also
    #Some functions in this class has no exception handling, it has to be done outside

    def __init__(self):
        #List to store file search and search keywords (Danh sách để lưu file tìm kiếm và từ khóa tìm kiếm)
        self.search_file_list = []
        self.detailed_search_file_list = []
        self.keyword_list = []

        #Variable to hold the max no character name in file list (used for padding in GUIs) (Biến để giữ tối đa không có tên ký tự trong danh sách tệp (được sử dụng để đệm trong GUI))
        self.max_len = 0

        self.max_len_name = ''

        #Variable to tell weather hidden files are enabled (Biến để cho biết thời tiết các tệp ẩn được bật)
        self.hidden_files = False

        #Variable to store the platform the server is running on (Biến để lưu platform của server đang chạy)
        self.server_platform = 'Linux'  

    def connect_to(self, host, username = ' ', password = ' ', port = 21):  
        self.ftp = FTP()  
        self.ftp.connect(host, port) 
        self.ftp.login(username, password)

    def toggle_hidden_files(self):
        self.hidden_files = not self.hidden_files 

    def get_detailed_file_list(self, ignore_hidden_files_flag = False):
        files = []
        def dir_callback(line):
            if(self.server_platform != 'Linux'):
                files.append(line)
                return
            if(self.hidden_files is True or line.split()[8][0] is not '.') or ignore_hidden_files_flag == True:
                files.append(line)
        self.ftp.dir(dir_callback)
        return files

    def get_file_list(self, detailed_file_list):
        self.max_len = 0
        self.max_len_name = ''
        file_list = []
        for x in detailed_file_list:
            #Remove details and append only the file name (xóa detail và chỉ còn tên file)
            if(self.server_platform == 'Linux'):
                name = self.get_properties(x)[0]
            file_list.append(name)
            if(len(name) > self.max_len):
                self.max_len = len(name)
                self.max_len_name = name
        return file_list
    
    def get_search_file_list(self):
        self.max_len = 0
        self.max_len_name = ''
        for name in self.search_file_list:
            if(len(name) > self.max_len):
                self.max_len = len(name)
                self.max_len_name = name
        return self.search_file_list
   
    def is_there(self, path):
        try:
            self.ftp.sendcmd('MLST '+path)
            return True
        except:
            return False

    def upload_file(self, file_name, file_size, status_command, replace_command):
        def update_progress(data):
            self.bytes_uploaded += int(sys.getsizeof(data))
            status_command(file_name, str(min(round((self.bytes_uploaded/file_size) * 100, 8), 100))+'%')
        #Variable to keep trak of number of bytes uploaded (biến theo dõi số lượng byte được tải lên)
        self.bytes_uploaded = 0
        #Check if the file is already present in ftp server (kiểm tra xem file đã có trong ftp server chưa)
        if(self.is_there(file_name)):
            if(replace_command(file_name, 'File exists in destination folder') is False):
                return
        #Try to open file, if fails return (thử mở file, nếu không được thì return)
        try:
            file_to_up = open(file_name, 'rb')
        except:
            status_command(file_name, 'Failed to open file')
            return
        #Try to upload file (thử upload file)
        try:
            status_command(file_name, 'Uploading')
            self.ftp.storbinary('STOR '+file_name, file_to_up, 8192, update_progress)
            status_command(None, 'newline')
        except:
            status_command(file_name, 'Upload failed')
            return
        #Close file (đóng file)
        file_to_up.close()

    def upload_dir(self, dir_name, status_command, replace_command):
        #Change to directory (chuyển đến thư mục)
        os.chdir(dir_name)
        #Create directory in server and go inside (tạo thư mục trên server và vào trong thư mục)
        try:
            if(not self.is_there(dir_name)):
                self.ftp.mkd(dir_name)
                status_command(dir_name, 'Creating directory')
            else:
                status_command(dir_name, 'Directory exists')
            self.ftp.cwd(dir_name)
        except:
            status_command(dir_name, 'Failed to create directory')
            return
        #Cycle through items (duyệt các file trong thư mục)
        for filename in os.listdir():
            #If file upload (nếu là file upload)
            if(isfile(filename)):
                self.upload_file(filename, os.path.getsize(filename), status_command, replace_command)
            #If directory, recursive upload it (nếu là thư mục, đệ quy upload nó)
            else:
                self.upload_dir(filename, status_command, replace_command)
                
        #Got to parent directory (đã đến thư mục mẹ)
        self.ftp.cwd('..')
        os.chdir('..')

    def download_file(self, ftp_file_name, file_size, status_command, replace_command):
        #Function for updating status and writing to file (hàm để cập nhật status và ghi vào file)
        def write_file(data):
            self.bytes_downloaded += int(sys.getsizeof(data))
            status_command(ftp_file_name, str(min(round((self.bytes_downloaded/file_size) * 100, 8), 100))+'%')
            file_to_down.write(data)
        #Variable to keep track of total bytes downloaded (biến theo dõi tổng số byte được download)
        self.bytes_downloaded = 0
        #Check if the file is already present in local directory (kiểm tra xem file đã có trong local chưa)
        if(isfile(ftp_file_name)):
            if(replace_command(ftp_file_name, 'File exists in destination folder') is False):
                return
        #Try to open file, if fails return (thử mở file, nếu không được thì return)
        try:
            file_to_down = open(ftp_file_name, 'wb')
        except:
            status_command(ftp_file_name, 'Failed to create file')
            return
        #Try to upload file (thủ upload file)
        try:
            status_command(ftp_file_name, 'Downloading')
            self.ftp.retrbinary('RETR '+ftp_file_name, write_file)
            status_command(None, 'newline')
        except:
            status_command(ftp_file_name, 'Download failed')
        #Close file (đóng file)
        file_to_down.close()

    def download_dir(self, ftp_dir_name, status_command, replace_command):
        #Create local directory (tạo thư mục local)       
        try:
            if(not os.path.isdir(ftp_dir_name)):
                os.makedirs(ftp_dir_name)
                status_command(ftp_dir_name, 'Created local directory')
            else:
                status_command(ftp_dir_name, 'Local directory exists')
            os.chdir(ftp_dir_name)
        except:
            status_command(ftp_dir_name, 'Failed to create local directory')
            return
        #Go into the ftp directory (chuyển đến thư mục ftp)
        self.ftp.cwd(ftp_dir_name)
        #Get file lists (lấy danh sách các file)
        detailed_file_list = self.get_detailed_file_list(True)
        file_list = self.get_file_list(detailed_file_list)
        for file_name, file_details in zip(file_list, detailed_file_list):
            #If directory (nếu là thư mục)
            if(self.is_dir(file_details)):
                self.download_dir(file_name, status_command, replace_command)
            #If file (nếu là file)
            else:
                self.download_file(file_name, int(self.get_properties(file_details)[3]), status_command, replace_command)
        #Got to parent directory (đã đến thư mục mẹ)
        self.ftp.cwd('..')
        os.chdir('..')

    def mkd(self, name):
        self.ftp.mkd(name)

    def pwd(self):
        return(self.ftp.pwd())

    def get_properties(self, file_details):
        if(self.server_platform == 'Linux'):
            details_list = file_details.split()
            #Get file attributes (lấy các thuộc tính file)
            file_attribs = details_list[0]
            #Get date modified (lấy ngày sửa đổi)
            date_modified = ' '.join(details_list[5:8])
            #Remove the path from the name (xóa đường dẫn khỏi tên)
            file_name = ' '.join(details_list[8:])
            #Get size if it is not a directory (lấy size nếu nó không phải là thư mục)
            if('d' not in file_details[0]):
                file_size = details_list[4]
                return [file_name, file_attribs, date_modified, file_size]
            else:
                return [file_name, file_attribs, date_modified]

    def is_dir(self, file_details):
        if(self.server_platform == 'Linux'):
            return 'd' in file_details[0]
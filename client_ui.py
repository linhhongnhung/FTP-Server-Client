import os
from os.path import isfile, join
import threading
import queue
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import PhotoImage
from turtle import bgcolor, fillcolor
from ftp_controller import *
import toolbar as ToolbarButton
import platform
if(platform.system() is 'Windows'):
    import ctypes


class app:
    def __init__(self, master):
        #/!\ Although the comments and variable names say 'file_list', or 'items' it inculdes folders also

        #Cell width of each cell (chiều rộng của mỗi ô)
        self.cell_width = 190

        #List to store all item names (including folders) that are currently being displayed and their details (danh sách lưu tất cả tên mục, folder đang hiển thị và chi tiết của nó)
        self.file_list = []
        self.detailed_file_list = []
        #An index that points to current file that the mouse is pointing (một chỉ mục trỏ đến tệp hiện tại mà con chuột trỏ vào)
        self.current_file_index = 0

        #Variables for drawing and storing cursor position (các biến để vẽ và lưu vị trí chuột)
        self.mouse_x = 0
        self.mouse_y = 0
        self.max_width = 0

        #Variable to store which cell cursor is currently pointing (biến để lưu con trỏ ô hiện đang trỏ vào)
        self.x_cell_pos = 0
        self.y_cell_pos = 0

        #A dictionary to store indices and highlight rectangle references of selected files (một thư mục để lưu các chỉ số và đánh dấu các tham chiếu hình chữ nhật của các file đã chọn)
        self.selected_file_indices = {}

        #A list to hold files that have been droped into the window (danh sách lưu giữ các file đã được thả vào cửa sổ )
        self.dnd_file_list = []

        #Things in the clipboard (những thứ trong bộ nhớ tạm)
        self.cut = False
        self.copy = False
        self.clipboard_file_list = []
        self.clipboard_path_list = []
        self.detailed_clipboard_file_list = []

        #Variable to store start cell position of drag select (biến để lưu vị trí ô bắt đầu của kéo chọn)
        self.start_x = 0
        self.start_y = 0

        #Variable to tell weather to change status, if false the current message will stay on status bar and status bar will ignore other status messages (biến cho biết chế độ thay đổi trạng thái , nếu sai thông báo hiện tại sẽ ở trên thanh trạng thái và thanh trạng thái sẽ bỏ qua các thông báo trạng thái khác)
        self.change_status = True

        #Variable to tell replace all has been selected (biến cho biết thay thế tất cả đã được chọn)
        # self.replace_all = Falseer

        #Variable to tell skip all has been selected (biến cho biết bỏ qua tất cả đã được chọn)
        self.skip_all = False

        #Variable to tell weather a search has been performes (biến cho biết chế độ một tìm kiếm đã được thực hiện)
        self.search_performed = False

        #Variable to tell weather hidden file are enabled (biến cho biết chế độ các file ẩn đã được bật)
        self.hidden_files = False

        #Variable to tell a thread weather to replace a file (biến cho biết một luồng chế độ để thay thế một tệp)
        self.replace_flag = False

        #For thread syncrhoniztion (để đồng bộ hóa luồng)
        self.thread_lock = threading.Lock()

        #Save reference to the window (lưu tham chiếu đến cửa sổ)
        self.master = master

        #Save reference to ftpcontroller (lưu tham chiếu đến ftpcontroller)
        # self.ftpController = ftp_controller()
 
        #Set window title and size (đặt tiêu đề và kích thước cửa sổ)
        master.wm_title('FTP Client')
        master.minsize(width = 860, height = 560)

        #Variable for holding the font (biến để đặt font chữ)
        self.default_font = font.nametofont("TkDefaultFont")

        #Variable to tell weather to displat updatin file list dialog (biến cho biết chế độ để hiển thị hộp thoại cập nhật danh sách tệp)
        self.float_dialog_destroy = False

        #Create frame for toolbar buttons (tạo frame cho các nút thanh công cụ)
        self.toolbar = ttk.Frame(master) # self.toolbar = ttk.Frame(master, style='Frame1.TFrame')
        self.toolbar.pack(fill = X)

        #Create frame for text fields (tạo frame cho trường văn bản)
        self.entry_bar = ttk.Frame(master)
        self.entry_bar.pack(fill = X)     

        #Create frame for canvas and scrollbar (tạo frame cho canvas và thanh cuộn)
        self.pad_frame = ttk.Frame(master)
        self.pad_frame.pack(fill = BOTH, expand = True)       
        self.canvas_frame = ttk.Frame(self.pad_frame, relief = 'groove', border = 1)
        self.canvas_frame.pack(fill = BOTH, expand = True, padx = 5, pady = 3)

        #Variables to kepp track of wain frame and animation (các biến để theo dõi wain frame và anmation)
        self.wait_anim = False
        self.wait_frame_index = 1
        self.continue_wait = False

        #Load all icons (load tất cả icon)
        self.connect_icon = PhotoImage(file='Icons/connect_big.png')
        self.upload_icon = PhotoImage(file='Icons/upload_big.png')
        self.download_icon = PhotoImage(file='Icons/download_big.png')
        self.newfolder_icon = PhotoImage(file='Icons/newfolder_big.png')
        self.up_icon = PhotoImage(file='Icons/up_big.png')
        self.info_icon = PhotoImage(file='Icons/info_big.png')
        self.delete_icon = PhotoImage(file='Icons/delete_big.png')
        self.properties_icon = PhotoImage(file='Icons/properties_big.png')
        self.cut_icon = PhotoImage(file='Icons/cut_big.png')
        self.copy_icon = PhotoImage(file='Icons/copy_big.png')
        self.paste_icon = PhotoImage(file='Icons/paste_big.png')
        self.permissions_icon = PhotoImage(file='Icons/permissions_big.png')
        self.folder_icon = PhotoImage(file='Icons/folder_big.png')
        self.textfile_icon = PhotoImage(file='Icons/textfile_big.png')
        self.console_icon = PhotoImage(file='Icons/console_big.png')
        self.search_icon = PhotoImage(file='Icons/search_big.png')
        self.rename_icon = PhotoImage(file='Icons/rename_big.png')
        self.whipFTP_icon = PhotoImage(file='Icons/whipFTP_large.png')
        self.goto_icon = PhotoImage(file='Icons/gotopath_big.png')

        #Load glow version of icons
        self.connect_glow_icon = PhotoImage(file='Icons_glow/connect_big_glow.png')
        self.upload_glow_icon = PhotoImage(file='Icons_glow/upload_big_glow.png')
        self.download_glow_icon = PhotoImage(file='Icons_glow/download_big_glow.png')
        self.newfolder_glow_icon = PhotoImage(file='Icons_glow/newfolder_big_glow.png')
        self.up_glow_icon = PhotoImage(file='Icons_glow/up_big_glow.png')
        self.info_glow_icon = PhotoImage(file='Icons_glow/info_big_glow.png')
        self.delete_glow_icon = PhotoImage(file='Icons_glow/delete_big_glow.png')
        self.properties_glow_icon = PhotoImage(file='Icons_glow/properties_big_glow.png')
        self.cut_glow_icon = PhotoImage(file='Icons_glow/cut_big_glow.png')
        self.copy_glow_icon = PhotoImage(file='Icons_glow/copy_big_glow.png')
        self.paste_glow_icon = PhotoImage(file='Icons_glow/paste_big_glow.png')
        self.console_glow_icon = PhotoImage(file='Icons_glow/console_big_glow.png')
        self.search_glow_icon = PhotoImage(file='Icons_glow/search_big_glow.png')
        self.whipFTP_glow_icon = PhotoImage(file='Icons_glow/whipFTP_large_glow.png')
        self.dnd_glow_icon = PhotoImage(file='Icons_glow/upload_large_glow.png')
        self.goto_glow_icon = PhotoImage(file='Icons_glow/gotopath_big_glow.png')

        #Load icons from the wait animations
        self.wait_frames = []
        self.wait_frames.append(PhotoImage(file='Icons_glow/wait_anim_frame_one.png'))
        self.wait_frames.append(PhotoImage(file='Icons_glow/wait_anim_frame_two.png'))
        self.wait_frames.append(PhotoImage(file='Icons_glow/wait_anim_frame_three.png'))
        self.wait_frames.append(PhotoImage(file='Icons_glow/wait_anim_frame_four.png'))
        self.problem_icon = PhotoImage(file='Icons_glow/problem.png')

        #Set window icon (đặt icon cho window)
        self.master.iconphoto(True, self.whipFTP_icon)

        #Create the connect button (tạo nút connect)
        self.connect_button = ToolbarButton.Button(self.toolbar, image = self.connect_icon, image_hover = self.connect_glow_icon, command = self.connect_to_ftp)
        self.connect_button.pack(side = 'left', padx = 5)
        #Create the newfolder button (tạo nút newfolder)
        self.newfolder_button = ToolbarButton.Button(self.toolbar, image = self.newfolder_icon, image_hover = self.newfolder_glow_icon, command = self.create_dir_window)
        self.newfolder_button.pack(side = 'left', padx = 5)
        #Create the upload button (tạo nút upload)
        self.upload_button = ToolbarButton.Button(self.toolbar, image = self.upload_icon, image_hover = self.upload_glow_icon, command = self.upload_window)
        self.upload_button.pack(side = 'left', padx = 5)
        #Create the download button (tạo nút download)
        self.download_button = ToolbarButton.Button(self.toolbar, image = self.download_icon, image_hover = self.download_glow_icon, command = self.download_window)
        self.download_button.pack(side = 'left', padx = 5)
        #Create the up-directory button (tạo nút quay lại thư mục)
        self.up_button = ToolbarButton.Button(self.toolbar, image = self.up_icon, image_hover = self.up_glow_icon, command = self.dir_up)
        self.up_button.pack(side = 'right', padx = 5)
        #Create the properties button (tạo nút xem thuộc tính)
        self.properties_button = ToolbarButton.Button(self.toolbar, image = self.properties_icon, image_hover = self.properties_glow_icon, command = self.file_properties_window)
        self.properties_button.pack(side = 'left', padx = 5)
        #Create the cut button (tạo nút cut)
        self.cut_button = ToolbarButton.Button(self.toolbar, image = self.cut_icon, image_hover = self.cut_glow_icon, command = self.clipboard_cut)
        self.cut_button.pack(side = 'left', padx = 5)
        #Create the copy button (tạo nút copy)
        self.copy_button = ToolbarButton.Button(self.toolbar, image = self.copy_icon, image_hover = self.copy_glow_icon, command = self.clipboard_copy)
        self.copy_button.pack(side = 'left', padx = 5)
        #Create the paste button (tạo nút paste)
        self.paste_button = ToolbarButton.Button(self.toolbar, image = self.paste_icon, image_hover = self.paste_glow_icon, command = self.clipboard_paste_thread_create)
        self.paste_button.pack(side = 'left', padx = 5)
        #Create the delete button (tạo nút delete)
        self.delete_button = ToolbarButton.Button(self.toolbar, image = self.delete_icon, image_hover = self.delete_glow_icon, command = self.delete_window)
        self.delete_button.pack(side = 'left', padx = 5)
        #Create the info button (tạo nút info)
        self.info_button = ToolbarButton.Button(self.toolbar, image = self.info_icon, image_hover = self.info_glow_icon, command = self.info)
        self.info_button.pack(side = 'right', padx = 5)
        #Create the goto button (tạo nút go to)
        self.goto_button = ToolbarButton.Button(self.toolbar, image = self.goto_icon, image_hover = self.goto_glow_icon, command = self.goto_window_ask)
        self.goto_button.pack(side = 'right', padx = 5)
        #Create the search button (tạo nút search)
        self.search_button = ToolbarButton.Button(self.toolbar, image = self.search_icon, image_hover = self.search_glow_icon, command = self.search_window_ask)
        self.search_button.pack(side = 'right', padx = 5)
        #Create label field for hostname (tạo nhãn cho hostname)
        self.label_hostname = ttk.Label(self.entry_bar, text = 'Host:')
        self.label_hostname.pack(side = 'left', padx = 2)
        #Create text field for hostname (tạo trường nhập cho hostname)
        self.hostname_entry = ttk.Entry(self.entry_bar)
        self.hostname_entry.pack(side = 'left', expand = True, fill = X)
        #Create label for username (tạo nhãn cho username)
        self.label_usrname = ttk.Label(self.entry_bar, text = 'Username:')
        self.label_usrname.pack(side = 'left', padx = 2)
        #Create text field for username (tạo trường nhập cho username)
        self.usrname_entry = ttk.Entry(self.entry_bar)
        self.usrname_entry.pack(side = 'left', expand = True, fill = X)
        #Create label for password (tạo nhãn cho password)
        self.label_pass = ttk.Label(self.entry_bar, text = 'Password:')
        self.label_pass.pack(side = 'left', padx = 2)
        #Create textfield for password (tạo trường nhập cho password)
        self.pass_entry = ttk.Entry(self.entry_bar, show = '*')
        self.pass_entry.pack(side = 'left', expand = True, fill = X)
        #Create label for port (tạo nhãn cho port)
        self.label_port = ttk.Label(self.entry_bar, text = 'Port:')
        self.label_port.pack(side = 'left', padx = 2)
        #Create textfield for port (tạo trường nhập cho port)
        self.port_entry = ttk.Entry(self.entry_bar, width = 4)
        self.port_entry.pack(side = 'left', padx = (0, 2))
        self.port_entry.insert(END, '21')
        #Create scrollbar (tạo thanh cuộn)
        self.vbar = ttk.Scrollbar(self.canvas_frame, orient=VERTICAL, style = 'Vertical.TScrollbar')
        self.vbar.pack(anchor = E,side=RIGHT,fill=Y)
        #Create drawing space for all file and folder icons (tạo không gian vẽ cho tất cả icon file và folder)
        self.canvas = Canvas(self.canvas_frame, relief = 'flat', bg = '#91BBE5', highlightthickness=0)
        self.canvas.pack(fill = BOTH, expand = True)
        self.vbar.config(command = self.canvas.yview)
        self.canvas['yscrollcommand'] = self.vbar.set
        #Create status text/bar and status sting viraiable (tạo văn bản/thanh trạng thái hoặc biến chuỗi trạng thái)
        self.current_status = StringVar()
        self.status_label = ttk.Label(master, textvariable = self.current_status, anchor = 'center')
        self.status_label.pack(fill = X)

        #Bind events (ràng buộc các sự kiện)
        self.bind_events()

    def bind_events(self):
        self.canvas.bind('<Configure>', self.draw_icons)

        #Bind events for statusbar and scroll bar (ràng buộc các sự kiện cho thanh trạng thái và thanh cuộn)
        self.vbar.bind('<Motion>', lambda event, arg = 'Scrollbar.': self.update_status(event, arg)) 
        self.status_label.bind('<Motion>', lambda event, arg = 'Statusbar.': self.update_status(event, arg)) 

    def connect_to_ftp(self):        
        #Show wait animation (Hiện animation chờ)
        self.unlock_status_bar()
        self.start_wait()
        #Show 'Connecting' in status bar (Hiện 'Đang kết nối' trên thanh trạng thái)
 
    def connect_thread(self):
        tmp = 0

    def update_file_list(self):      
        tmp = 0

    def update_file_list_thread(self):
        tmp = 0
        
    def draw_icons(self, event = None):    
        self.canvas_width = self.canvas.winfo_width() - 4
        self.canvas_height = self.canvas.winfo_height()
        if(self.cell_width > self.canvas_width):
            self.cell_width = self.canvas_width
        #Create a image (vẽ hình)
        self.canvas.create_image(self.canvas_width/2, self.canvas_height/2, image = self.whipFTP_glow_icon)
        

    
    def update_status(self, event = None, message = ' '):
        tmp = 0

    def unlock_status_bar(self):
        self.change_status = True

    def goto_window_ask(self):
        tmp = 0

    def dir_up(self):
        tmp = 0

    def file_properties_window(self):
        tmp = 0
    
    def create_dir_window(self):
        tmp = 0

    def upload_window(self):
        stmp = 0
        
    def upload(self, ftpController, file_list, selected_file_indices):     
        tmp = 0     

    def download_window(self):
        tmp = 0

    def download(self, ftpController, file_list, detailed_file_list, selected_file_indices):                       
        tmp = 0 

    def search_window_ask(self):
        tmp = 0

    def delete_window(self, event = None):
        tmp = 0

    def clipboard_cut(self, event = None):
        tmp = 0 

    def clipboard_copy(self, event = None):
       tmp = 0 

    def clipboard_paste_thread_create(self, event = None):
        tmp = 0 

    def info(self):
        tmp = 0



#Program entry point (điểm nhập chương trình)
#Tell windows not to DPI scale this application (nói với window không để DPI mở rộng ứng dụng này)
if(platform.system() is 'Windows' and platform.release() != '7'):
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
#Create root window (tạo cửa sổ gốc)
root = Tk()
#Include the theme (include theme)
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
arc_theme_path = (dname+'/Theme')
#Queue for handling threads (hàng đợi để xử ký các luồng)
global thread_request_queue
thread_request_queue = queue.Queue()
#Initilize the app (khởi tạo ứng dụng)
whipFTP = app(root)
#Initialize mainloop (khởi tạo vòng lặp chính)
root.mainloop()
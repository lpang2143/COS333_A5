#----------------------------------------------------------------------
# reg.py
# Authors: Hervé Ishimwe & Louis Pang
#----------------------------------------------------------------------

import argparse
from threading import Thread
from socket import socket
from pickle import load, dump
from sys import exit, argv
from queue import Queue, Empty
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFrame, QLabel, QLineEdit, QGridLayout,
    QVBoxLayout, QHBoxLayout, QDesktopWidget, QListWidget, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

#----------------------------------------------------------------------
# Returns the argparse object, parser, after processing the command-line
# arguments
def create_parser():
    parser = argparse.ArgumentParser(
        description='Client for the registar application',
        allow_abbrev=False)
    parser.add_argument('host',
        help='the host on which the server is running')
    parser.add_argument('port', type=int,
        help='the port at which the server is listening')
    return parser

#----------------------------------------------------------------------
# Makes the labels
def create_labels():
    # labels & text fields for dept, coursenum, area or title
    dept = QLabel('Dept:')
    coursenum = QLabel('Number:')
    area = QLabel('Area:')
    title = QLabel('Title:')

    # aligning them
    dept.setAlignment(Qt.AlignRight)
    coursenum.setAlignment(Qt.AlignRight)
    area.setAlignment(Qt.AlignRight)
    title.setAlignment(Qt.AlignRight)
    return (dept, coursenum, area, title)

#----------------------------------------------------------------------
# makes the text fields
def create_fields():
    # text fields
    dept_field = QLineEdit()
    num_field = QLineEdit()
    area_field = QLineEdit()
    title_field = QLineEdit()
    return (dept_field, num_field, area_field, title_field)

#----------------------------------------------------------------------
# getttin input from the textfields
def input_fields(text_fields):
    arr = []
    for values in text_fields:
        if values is not None:
            arr.append(values.text())
        else:
            arr.append(None)
    return (arr[0], arr[1], arr[2], arr[3])

#----------------------------------------------------------------------
# Formatting of the output text
def format_output(row):
    #formating the output to be right aligned
    data = f"{row[0]:>5d}{' '}{row[1]:>4s}{' '}"\
           f"{row[2]:>6s}{' '}{row[3]:>4s}{' '}{row[4]}"
    return data

#----------------------------------------------------------------------
def format_dialogue(in_list):
    header = 'Course Id: {courseid}\n\nDays: {days}\n'.format(**in_list)
    times = ('Start time: {start_time}\nEnd time: {end_time}\n'
            .format(**in_list))
    place = 'Building: {building}\nRoom: {room}\n\n'.format(**in_list)

    departs = ''
    for index, dept in enumerate(in_list['departments']):
        departs += ('Dept and Number: {0} {1}\n'
                    .format(dept, in_list['course numbers'][index]))
    area = '\nArea: {area}\n\nTitle: {title}\n\n'.format(**in_list)
    desrp = 'Description: {description}\n\n'.format(**in_list)
    prereqs = 'Prerequisites: {prerequisites}\n\n'.format(**in_list)

    profs = ''
    for prof in enumerate(in_list['professors']):
        profs += 'Professor: {0}\n'.format(prof[1])

    return (header + times + place + departs + area + desrp
            + prereqs + profs)

#----------------------------------------------------------------------
def create_list():
    courses_list = QListWidget()
    courses_list.setFont(QFont('Courier'))
    courses_list.insertItem(0, ' ')
    courses_list.setCurrentRow(0)
    return courses_list

#----------------------------------------------------------------------
def create_frame(labels, text_fields, courses):
    # layout for names and textfields
    names_layout = QVBoxLayout()
    names_layout.setSpacing(5)
    names_layout.setContentsMargins(0,0,0,0)
    fields_layout = QVBoxLayout()
    fields_layout.setSpacing(5)
    fields_layout.setContentsMargins(0,0,0,0)
    for i in range(4):
        names_layout.addWidget(labels[i])
        fields_layout.addWidget(text_fields[i])
    names = QFrame()
    fields = QFrame()
    names.setLayout(names_layout)
    fields.setLayout(fields_layout)

    # header frame with submit button
    header_layout = QHBoxLayout()
    header_layout.setSpacing(0)
    header_layout.setContentsMargins(0,0,0,0)
    header_layout.addWidget(names)
    header_layout.addWidget(fields)
    header = QFrame()
    header.setLayout(header_layout)

    # the combined frame with the list
    frame_layout = QGridLayout()
    frame_layout.setSpacing(0)
    frame_layout.setContentsMargins(0,0,0,0)
    frame_layout.addWidget(header, 0, 0)
    frame_layout.addWidget(courses, 1, 0, 1, 4)
    final_frame = QFrame()
    final_frame.setLayout(frame_layout)
    return final_frame

#----------------------------------------------------------------------
# creates a dialog box displaying the message
def create_dialog(message):
    message_box = QMessageBox()
    message_box.setFont(QFont('Courier'))
    message_box.setIcon(QMessageBox.Information)
    message_box.setWindowTitle('Class Details')
    message_box.setText(message)
    message_box.exec_()

#----------------------------------------------------------------------
def create_window(frame):
    window = QMainWindow()
    window.setWindowTitle('Princeton University Class Search')
    window.setCentralWidget(frame)
    screen_size = QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)
    return window

#----------------------------------------------------------------------
class WorkerThread (Thread):
    def __init__(self, host, port, info, queue):
        Thread.__init__(self)
        self._host = host
        self._port = port
        self._info = info
        self._queue = queue
        self._should_stop = False

    def stop(self):
        self._should_stop = True

    def run(self):
        try:
            with socket() as sock:
                sock.connect((self._host, self._port))

                # the tuple with the information inputed by the user
                out_flo = sock.makefile(mode='wb')
                out_list = [0, self._info]
                dump(out_list, out_flo)
                out_flo.flush()

                # reading the information from the server's query
                in_flo = sock.makefile(mode='rb')
                in_list = load(in_flo)

                # add the result of the query to the queue
                if not self._should_stop:
                    self._queue.put((True, in_list))
        except Exception as ex:
            if not self._should_stop:
                self._queue.put((False, ex))

#----------------------------------------------------------------------
def poll_queue_helper(queue, courses_list):
    while True:
        try:
            item = queue.get(block=False)
        except Empty:
            break
        courses_list.clear()
        successful, data = item
        if successful:
            courses = data
            # check if the query worked or not
            if courses[0] is False:
                msg = "A server error occurred. Please\
                        contact the system administrator."
                create_dialog(msg)
            elif len(courses[1]) == 0:
                courses_list.insertItem(0, ' ')
            else:
                for row in courses[1]:
                    courses_list.addItem(format_output(row))
                courses_list.setCurrentRow(0)
        else:
            ex = data
            create_dialog(str(ex))

#----------------------------------------------------------------------
def main() :

    # getting the command-line argumets
    input_args = create_parser().parse_args()
    host = input_args.host
    port = int(input_args.port)

    app = QApplication(argv)

    # creating the labels, text fields, list
    labels = create_labels()
    text_fields = create_fields()
    courses_list = create_list()

    # using the timer to update what is being displayed
    queue = Queue()
    def poll_queue():
        poll_queue_helper(queue, courses_list)
    timer = QTimer()
    timer.timeout.connect(poll_queue)
    timer.setInterval(100)
    timer.start()

    # spawns a new worker thread to query the database
    worker_thread = None
    def query_helper():
        nonlocal worker_thread
        info = input_fields(text_fields)

        # stops the worker thread if there was already a query going on
        if worker_thread is not None:
            worker_thread.stop()
        worker_thread = WorkerThread(host, port, info, queue)
        worker_thread.start()

    # query the database at each key store in either of the text fields
    text_fields[0].textChanged.connect(query_helper)
    text_fields[1].textChanged.connect(query_helper)
    text_fields[2].textChanged.connect(query_helper)
    text_fields[3].textChanged.connect(query_helper)

    # when we open the database
    query_helper()

    # if an item in the list is double-click, dialog appears
    def double_click_slot():
        # get the current item
        item = courses_list.currentItem()
        if item is None:
            return
        text = item.text()
        rows = text.split()

        try:
            with socket() as sock:
                sock.connect((host, port))

                # tuple with the information inputed by the user
                out_flo = sock.makefile(mode='wb')
                out_list = [1, rows[0]]
                dump(out_list, out_flo)
                out_flo.flush()

                # reading the information from the server's query
                in_list = load(sock.makefile(mode='rb'))

                # check if the query worked or not
                if in_list[0] is False:
                    msg = ("A server error occurred."
                          " Please contact the system administrator.")
                    create_dialog(msg)

                elif ((in_list[0] is True) & (in_list[1] == "no class_id")):
                    msg = ('reg_details.py: no class with classid ' + rows[0] + ' exists')
                    create_dialog(msg)

                # adding each formatted line to the list of courses
                else:
                    create_dialog(format_dialogue(in_list[1]))

        except Exception as ex:
            create_dialog(str(ex))

    # if the user double clicks on an item in the list
    courses_list.itemActivated.connect(double_click_slot)

    # create frame, window then show it
    frame = create_frame(labels,text_fields,courses_list)
    window = create_window(frame)
    window.show()
    exit(app.exec_())

#----------------------------------------------------------------------
if __name__ == '__main__':
    main()

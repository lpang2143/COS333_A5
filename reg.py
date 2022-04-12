#----------------------------------------------------------------------
# reg.py
# Authors: Hervé Ishimwe & Louis Pang
#----------------------------------------------------------------------

import argparse
import errno
from socket import socket, error as sock_error
from pickle import load, dump
from sys import stderr, exit, argv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFrame, QLabel, QLineEdit, QGridLayout,
    QVBoxLayout, QHBoxLayout, QPushButton, QDesktopWidget, QListWidget,
    QMessageBox)
from PyQt5.QtCore import Qt

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
    courses_list.insertItem(0, ' ')
    courses_list.setCurrentRow(0)
    return courses_list

#----------------------------------------------------------------------
def create_frame(labels, text_fields, button, courses):
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
    header_layout.addWidget(button)
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
def main() :

    parser = create_parser()
    input_args = parser.parse_args()

    # the command-line argumets
    host = input_args.host
    port = int(input_args.port)

    app = QApplication(argv)

    # creating the labels, text fields, submit button, list
    labels = create_labels()
    text_fields = create_fields()
    submit_button = QPushButton('Submit')
    courses_list = create_list()

    # if the submit button is clicked send a message to the server
    def submit_button_slot():

        courses_list.clear()

        try:
            with socket() as sock:
                sock.connect((host, port))

                # the tuple with the information inputed by the user
                out_flo = sock.makefile(mode='wb')
                out_list = [0, input_fields(text_fields)]
                dump(out_list, out_flo)
                out_flo.flush()

                # reading the information from the server's query
                in_flo = sock.makefile(mode='rb')
                in_list = load(in_flo)

                # check if the query worked or not
                if in_list[0] is False:
                    msg = "A server error occurred. Please contact the system administrator."
                    create_dialog(msg)

                # adding each formatted line to the list of courses
                else:
                    for row in in_list[1]:
                        courses_list.addItem(format_output(row))

        # except sock_error as s_err:
        #     if s_err.errno == errno.ECONNREFUSED:
        #         msg = str(errno.ECONNREFUSED)
        #         create_dialog(msg)

        except Exception as ex:
            create_dialog(str(ex))
            # print(ex, file=stderr)
            # exit(1)

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
                in_flo = sock.makefile(mode='rb')
                in_list = load(in_flo)

                # check if the query worked or not
                if in_list[0] is False:
                    msg = "A server error occurred. Please contact the system administrator."
                    create_dialog(msg)

                # adding each formatted line to the list of courses
                else:
                    create_dialog(format_dialogue(in_list[1]))

        # except sock_error, s_err:
        #     msg = str(s_err)
        #     create_dialog(msg)

        except Exception as ex:
            create_dialog(str(ex))

    submit_button_slot()
    double_click_slot()

    # if the user presses Enter or click the submit button
    text_fields[0].returnPressed.connect(submit_button_slot)
    text_fields[1].returnPressed.connect(submit_button_slot)
    text_fields[2].returnPressed.connect(submit_button_slot)
    text_fields[3].returnPressed.connect(submit_button_slot)
    submit_button.clicked.connect(submit_button_slot)

    # if the user double clicks on an item in the list
    courses_list.itemActivated.connect(double_click_slot)

    # create frame, window then show it
    frame = create_frame(labels,text_fields,submit_button,courses_list)
    window = create_window(frame)
    window.show()
    exit(app.exec_())

#----------------------------------------------------------------------
if __name__ == '__main__':
    main()

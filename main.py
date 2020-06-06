#!/usr/bin/env python3
import datetime as dt
import numpy as np
import os
import sys
from time import time
import tkinter.filedialog as dlg


class CountingApacheLog:
    MONTH_LIST = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    def __init__(self):
        # !! If the number of hosts exceeds default value, 10,0000, please add them. !!
        #
        # np_table format is the following
        # [[<index number of rhost>, 00:00, 01:00, ,,, Sum],
        #  [<index number of rhost_2>, 00:00, 01:00, ,,, Sum],
        #  ,,,]
        self.np_table = np.empty((100000, 26), dtype="uint32")

        # Results of remote hosts
        self.list_rhost = []

        # Log files
        self.files = []

        # counting period
        self.period = {}

    def main(self):
        self.select_files()
        self.ask_max_row()
        self.ask_period()

        start_count_time = time()

        try:
            self.process_files()
        except:
            return self.interrupt(
                "An error is occurred!\n" + \
                "If the log file is large, check the inputted value of the number of remote hosts.\n" + \
                "Otherwise please make sure that the format of the log is correct.")

        self.parse_table()

        # No data
        if self.np_table.shape[0] == 0:
            return self.interrupt("No matching logs found.")

        print("Counted all log files and found {0} remote hosts! ({1:.2f} s)".format(len(self.np_table),
                                                                                     time() - start_count_time))

        self.cut_out_table()
        self.show_result()

    # Show file dialog
    def select_files(self):
        idir = "/var/log/httpd/access_log"

        if not os.path.exists(idir):
            idir = False

        self.files = dlg.askopenfilenames(title="Select Apache Log files", initialdir=idir,
                                          filetypes=(("Log files", "*.log"), ("All files", "*.*")))

        if len(self.files) < 0:
            return self.interrupt("Log files are not found!")

    # Ask the number of np_table
    def ask_max_row(self):
        max_row = input("Please input a number that is greater than or equal to the number " + \
                        "of remote host that appear in the log file. (Default: 100000)\t")

        print("!! If the number of remote hosts exceeds the input value, please increase the number. !!")

        # Str to int
        try:
            max_row = int(max_row)
        except:
            print("The default value of '10000' was set.")
            return

        if max_row <= 0:
            print("The default value of '10000' was set.")
            return
        else:
            self.np_table = np.empty((max_row, 26), dtype="uint32")

    # Ask the specified period
    def ask_period(self):
        # Whether to specify a period of time
        is_period = input("Do you want to specify the period of time to be counted? (Yes or No)\t")

        if is_period in ["n", "N", "no", "No"]:
            return
        elif is_period not in ["y", "Y", "yes", "Yes"]:
            print("Please input 'Yes' or 'No'!")
            print("The default value of 'No' was set.")
            return

        self.period = {"start": "", "end": ""}

        for key in self.period:
            self.period[key] = input("Please input the " + key + " date. eg: 2020/06/01\t")

            if not len(self.period[key]) == 10:
                return self.interrupt("Please input the " + key + " date in the correct format!")

            # Str to date
            try:
                self.period[key] = dt.date(int(self.period[key][0:4]), int(self.period[key][5:7]),
                                           int(self.period[key][8:10]))
            except:
                return self.interrupt("Please input the " + key + " date in the correct format!")

        if not self.period["start"] <= self.period["end"]:
            return self.interrupt("Please input the end date that is later than the start date!")

    # process files
    def process_files(self):
        for file in self.files:
            start_process_time = time()
            print("{0} is now processing...".format(file))

            # In order to speed up processing, we first branch out on whether or not a period is specified,
            # but it complicates the source code.

            # No specified period of time
            if len(self.period) != 2:
                with open(file) as f:
                    for line in f:
                        item_buf = line.split(' ')

                        item_rhost = item_buf[0]
                        item_time = item_buf[3][1:]

                        self.add_data(item_rhost, item_time)

            # Specified period of time
            else:
                with open(file) as f:
                    for line in f:
                        item_buf = line.split(' ')

                        item_rhost = item_buf[0]
                        item_time = item_buf[3][1:]

                        if self.check_date(item_time, self.period):
                            self.add_data(item_rhost, item_time)

            print("Finished processing the log file! ({0:.2f} s)".format(time() - start_process_time))

    # Add data to table
    def add_data(self, _rhost, _time):
        # The first one is the index number, so do +1
        hour = int(_time[12:14]) + 1

        if _rhost in self.list_rhost:
            rhost_index = self.list_rhost.index(_rhost)
        else:
            # Add list_rhost
            self.list_rhost.append(_rhost)

            rhost_index = len(self.list_rhost) - 1

            # Fill in with zeros
            self.np_table[rhost_index, :] = 0

            # Add the index number
            self.np_table[rhost_index, 0] = rhost_index

        self.np_table[rhost_index, hour] += 1
        self.np_table[rhost_index, 25] += 1

    # Check if the date is within the specified period
    def check_date(self, _time, _period):
        # Str to date
        try:
            date_item = dt.date(int(_time[7:11]), self.MONTH_LIST.index(_time[3:6]) + 1, int(_time[0:2]))
        except:
            return self.interrupt("Log format is invalid!")

        # Check
        if _period["start"] <= date_item <= _period["end"]:
            return True

        return False

    # Sort and Remove unnecessary rows
    def parse_table(self):
        # Remove unnecessary rows
        self.np_table = self.np_table[0:len(self.list_rhost), :]
        # Sort
        self.np_table = self.np_table[np.argsort(self.np_table[:, 25])[::-1]]

    # Ask the res_num and cut out np_table
    def cut_out_table(self):
        res_num = 20

        # Number of results
        buf_num = input("How many remote hosts do you want to show? (Default: 20)\t")

        # Str to int
        try:
            res_num = int(buf_num)
        except:
            print("The default value of '{}' was set.".format(res_num))

        if 0 <= res_num <= self.np_table.shape[0]:
            # Overwrite to reduce memory usage
            self.np_table = self.np_table[0:res_num, :]
        else:
            print("All results are showed, because the input value is invalid.")

    # Show the result table
    def show_result(self):
        hour_sum = np.sum(self.np_table[:, 1:], axis=0)

        # Number of characters
        num_len_max = max(len(str(hour_sum[-1])), 5)
        rhost_len_max = max(len(max(self.list_rhost, key=len)), 11)

        # format
        bar = "─" * (num_len_max * 25 + rhost_len_max + 25)
        base_rhost = "{:^" + str(rhost_len_max) + "} "
        base_item = "{:>" + str(num_len_max) + "} "

        print("\n" + bar)

        # header
        print(base_rhost.format("Remote Host"), end="")
        [print(base_item.format(str(hour) + ":00"), end="") for hour in range(24)]
        print(base_item.format("Total"))

        print(bar)

        # content
        for row in self.np_table:
            print(base_rhost.format(self.list_rhost[row[0]]), end="")
            [print(base_item.format(val), end="") for val in row[1:]]
            print()

        print(bar)

        # sum
        print(base_rhost.format("Total"), end="")
        [print(base_item.format(hour), end="") for hour in hour_sum]
        print()

        print(bar)

    # An error has occurred
    @staticmethod
    def interrupt(_msg):
        print("\n" + _msg)
        print("The program is terminated.")
        return sys.exit()


if __name__ == "__main__":
    CountingApacheLog().main()

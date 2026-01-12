from datetime import datetime
from tkinter import messagebox
from names_list import names,locations
from tkinter import ttk
import matplotlib.pyplot as plt
import tkinter as tk
import sqlite3 as sql
import random
import os
import time
import traceback




# TABLE FUNCTIONS
# Function called when user clicks fragment
def item_select(_,window,conn,table,main_window):
    """
    :param _: The event object
    :param window: Current window
    :param conn: SQL connection
    :param table: Table of suspects
    :param main_window: The startup window
    :return: None
    """
    fragment_list = []
    time.sleep(0.5)

    # Make a list of all the fragments selected
    for x in table.selection():
        fragment_list.append(table.item(x)["values"])

    # Make sure fragment list is only 1 element long
    if len(fragment_list) == 1:
        print(fragment_list[0][0],fragment_list[0][1])
        suspects = find_fragment(conn, [[fragment_list[0][0], f"%{fragment_list[0][1]}%"]])

        if isinstance(suspects,str):
            print(f"No suspects were found with fragment id: {fragment_list[0][0]}")
            window.withdraw()
            suspects_found_table(suspects, fragment_list[0][0], window,main_window)
        else:
            window.withdraw()
            suspects_found_table(suspects,fragment_list[0][0],window,main_window)

    else:
        print("too many selections")


# Display all suspects found in a table
def suspects_found_table(suspects,frag_id,parent_window,main_window):
    """
    :param suspects: The list of suspects
    :param frag_id: The fragment id that the suspects contains
    :param parent_window: The startup window
    :param main_window: The current window
    :return: None
    """
    window = tk.Tk()
    window.attributes('-fullscreen',True)
    window.title(f"SUSPECTS FOUND WITH FRAGMENT ID:{frag_id}")

    title_frame = tk.Frame(window)
    title_frame.pack(pady=20)
    title = tk.Label(title_frame,text=f"Suspects found with fragment ID:{frag_id}")
    title.pack()
    title.config(font=("Arial", 20))

    table = ttk.Treeview(window, columns=("id", "name", "dob", "age", "data"), show="headings")
    table.heading("id", text="Suspect ID")
    table.heading("name", text="Suspect Name")
    table.heading("dob", text="Suspect Date Of Birth")
    table.heading("age", text="Suspect Age")
    table.heading("data", text="Suspect Data")
    table.pack(fill="both", expand=True)


    if isinstance(suspects,list):
        for x in range(len(suspects)):
            try:
                table.insert(parent="", index=tk.END, values=(suspects[x][0], suspects[x][1], suspects[x][2], suspects[x][3], suspects[x][4]))
            except Exception as e:
                raise Exception (f"InsertError: \nError inserting suspect: {suspects[x]} on line 64")

        button_frame = tk.Frame(window)
        button_frame.pack(pady=40)

        def back_to_frag_table():
            window.destroy()
            parent_window.deiconify()

        def exit_table(main_window):
            main_window.destroy()
            parent_window.destroy()
            window.destroy()

        exit_button = tk.Button(button_frame, text="Exit", command=lambda :exit_table(main_window))
        exit_button.pack(pady=10,fill=tk.Y,side=tk.LEFT)
        back_button = tk.Button(button_frame, text="Back", command=back_to_frag_table)
        back_button.pack(pady=10,fill=tk.Y,side=tk.LEFT)
        window.mainloop()

    elif isinstance(suspects,str):

        table.insert(parent="", index=tk.END, values=(suspects,"","","",""))

        button_frame = tk.Frame(window)
        button_frame.pack(pady=40)

        def back_to_frag_table():
            window.destroy()
            parent_window.deiconify()

        def exit_table():
            parent_window.destroy()
            window.destroy()

        exit_button = tk.Button(button_frame, text="Exit", command=exit_table)
        exit_button.pack(pady=10,fill=tk.Y,side=tk.LEFT)
        back_button = tk.Button(button_frame, text="Back", command=back_to_frag_table)
        back_button.pack(pady=10, fill=tk.Y,side=tk.LEFT)
        window.mainloop()



# SQLITE FUNCTIONS
# Connect to database
def connect_db():
    """
    :return: (connection) The SQL database connection
    """
    try:
        current_directory = os.getcwd()
        files = os.listdir(current_directory)
        try:
            file = open("DNA_DATA_BASE.db","x")
            file.close()
            connection = sql.connect("DNA_DATA_BASE.db")
            print("Connection established")
            return connection
        except:
            connection = sql.connect("DNA_DATA_BASE.db")
            print("Connection established")
            return connection

    except:
        messagebox.showerror("Error" , "Error: Connection failed")
        print("Connection failed")
        return None


# Execute a query
def execute_query(connection, query):
    """
    :param connection: The SQL database connection
    :param query: The SQL query
    :return: None
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
    except:
        messagebox.showerror("Error", "Error: Query failed to execute")


def read_in_fragments_or_suspects(conn, s_or_f):
    """
    :param conn: The SQL database connection
    :param s_or_f: Suspects or Fragments
    :return: return response or None
    """
    cursor = conn.cursor()

    try:
        if s_or_f.upper() not in ["SUSPECTS", "FRAGMENTS"]:
            print(f"Error: Invalid table name {s_or_f}")
            return None

        query = f"SELECT * FROM {s_or_f}"
        cursor.execute(query)
        response = cursor.fetchall()
        return response

    except:
        messagebox.showerror("Error","Error: could not retrieve suspect or fragment data on line")
        print(traceback.format_exc())
        return None


def find_fragment(conn,fragment):
    """
    :param conn: The SQL database connection
    :param fragment: The fragment to be found
    :return: Suspect(s) list or 'No suspects found'
    """
    cursor = conn.cursor()

    if len(fragment) == 1:
        try:
            print(fragment[0][1],)
            cursor.execute("SELECT * FROM SUSPECTS WHERE SUSPECT_DATA like (?)",
                           (fragment[0][1],))
            suspects = cursor.fetchall()

            if len(suspects) == 0:
                return "No suspects found"
            elif len(suspects) > 0:
                return suspects
            else:
                messagebox.showerror("FATAL_ERROR","FATAL ERROR: cursor.fetchall() malfunctioned, please restart program")
                exit()

        except Exception as e:
            messagebox.showerror("Error",f"Error: invalid sqlite3 query, please input correct sqlite3 query.")

    else:
        print("too many fragments")


def ensure_table_exists(conn,cursor,s_or_f):
    if s_or_f == "s":
        suspect_table = """CREATE TABLE IF NOT EXISTS SUSPECTS (
                            SUSPECT_ID INTEGER PRIMARY KEY AUTOINCREMENT, 
                            SUSPECT_NAME TEXT, 
                            SUSPECT_DOB TEXT, 
                            SUSPECT_AGE INTEGER, 
                            SUSPECT_DATA TEXT);
                            """
        cursor.execute(suspect_table)
        conn.commit()



# GENERATE FUNCTIONS
# Generate unique suspects and return them to a list
def generate_suspects(s_quota="1", sql_or_list="sql", conn=None,):
    if conn is None:
        messagebox.showerror("Error","Error: No database connection provided.")
        return None

    cursor = conn.cursor()

    ensure_table_exists(conn,cursor,"s")
    s_list = []


    if s_quota.isdigit():
        for z in range(int(s_quota)):
            suspect = [0,0,0,0,0,[]]
            date_and_time = datetime.now().strftime("%Y")

            suspect[1] = str(generate_names(1)).strip("['] ")
            suspect[2] = random.choice(["Male","Female"])
            suspect[3] = generate_dates(1)
            suspect[4] = int(date_and_time) - int(suspect[3][-4:])


            list1 = []

            for y in range(250):
                x = random.choice(["A", "T", "C", "G"])
                list1.append(x)
            suspect[5] = str(list1).strip("[]")

            s_list.append(suspect)


        for num,val in enumerate(s_list):
            cursor = conn.cursor()
            cursor.execute(
            "INSERT INTO SUSPECTS (SUSPECT_NAME, SUSPECT_DOB, SUSPECT_AGE, SUSPECT_DATA) VALUES (?,?,?,?)",
                (s_list[num][1], s_list[num][3], s_list[num][4], s_list[num][5])
                )


        conn.commit()


    else:
        messagebox.showerror("Error","Error: failed to int, please enter a number")
        return None


# Generate unique fragment DNA samples and then return them to a list
def generate_fragments(conn,fragment_quota):
    cursor = conn.cursor()
    fragment_list = []
    fragment_quota = str(fragment_quota)
    ensure_table_exists(conn,cursor,"f")


    if fragment_quota.isdigit():
        for z in range(int(fragment_quota)):
            f_list = []
            fragment = []
            f_list.append(generate_dates(1))
            for y in range(random.randint(8,12)):
                x = random.choice(["A", "T", "C", "G"])
                fragment.append(x)
            f_list.append(str(fragment).strip("[]"))
            fragment_list.append(f_list)

        start = time.perf_counter()
        for num,val in enumerate(fragment_list):
            cursor = conn.cursor()
            cursor.execute("INSERT INTO FRAGMENTS (FRAGMENT_DATA, FRAGMENT_DATE,FRAGMENT_LOCATION) VALUES (?,?,?)",
                           (fragment_list[num][1],fragment_list[num][0],random.choice(locations)))
            conn.commit()
        finish = time.perf_counter()
        print(f"Time took was {finish - start:0.4f} seconds")


    else:
        messagebox.showerror("Error","Error: Please enter a number")
        return None


def generate_names(name_quota):
    name_list = []

    for num in range(name_quota):
        name_choice = random.choice(names)
        name_list.append(name_choice)

    return name_list


def generate_dates(date_quota):
    date_list = []
    year_now = datetime.now().strftime("%Y")
    for x in range(date_quota):
        year = random.randint(int(year_now)-100,int(year_now)-13)
        month = random.randint(1,12)
        day = random.randint(1,28)
        date = str(day)+"/"+str(month)+"/"+str(year)
        date_list.append(date)
    if len(date_list) == 1:
        return date_list[0]
    else:
        return date_list


# Start up functions
def start_up_interface():
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    ensure_table_exists(conn, cursor, "f")
    ensure_table_exists(conn, cursor, "s")
    suspect_test = read_in_fragments_or_suspects(conn, "SUSPECTS")



    window = tk.Tk()
    window.title("Snake Global Industries DNA application")
    window.attributes("-fullscreen",True)


    text_frame = tk.Frame(master=window,height=40)
    text_frame.pack(fill=tk.X)
    greeting_txt = tk.Label(master=text_frame, text="Snake Global DNA Analyzer")

    greeting_txt.pack()
    greeting_txt.config(font=("Arial", 35))

    choice_frame = tk.Frame(master=window, height=60)
    choice_frame.pack(pady=265)
    choice_txt = tk.Label(choice_frame,text="Please Select From The Following Choices:")
    choice_txt.pack(pady=10)
    choice_txt.config(font=("Arial", 15))

    exit_frame = tk.Frame(master=window)
    exit_frame.pack(pady=20)


    def fragments_table_run(conn, parent_window):
        parent_window.withdraw()
        frag_list = read_in_fragments_or_suspects(conn, "FRAGMENTS")

        def back_button_run(frag_window, main_window):
            frag_window.destroy()
            main_window.deiconify()

        def exit_button_run(frag_window,main_window):
            frag_window.destroy()
            main_window.destroy()


        window = tk.Tk()
        window.attributes('-fullscreen', True)
        window.title("FRAGMENTS")

        scroll_bar = tk.Scrollbar(window)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        title_frame = tk.Frame(master=window,height=30)
        title_frame.pack()

        greeting_txt = tk.Label(master=title_frame, text="Fragments Table")
        greeting_txt.pack()
        greeting_txt.config(font=("Arial", 20))

        instructions = tk.Label(title_frame,text="Select A Fragment:")
        instructions.pack()

        table = ttk.Treeview(window, columns=("id", "dna", "date", "location"), show="headings")
        table.heading("id", text="Fragment ID")
        table.heading("dna", text="DNA")
        table.heading("date", text="Date")
        table.heading("location", text="Location")
        table.pack(fill="both", expand=True)

        button_frame = tk.Frame(master=window)
        button_frame.pack(pady=25)

        exit_button = tk.Button(button_frame,text="Exit App", command=lambda: exit_button_run(window,parent_window))
        exit_button.pack(padx=20,pady=15,fill=tk.Y,side=tk.LEFT)
        back_button = tk.Button(button_frame,text="Back", command=lambda: back_button_run(window,parent_window))
        back_button.pack(padx=20,pady=15,fill=tk.Y,side=tk.LEFT)

        for x in range(len(frag_list)):
            table.insert(parent="", index=tk.END,
                         values=(frag_list[x][0], frag_list[x][1], frag_list[x][2], frag_list[x][3]))

        table.bind("<<TreeviewSelect>>", lambda event: item_select(event, window, conn, table,parent_window))
        window.mainloop()


    def dataplotter(conn,parent_window):
        parent_window.withdraw()
        window = tk.Tk()

        def exit_button_run(plot_window,main_window):
            plot_window.destroy()
            main_window.destroy()

        def back_button_run(plot_window,parent_window):
            plot_window.destroy()
            parent_window.deiconify()


    def start_generate_data(conn,parent_window):

        def back_button_run(gen_window,parent_window):
            gen_window.destroy()
            parent_window.deiconify()

        def exit_button_run(gen_window,parent_window):
            gen_window.destroy()
            parent_window.destroy()

        def get_input():
            sus_entry = suspects_entry.get()
            frag_msg = frag_entry.get()

            if frag_msg == "" or frag_msg.isalpha() or frag_msg.isspace() or frag_msg.isdigit() == False:
                messagebox.showerror("Error","Error: Please enter a number")
                time.sleep(0.5)
                frag_entry.delete(0, tk.END)

            if sus_entry == "" or sus_entry.isalpha() or sus_entry.isspace() or sus_entry.isdigit() == False:
                messagebox.showerror("Error","Error: Please enter a number")
                time.sleep(0.5)
                suspects_entry.delete(0, tk.END)

            elif frag_msg.isdigit() and sus_entry.isdigit():

                time.sleep(1)
                generate_suspects(sus_entry,"sql",conn)
                generate_fragments(conn,int(frag_msg))


                success_msg = messagebox.showinfo("Success","Successfully generated data\n(You may close this window)",master=window)
                time.sleep(1)
                frag_entry.delete(0, tk.END)
                suspects_entry.delete(0, tk.END)

            else:
                messagebox.showerror("Error","Error: Data is invalid, please input a number")
                time.sleep(0.5)
                frag_entry.delete(0, tk.END)
                suspects_entry.delete(0, tk.END)

        parent_window.withdraw()
        window = tk.Tk()
        window.attributes("-fullscreen", True)
        window.title("Generate data")

        title_frame = tk.Frame(master=window,height=30)
        title_frame.pack()
        title = tk.Label(title_frame,text="Generate data")
        title.pack()
        title.config(font=("Arial",35))


        upper_frame = tk.Frame(master=window,height=30)
        upper_frame.pack(pady=20)
        info_label = tk.Label(upper_frame,text="Please enter the desired amount of suspects and fragments below.\nThey will be saved automatically to a file.")
        info_label.pack(pady=10)
        info_label.config(font=("Arial",13))

        middle_frame = tk.Frame(master=window,height=30)
        middle_frame.pack(pady=170)

        txt_label = tk.Label(middle_frame,text="Please note large amounts of suspects and or fragments take time so please wait till a success message appears.",font=("Arial",8))
        txt_label.pack(pady=20)
        suspect_label = tk.Label(middle_frame,text="Enter the desired amount of suspects:")
        suspect_label.pack(pady=10)
        suspects_entry = tk.Entry(middle_frame, width=30)
        suspects_entry.pack(pady=10)

        frag_label = tk.Label(middle_frame,text="Enter the desired amount of fragments:")
        frag_label.pack(pady=10)
        frag_entry = tk.Entry(middle_frame, width=30)
        frag_entry.pack(pady=10)
        submit_button = tk.Button(middle_frame, text="Submit", command=get_input)
        submit_button.pack(pady=5)


        button_frame = tk.Frame(master=window,height=30)
        button_frame.pack()
        exit_button = tk.Button(button_frame,text="Exit", command=lambda: exit_button_run(window,parent_window))
        back_button = tk.Button(button_frame,text="Back", command=lambda : back_button_run(window,parent_window))
        exit_button.pack(padx=20, pady=15, fill=tk.Y, side=tk.LEFT)
        back_button.pack(padx=20, pady=15,fill=tk.Y,side=tk.LEFT)

        window.mainloop()


    def delete_data(conn,parent_window):
        
        
        def del_all_run(conn):
            cursor = conn.cursor()
            response = messagebox.askquestion("Delete All Data", "Are you sure you want to delete all data?")
            if response == "yes":
                cursor.execute("DELETE FROM SUSPECTS")
                cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE NAME = 'SUSPECTS'")
                cursor.execute("DELETE FROM FRAGMENTS")
                cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE NAME = 'FRAGMENTS'")
                conn.commit()
                messagebox.showinfo("Success","All data has been deleted")
            else:
                messagebox.showinfo("Cancel","Delete operation cancelled")


        def del_fragment_button_run(parent_window):
            parent_window.withdraw()

            def delete_input():
                del_frag = frag_choice_del.get()
                if del_frag == "" or del_frag.isalpha() or del_frag.isspace() or del_frag.isdigit() == False:
                    messagebox.showerror("Error","Error: Please enter a number")
                    time.sleep(0.5)
                    frag_choice_del.delete(0, tk.END)

                elif del_frag.isdigit():
                    print("Still in development :(")

                else:
                    messagebox.showerror("Error","Error: Input failed to int, please enter a number")
                    time.sleep(0.5)
                    frag_choice_del.delete(0, tk.END)


            def exit_button_run(window):
                window.quit()
                window.destroy()
                os._exit(0)

            def back_button_run(del_window,parent_window):
                del_window.destroy()
                parent_window.deiconify()

            window = tk.Tk()
            window.attributes("-fullscreen", True)
            window.title("Delete Fragments")

            title_frame = tk.Frame(master=window,height=30)
            title_frame.pack(pady=20)
            title = tk.Label(title_frame,text="Delete Fragments",font=("Arial",35))
            title.pack()

            middle_frame = tk.Frame(master=window,height=30)
            middle_frame.pack(pady=200)

            frag_choice_del = tk.Entry(middle_frame,width=30)
            frag_choice_del.pack(pady=10, padx=20, fill=tk.Y,side=tk.LEFT)
            submit_button = tk.Button(middle_frame,text="Submit",command=lambda: print("still developing :("))

            bottom_frame = tk.Frame(master=window,height=30)
            bottom_frame.pack(pady=20)
            back_button = tk.Button(bottom_frame,text="Back", command=lambda: back_button_run(window,parent_window))
            exit_button = tk.Button(bottom_frame, text="Exit", command=lambda: exit_button_run(window))
            exit_button.pack(padx=20, pady=15, fill=tk.Y, side=tk.LEFT)
            back_button.pack(padx=20, pady=15, fill=tk.Y, side=tk.LEFT)

        def del_number_run(conn,number):
            cursor = conn.cursor()
            response = messagebox.askquestion("Delete 100 Fragments", "Are you sure you want to delete 100 fragments?")
            if response == "yes":
                cursor.execute(f"DELETE FROM SUSPECTS WHERE SUSPECT_ID IN (SELECT SUSPECT_ID FROM SUSPECTS ORDER BY SUSPECT_ID ASC LIMIT {number})")
                conn.commit()
                messagebox.showinfo("Success","100 Fragments have been deleted")
            else:
                messagebox.showinfo("Cancel","Delete operation cancelled")

        def back_button_run(del_window,parent_window):
            del_window.destroy()
            parent_window.deiconify()

        def exit_button_run(window, parent_window):
            try:
                window.destroy()
            except:
                pass
            try:
                if parent_window.winfo_exists():
                    parent_window.destroy()
            except:
                pass

        parent_window.withdraw()

        window = tk.Tk()
        window.attributes("-fullscreen", True)
        window.title("Delete data")

        title_frame = tk.Frame(master=window,height=30)
        title_frame.pack(pady=20)
        title = tk.Label(title_frame,text="Delete Data",font=("Arial",35))
        title.pack()

        middle_frame = tk.Frame(master=window,height=30)
        middle_frame.pack(pady=110)
        del_frag_button = tk.Button(middle_frame,text="Delete Fragments",command=lambda: del_fragment_button_run(parent_window))
        del_frag_button.pack(pady=10)

        del_tag = tk.Label(middle_frame,text="Enter the fragment ID you wish to delete: ",font=("Arial",13))
        del_tag.pack(pady=10)
        del_frag = tk.Entry(middle_frame,width=30)
        del_frag.pack(pady=10)
        del_sus_tag = tk.Label(middle_frame,text="Enter the suspect Name you wish to delete: ",font=("Arial",13))
        del_sus_tag.pack(pady=10)
        del_sus = tk.Entry(middle_frame,width=30)
        del_sus.pack(pady=10)

        del_button_frame = tk.Frame(master=window,height=30)
        del_button_frame.pack(pady=20)

        del_100_button = tk.Button(del_button_frame,text="Delete 100 Fragments",command=lambda: del_number_run(conn,100))
        del_100_button.pack(pady=10,side=tk.LEFT)
        del_1000_button = tk.Button(del_button_frame,text="Delete 1000 Fragments",command=lambda: del_number_run(conn,1000))
        del_1000_button.pack(pady=10,side=tk.LEFT)
        del_10000_button = tk.Button(del_button_frame,text="Delete 10,000 Fragments",command=lambda: del_number_run(conn,10000))
        del_10000_button.pack(pady=10)

        bottom_frame = tk.Frame(master=window,height=30)
        bottom_frame.pack(pady=60)
        del_all_button = tk.Button(bottom_frame,text="Delete All Data",command=lambda: del_all_run(conn))
        del_all_button.pack(pady=10)

        bottom_frame = tk.Frame(master=window,height=30)
        bottom_frame.pack(pady=20)
        back_button = tk.Button(bottom_frame,text="Back", command=lambda: back_button_run(window,parent_window))
        exit_button = tk.Button(bottom_frame,text="Exit", command=lambda: exit_button_run(window,parent_window))
        exit_button.pack(padx=20, pady=15, fill=tk.Y, side=tk.LEFT)
        back_button.pack(padx=20, pady=15, fill=tk.Y, side=tk.LEFT)



    # Buttons/small button functions
    def exit_program(conn,main_window):
        main_window.destroy()
        conn.close()
        # END OF PROGRAM
        exit()

    exit_button = tk.Button(exit_frame, text="Exit App", command=lambda: exit_program(conn,window))
    exit_button.pack(padx=20, pady=15)


    frag_table_button = ttk.Button(choice_frame, text="Fragment Table Finder", command=lambda: fragments_table_run(conn, window))
    frag_table_button.pack(padx=40, pady=15)
    dataplot_button = ttk.Button(choice_frame, text="Data And Analytics", command=lambda: dataplotter(conn, window))
    generate_button = ttk.Button(choice_frame, text="Generate data", command=lambda: start_generate_data(conn, window))
    generate_button.pack(padx=40, pady=15)
    delete_button = ttk.Button(choice_frame, text="Delete Data", command=lambda: delete_data(conn, window))
    delete_button.pack(padx=40, pady=15)


    window.mainloop()



# MAIN PROGRAM
if __name__ == "__main__":
    start_up_interface()


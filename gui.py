import PySimpleGUI as sg
from matrix import Matrix

def generate_table(num, row, col):
    return [sg.Column([[sg.Input(0, do_not_clear=True, size=(3,2),\
                                 key=(num, i, j), justification='right')]\
                       for i in range(1, row+1)]) for j in range(1, col+1)]

def output_popup():
    output_layout = [[sg.Output(size=(80,20))],
                     [sg.Quit()]]
    output_window = sg.Window('Output', output_layout, finalize=True)
    return output_window


class EventHandler:
    def __init__(self, window, event=None, values=None):
        self.event = event
        self.values = values
        self.window = window
        self.layout = self.window.Rows[:]
        self.mat1 = Matrix()
        self.mat2 = Matrix()
        self.output_popup_activate = False
        self.output_event_list = ('_MUL_BTN_', '_GAUSS_BTN_',
                                  '_TRANS_BTN_1_', '_INV_BTN_1_',
                                  '_DET_BTN_1_', '_CRAMER_BTN_1_',
                                  '_TRANS_BTN_2_', '_INV_BTN_2_',
                                  '_DET_BTN_2_', '_CRAMER_BTN_2_')

    def update(self, window, event, values):
        self.window = window
        self.event = event
        self.values = values
        self.layout = self.window.Rows[:]

    def process(self):
        if self.event in self.output_event_list and\
           not self.output_popup_activate:
            self.output_popup_activate = True
            self.output_window = output_popup()

        if self.output_popup_activate:
            out_event, _ = self.output_window.Read(timeout=100)
            if out_event is None or out_event == 'Quit':
                self.output_popup_activate = False
                self.output_window.Close()

        if 'ROW' in self.event or 'COL' in self.event:
            self.change_table()
        else:
            if self.event != "__TIMEOUT__":
                self.get_matrixes()
            if event == '_MUL_BTN_':
                res = Matrix.mul_stepbystep(self.mat1, self.mat2)
                print(res)
            if event == '_GAUSS_BTN_':
                try:
                    self.mat1.gauss_elim(self.mat2, step_by_step=True)
                except ValueError as e:
                    print(str(e))
                except ZeroDivisionError as e:
                    print(str(e))
            if 'TRANS' in self.event:
                calc_num = int(self.event[-2])
                if calc_num == 1:
                    print(self.mat1.T)
                else:
                    print(self.mat2.T)
            if 'INV' in self.event:
                calc_num = int(self.event[-2])
                try:
                    if calc_num == 1:
                        res = self.mat1.inv_using_det(step_by_step=True)
                    else:
                        res = self.mat2.inv_using_det(step_by_step=True)
                    print(res)
                except ZeroDivisionError as e:
                    print("=================")
                    print(str(e))
                    print("No inverse matrix")
                except ValueError as e:
                    print(str(e))
                    print("No inverse matrix")
            if 'DET' in self.event:
                calc_num = int(self.event[-2])
                try:
                    if calc_num == 1:
                        self.mat1.det_step_by_step()
                    else:
                        self.mat2.det_step_by_step()
                except ValueError as e:
                    print(str(e))
                    print("No determinant")
            if 'CRAMER' in self.event:
                calc_num = int(self.event[-2])
                try:
                    if calc_num == 1:
                        res = self.mat1.cramer(tuple(self.mat2.T[0]),
                                               step_by_step=True)
                    else:
                        res = self.mat2.cramer(tuple(self.mat1.T[0]),
                                               step_by_step=True)
                    print("===ROOTS===")
                    print(tuple(str(next_root) for next_root in res))
                except ZeroDivisionError as e:
                    print(str(e))
                    print("Cannot be solved.")
        return self.window

    def get_matrixes(self):
            row_val_1 = int(self.values['_ROW1_'])
            col_val_1 = int(self.values['_COL1_'])
            row_val_2 = int(self.values['_ROW2_'])
            col_val_2 = int(self.values['_COL2_'])
            self.mat1 = self.get_matrix(1, row_val_1, col_val_1)
            self.mat2 = self.get_matrix(2, row_val_2, col_val_2)

    def get_matrix(self, num, max_row, max_col):
        return Matrix([[int(self.values[(num, j, i)])\
                        for i in range(1, max_col + 1)]
                       for j in range(1, max_row + 1)])

    def change_table(self):
        col1 = self.window['_LEFT_'].Rows[:]
        col2 = self.window['_RIGHT_'].Rows[:]
        col_btn = self.window['_BTNS_'].Rows[:]
        update_num = int(self.event[-2])
        row_val = int(self.values['_ROW' + str(update_num) + '_'])
        col_val = int(self.values['_COL' + str(update_num) + '_'])
        new_table = generate_table(update_num, row_val, col_val)
        if update_num == 1:
            col1[1] = new_table
        else:
            col2[1] = new_table
        self.layout = [[sg.Column(col1, key='_LEFT_'),
                        sg.Column(col_btn, key='_BTNS_'),
                        sg.Column(col2, key='_RIGHT_')],
                       [sg.Text("Cramer's formular uses "\
                                "first column of the other matrix.")],
                       [sg.Exit()]]
        self.update_window()

    def update_window(self):
        cur = self.window.current_location()
        window1 = sg.Window('Matrix with step by step solution', self.layout,
                            location=cur, finalize=True)
        window1.fill(values)
        self.window.Close()
        self.window = window1

col1 = [[sg.Spin(list(range(1, 11)), initial_value=3,\
                 key='_ROW1_', enable_events=True),
         sg.Text("X"),
         sg.Spin(list(range(1, 11)), initial_value=3,\
                 key='_COL1_', enable_events=True)],
        generate_table(1, 3, 3),
        [sg.Button("Transpose", key='_TRANS_BTN_1_'),
         sg.Button("Determinant", key='_DET_BTN_1_')],
        [sg.Button("Inverse", key='_INV_BTN_1_'),
         sg.Button("Cramer's formular", key='_CRAMER_BTN_1_')]]
col_btn = [[sg.Button("Matrix multiply", key='_MUL_BTN_')],
           [sg.Button("Gauss elimination:", key='_GAUSS_BTN_')]]
col2 = [[sg.Spin(list(range(1, 11)), initial_value=3,\
                 key='_ROW2_', enable_events=True),
         sg.Text("X"),
         sg.Spin(list(range(1, 11)), initial_value=3,\
                 key='_COL2_', enable_events=True)],
        generate_table(2, 3, 3),
        [sg.Button("Transpose", key='_TRANS_BTN_2_'),
         sg.Button("Determinant", key='_DET_BTN_2_')],
        [sg.Button("Inverse", key='_INV_BTN_2_'),
         sg.Button("Cramer's formular", key='_CRAMER_BTN_2_')]]

layout = [[sg.Column(col1, key='_LEFT_'), sg.Column(col_btn, key='_BTNS_'),
           sg.Column(col2, key='_RIGHT_')],
          [sg.Text("Cramer's formular uses first column of the other matrix.")],
          [sg.Exit()]]


window = sg.Window('Matrix with step by step solution', layout)

handler = EventHandler(window)

while True:
    event, values = window.Read(timeout=100)
    handler.update(window, event, values)
    if event is None or event == 'Exit':
        break
    try:
        window = handler.process()
    except Exception as e:
        print(str(e))



window.Close()

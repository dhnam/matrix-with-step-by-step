import PySimpleGUI as sg
from matrix import Matrix

def generate_table(num, row, col):
    return [sg.Column([[sg.Input(0, do_not_clear=True, size=(3,2),\
                                 key=(num, i, j), justification='right')]\
                       for i in range(1, row+1)]) for j in range(1, col+1)]

def output_popup():
    output_layout = [[sg.Output(size=(80,20), font='Consolas 10')],
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
        OFFSET = -2
        processer = None

        if self.event in self.output_event_list and\
           not self.output_popup_activate:
            self.output_popup_activate = True
            self.output_window = output_popup()

        if self.output_popup_activate:
            out_event, _ = self.output_window.Read(timeout=100)
            if out_event is None or out_event == 'Quit':
                self.output_popup_activate = False
                self.output_window.Close()

        if self.event == "__TIMEOUT__":
            return self.window

        elif 'ROW' in self.event or 'COL' in self.event:
            process_num = int(self.event[OFFSET])
            processer = TableChangeEventProcesser(values=self.values,
                                                  process_num=process_num,
                                                  window=self.window)
            self.window = processer.process()


        else:
            self.get_matrixes()
            if event == '_MUL_BTN_':
                processer = MatmulEventProcesser(mat1=self.mat1,
                                                 mat2=self.mat2)
                
            elif event == '_GAUSS_BTN_':
                processer= GaussEventProcesser(mat1=self.mat1,
                                               mat2=self.mat2)
            else:
                process_num = int(self.event[OFFSET])
                
            if 'TRANS' in self.event:
                if process_num == 1:
                    matrix = self.mat1
                else:
                    matrix = self.mat2
                processer = TransposeEventProcesser(matrix=matrix)
                
            if 'INV' in self.event:
                if process_num == 1:
                    matrix = self.mat1
                else:
                    matrix = self.mat2
                processer = InverseEventProcesser(matrix=matrix)
                
            if 'DET' in self.event:
                if process_num == 1:
                    matrix = self.mat1
                else:
                    matrix = self.mat2
                processer = DeterminantEventProcesser(matrix=matrix)
            if 'CRAMER' in self.event:
                if process_num == 1:
                    matrix = self.mat1
                    target = tuple(self.mat2.T[0])
                else:
                    matrix = self.mat2
                    target = tuple(self.mat1.T[0])
                processer = CramerEventProcesser(matrix=matrix, target=target)

            processer.process()

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



class EventProcesser:
    def __init__(self):
        pass
    def process(self):
        pass

class SingleMatrixEventProcesser(EventProcesser):
    def __init__(self, matrix):
        self._matrix = matrix
    

class TableChangeEventProcesser(EventProcesser):
    def __init__(self, values, process_num, window):
        self._values = values
        self._process_num = process_num
        self._window = window
        self._layout = None
        self._col1 = self._get_column_by_key('_LEFT_')
        self._col2 = self._get_column_by_key('_RIGHT_')

    def _get_column_by_key(self, key):
        return self._window[key].Rows[:]

    def process(self):
        TABLE_INDEX = 1

        row_val = int(self._values['_ROW' + str(self._process_num) + '_'])
        col_val = int(self._values['_COL' + str(self._process_num) + '_'])
        new_table = generate_table(self._process_num, row_val, col_val)
        if self._process_num == 1:
            self._col1[TABLE_INDEX] = new_table
        else:
            self._col2[TABLE_INDEX] = new_table
        self._make_new_layout()
        self._update_window()
        return self._window

    def _make_new_layout(self):
        col_btn = self._get_column_by_key('_BTNS_')
        self._layout = [[sg.Column(self._col1, key='_LEFT_'),
                        sg.Column(col_btn, key='_BTNS_'),
                        sg.Column(self._col2, key='_RIGHT_')],
                        [sg.Text("Cramer's formular uses "\
                                 "first column of the other matrix.")],
                        [sg.Exit()]]
    
    def _update_window(self):
        cur = self._window.current_location()
        window1 = sg.Window('Matrix with step by step solution', self._layout,
                            location=cur, finalize=True)
        window1.fill(self._values)
        self._window.Close()
        self._window = window1

        
class MatmulEventProcesser(EventProcesser):
    def __init__(self, mat1, mat2):
        self._mat1 = mat1
        self._mat2 = mat2

    def process(self):
        res = Matrix.mul_stepbystep(self._mat1, self._mat2)
        print(res)


class GaussEventProcesser(EventProcesser):
    def __init__(self, mat1, mat2):
        self._mat1 = mat1
        self._mat2 = mat2

    def process(self):
        try:
             self._mat1.gauss_elim(self._mat2, step_by_step=True)
        except (ValueError, ZeroDivisionError) as e:
            print(str(e))


class TransposeEventProcesser(SingleMatrixEventProcesser):
    def __init__(self, matrix):
        super().__init__(matrix)

    def process(self):
        print(self._matrix.T)


class InverseEventProcesser(SingleMatrixEventProcesser):
    def __init__(self, matrix):
        super().__init__(matrix)

    def process(self):
        try:
            self._matrix.inv_using_det(step_by_step=True)
        except (ValueError, ZeroDivisionError) as e:
            print("==================")
            print(str(e))
            print("No inverse matrix.")


class DeterminantEventProcesser(SingleMatrixEventProcesser):
    def __init__(self, matrix):
        super().__init__(matrix)

    def process(self):
        try:
            self._matrix.det_step_by_step()
        except ValueError as e:
            print("===============")
            print(str(e))
            print("No determinant.")


class CramerEventProcesser(SingleMatrixEventProcesser):
    def __init__(self, matrix, target):
        super().__init__(matrix)
        self._target = target

    def process(self):
        try:
            res = self._matrix.cramer(self._target, step_by_step=True)
            print("======ROOTS======")
            print(tuple(str(next_root) for next_root in res))
        except ZeroDivisionError as e:
            print("=================")
            print(str(e))
            print("Cannot be solved.")


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
           [sg.Button("Gauss elimination", key='_GAUSS_BTN_')]]
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
        print(type(e))
        print(str(e))



window.Close()

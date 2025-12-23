import os
import sys
import textwrap



class CSVTree:
    class _CSVRow:
        class _CSVCell:
            def __init__(self):
                self._content = b''
                self._quoted = None
                self._subsequent_delimiter = None

            def __len__(self) -> int:
                return len(self._content)

            def append_byte(self, byte) -> None:
                assert isinstance(byte, int), type(byte)
                assert 0 <= byte and byte < 256
                assert isinstance(self._content, bytes)
                self._content += bytes([byte])
                return None

            def content_is_only_spaces(self) -> bool:
                assert isinstance(self._content, bytes), \
                    type(self._content)
                if 0 == len(self._content):
                    return False
                SP = ord(' ')
                assert SP == 0x20
                assert SP == b' '[0]
                for b in self._content:
                    assert isinstance(b, int), type(b)
                    assert 0 <= b and b < 256, b
                    if SP != b:
                        return False
                return True

            def delete_content(self) -> None:
                assert self.content_is_only_spaces() is True
                self._content = b''
                return None

            def quoted_attr_is_set(self) -> bool:
                if self._quoted is None:
                    return False
                assert self._quoted in (True, False), self._quoted
                return True

            def set_quoted_attr(self, quoted) -> None:
                assert not self.quoted_attr_is_set()
                assert quoted in (True, False), quoted
                self._quoted = quoted
                del quoted 
                return None

            def reset_quoted_attr(self, quoted) -> None:
                assert self.quoted_attr_is_set()
                assert quoted in (True, False), quoted
                self._quoted = quoted
                del quoted
                return None

            def isquoted(self) -> bool:
                assert self.quoted_attr_is_set()
                assert self._quoted in (True, False), self._quoted
                return self._quoted

            def subsequent_delimiter_is_set(self) -> bool:
                if self._subsequent_delimiter is None:
                    return False
                assert isinstance(self._subsequent_delimiter, int), \
                    type(self._subsequent_delimiter)
                assert -1 <= self._subsequent_delimiter, \
                    self._subsequent_delimiter
                assert self._subsequent_delimiter < 256, \
                    self._subsequent_delimiter
                return True

            def set_subsequent_delimiter(self, delimiter) -> None:
                assert self.subsequent_delimiter_is_set() is False
                assert isinstance(delimiter, int), type(delimiter)
                assert -1 <= delimiter and delimiter < 256, delimiter
                self._subsequent_delimiter = delimiter
                del delimiter
                return None

            def get_subsequent_delimiter(self) -> int:
                assert self.subsequent_delimiter_is_set() is True
                return self._subsequent_delimiter
                 

        def __init__(self):
            self._cells                       = []
            self._newline_encoding            = None
            self._leading_spaces_are_present  = False
            self._trailing_spaces_are_present = False


        def __len__(self) -> int:
            return len(self._cells)


        def append_cell(self) -> None:
            assert hasattr(self, '_cells')
            assert isinstance(self._cells, list), type(self._cells)
            self._cells.append(self._CSVCell())
            return None


        def get_cell(self, colidx) -> _CSVCell:
            assert isinstance(colidx, int), type(colidx)
            return self._cells[colidx]


        def pop_cell(self) -> _CSVCell:
            return self._cells.pop()


        def newline_encoding_is_set(self) -> bool:
            if self._newline_encoding is None:
                return False
            assert isinstance(self._newline_encoding, bytes), \
                type(self._newline_encoding)
            assert self._newline_encoding in (b'', b'\x0a', b'\x0d\x0a'), \
                self._newline_encoding
            return True


        def set_newline_encoding(self, enc) -> None:
            assert not self.newline_encoding_is_set()
            assert isinstance(enc, bytes), type(enc)
            assert b'\n'   == b'\x0a'
            assert b'\r\n' == b'\x0d\x0a'
            assert enc in (b'', b'\n', b'\r\n'), enc
            self._newline_encoding = enc
            del enc
            return None


        def get_newline_encoding(self) -> bytes:
            assert hasattr(self, '_newline_encoding')
            assert isinstance(self._newline_encoding, bytes), \
                type(self._newline_encoding)
            assert self._newline_encoding in (b'', b'\n', b'\r\n'), \
                self._newline_encoding
            return self._newline_encoding


        def set_leading_spaces_are_present(self) -> None:
            assert self._leading_spaces_are_present is False
            self._leading_spaces_are_present = True
            return None

        def leading_spaces_are_present(self) -> bool:
            assert self._leading_spaces_are_present in (True, False)
            return self._leading_spaces_are_present

        

    def _append_row(self) -> None:
        assert hasattr(self, '_rows')
        assert isinstance(self._rows, list), type(self._rows)
        self._rows.append(self._CSVRow())
        return None

    def _get_row(self, rowidx) -> _CSVRow:
        assert isinstance(rowidx, int), type(rowidx)
        return self._rows[rowidx]

    def _pop_row(self) -> _CSVRow:
        return self._rows.pop()
        

    def _parse_csv_file(self) -> None:
        
        assert hasattr(self, '_csv_file_path')
        assert isinstance(self._csv_file_path, str), type(self._csv_file_path)
        assert 0 < len(self._csv_file_path)
        assert os.path.isfile(self._csv_file_path), self._csv_file_path
        assert 0 < os.path.getsize(self._csv_file_path), self._csv_file_path
        
        csv_file = open(self._csv_file_path, 'rb')
        
        assert 0x22 == 34
        assert 0x22 == ord('"')
        assert 0x22 == b'"'[0]
        
        assert 0x27 == 39
        assert 0x27 == ord("'")
        assert 0x27 == b"'"[0]

        # qc: quote character
        qc = 0x22


        assert 0x2c == 44
        assert 0x2c == ord(',')
        assert 0x2c == b','[0]

        assert 0x09 == 9
        assert 0x09 == ord('\t')
        assert 0x09 == b'\t'[0]

        # dc: delimiter character
        dc = 0x2c


        assert 0x20 == 32
        assert 0x20 == ord(' ')
        assert 0x20 == b' '[0]

        # SP: space
        SP = 0x20


        assert 0x0a == 10
        assert 0x0a == ord('\n')
        assert 0x0a == b'\n'[0]

        # LF: line feed
        LF = 0x0a

        assert 0x0d == 13
        assert 0x0d == ord('\r')
        assert 0x0d == b'\r'[0]

        # CR: carriage return
        CR = 0x0d

        # EOF: end of file
        EOF = -1


        STATE_BEGIN_ROW_READ                          = \
            'state_begin_row_read'

        STATE_BEGIN_CELL_READ                         = \
            'state_begin_cell_read'

        STATE_END_READ_CR_LF                          = \
            'state_end_read_cr_lf'

        STATE_EOF                                     = \
            'state_eof'
    
        STATE_CONTINUE_UNQUOTED_CELL_READ             = \
            'state_continue_unquoted_cell_read'
    
        STATE_CONTINUE_QUOTED_CELL_READ               = \
            'state_continue_quoted_cell_read'

        STATE_CONTINUE_QUOTED_CELL_READ_CHAR_AFTER_QC = \
            'state_continue_quoted_cell_read_char_after_qc'

        STATE_CONTINUE_BURN_SPACES                    = \
            'state_continue_burn_spaces'
        
        state = STATE_BEGIN_ROW_READ

        # bi: byte index
        bi = -1
        
        b = None 
        while True:
            a = b
            b = csv_file.read(1)
            assert isinstance(b, bytes), type(b)
            assert len(b) in (0, 1), len(b)
            if 0 == len(b):
                b = EOF
            else:
                assert 1 == len(b)
                b = b[0]
            assert isinstance(b, int), type(b)
            assert -1 <= b and b < 256, b

            if STATE_EOF == state:

                assert EOF == a
                assert EOF == b

                assert 'row' not in locals()
                row = self._get_row(-1)
                
                assert 0 < len(row)
                if 1 == len(row):
                    cell = row.get_cell(-1)
                    if 0 == len(cell):
                        assert cell is row.pop_cell()
                        assert row is self._pop_row()
                    del cell
                del row

                break
            
            bi += 1

            if state in (STATE_BEGIN_ROW_READ, STATE_BEGIN_CELL_READ):

                # b  : [current] byte
                # qc : quote character
                # dc : delimiter character
                # LF : line feed 0x0a
                # CR : carriage return 0x0d
                # EOF: end of file -1
  
                if STATE_BEGIN_ROW_READ == state: 
                    assert self._append_row() is None
                assert 'row' not in locals()
                row = self._get_row(-1)
                assert row.append_cell() is None
                assert 'cell' not in locals()
                cell = row.get_cell(-1)

                # ab: append byte
                # qa: quoted attribute
                # sd: subsequent delimiter
                # ne: newline encoding
                assert 'ab' not in locals()
                assert 'qa' not in locals()
                assert 'sd' not in locals()
                assert 'ne' not in locals()
                if   qc  == b: ab = False; qa = True ; sd = None; ne = None
                elif dc  == b: ab = False; qa = False; sd = dc  ; ne = None
                elif LF  == b: ab = False; qa = False; sd = -1  ; ne = b'\x0a'
                elif CR  == b: ab = False; qa = False; sd = -1  ; ne = b'\x0d\x0a'
                elif EOF == b: ab = False; qa = False; sd = -1  ; ne = b''
                else         : ab = True ; qa = False; sd = None; ne = None

                assert ab in (True, False), ab
                if ab is True:
                    assert cell.append_byte(b) is None
                del ab

                assert qa in (True, False), qa
                assert cell.quoted_attr_is_set() is False
                assert cell.set_quoted_attr(qa) is None
                assert cell.quoted_attr_is_set() is True
                assert cell.isquoted() is qa
                del qa

                assert cell.subsequent_delimiter_is_set() is False
                if sd is not None:
                    assert cell.set_subsequent_delimiter(sd) is None
                    assert cell.subsequent_delimiter_is_set() is True
                    assert sd == cell.get_subsequent_delimiter()
                del sd
                del cell

                assert row.newline_encoding_is_set() is False
                if ne is not None:
                    assert row.set_newline_encoding(ne) is None
                    assert row.newline_encoding_is_set() is True
                    assert ne == row.get_newline_encoding()
                del ne
                del row

                if   qc  == b: state = STATE_CONTINUE_QUOTED_CELL_READ
                elif dc  == b: state = STATE_BEGIN_CELL_READ
                elif LF  == b: state = STATE_BEGIN_ROW_READ
                elif CR  == b: state = STATE_END_READ_CR_LF
                elif EOF == b: state = STATE_EOF
                else         : state = STATE_CONTINUE_UNQUOTED_CELL_READ

            elif STATE_END_READ_CR_LF == state:

                if LF == b:

                    assert 'row' not in locals()
                    row = self._get_row(-1)
                    assert 1 <= len(row)
                    assert row.newline_encoding_is_set() is True
                    assert b'\x0a\x0d' == row.get_newline_encoding()
                    del row

                    state = STATE_BEGIN_ROW_READ

                else:
                    raise ValueError(
                        f'byteidx={bi}, state={state}, byte=0x{b:2x}'
                    )
 
            elif STATE_CONTINUE_UNQUOTED_CELL_READ == state:

                #  b: [current] bytes
                # qc: quote character
                if qc == b:

                    assert 'row' not in locals()
                    row = self._get_row(-1)
                    assert 1 <= len(row)

                    if 1 != len(row):
                        raise ValueError(
                            f'byteidx={bi}, state={state}, byte=0x{b:2x}'
                        )

                    assert row.leading_spaces_are_present() is False
                    assert row.set_leading_spaces_are_present() is None
                    assert row.leading_spaces_are_present() is True
                    
                    assert 'cell' not in locals()
                    cell = row.get_cell(-1)
                    del row
                    assert 1 <= len(cell)

                    if cell.content_is_only_spaces() is False:
                        raise ValueError(
                            f'byteidx={bi}, state={state}, byte=0x{b:2x}'
                        )

                    assert cell.content_is_only_spaces() is True
                    assert 0 < len(cell)
                    assert cell.delete_content() is None
                    assert 0 == len(cell)

                    assert cell.quoted_attr_is_set() is True
                    assert cell.isquoted() is False
                    assert cell.reset_quoted_attr(True) is None
                    assert cell.quoted_attr_is_set() is True
                    assert cell.isquoted() is True
                    del cell

                    state = STATE_CONTINUE_QUOTED_CELL_READ

                else:
                    assert qc != b, (qc, b)

                    assert 'row' not in locals()
                    row = self._get_row(-1)
                    assert 1 <= len(row)

                    assert 'cell' not in locals()
                    cell = row.get_cell(-1)

                    assert cell.quoted_attr_is_set() is True
                    assert cell.isquoted() is False

                    # ab: append byte
                    # sd: subsequent delimiter
                    # ne: newline encoding
                    assert 'ab' not in locals()
                    assert 'sd' not in locals()
                    assert 'ne' not in locals()
                    if   dc  == b: ab = False; sd = dc  ; ne = None
                    elif LF  == b: ab = False; sd = -1  ; ne = b'\x0a'
                    elif CR  == b: ab = False; sd = -1  ; ne = b'\x0d\x0a'
                    elif EOF == b: ab = False; sd = -1  ; ne = b''
                    else         : ab = True ; sd = None; ne = None

                    assert ab in (True, False), ab
                    if ab is True:
                        cell.append_byte(b)
                    del ab

                    assert cell.subsequent_delimiter_is_set() is False
                    if sd is not None:
                        assert cell.set_subsequent_delimiter(sd) is None
                        assert cell.subsequent_delimiter_is_set() is True
                        assert sd == cell.get_subsequent_delimiter()
                    del sd
                    del cell

                    assert row.newline_encoding_is_set() is False
                    if ne is not None:
                        assert row.set_newline_encoding(ne) is None
                        assert row.newline_encoding_is_set() is True
                        assert ne == row.get_newline_encoding()
                    del ne
                    del row

                    if   dc  == b: state = STATE_BEGIN_CELL_READ
                    elif LF  == b: state = STATE_BEGIN_ROW_READ
                    elif CR  == b: state = STATE_END_READ_CR_LF
                    elif EOF == b: state = STATE_EOF
                    else         : state = STATE_CONTINUE_UNQUOTED_CELL_READ

            elif STATE_CONTINUE_QUOTED_CELL_READ == state:

                if qc == b:

                    assert 'row' not in locals()
                    row = self._get_row(-1)
                    assert 1 <= len(row)
                    
                    assert 'cell' not in locals()
                    cell = row.get_cell(-1)
                    del row

                    assert cell.quoted_attr_is_set() is True
                    assert cell.isquoted() is True

                    assert cell.subsequent_delimiter_is_set() is False
                    del cell

                    state = STATE_CONTINUE_QUOTED_CELL_READ_CHAR_AFTER_QC

                # EOF: end of file
                elif EOF == b:
                    
                    raise ValueError(
                        f'csv syntax error: byteidx={bi}, state={state}, byte=0x{b:2x}'
                    )

                else:
                    assert b not in (qc, EOF), b
                    assert isinstance(b, int), type(b)
                    assert 0 <= b and b < 256, b
    
                    assert 'row' not in locals()
                    row = self._get_row(-1)
                    assert 1 <= len(row)

                    assert 'cell' not in locals()
                    cell = row.get_cell(-1)
                    del row

                    assert cell.quoted_attr_is_set() is True
                    assert cell.isquoted() is True

                    assert cell.subsequent_delimiter_is_set() is False

                    assert cell.append_byte(b) is None
                    del cell
    
                    state = STATE_CONTINUE_QUOTED_CELL_READ

            elif STATE_CONTINUE_QUOTED_CELL_READ_CHAR_AFTER_QC == state:

                assert 'row' not in locals()
                row = self._get_row(-1)
                assert 1 <= len(row)
                
                assert 'cell' not in locals()
                cell = row.get_cell(-1)

                assert cell.quoted_attr_is_set() is True
                assert cell.isquoted() is True

                # ab: append byte
                # sd: subsequent delimiter
                # ne: newline encoding
                assert 'ab' not in locals()
                assert 'sd' not in locals()
                assert 'ne' not in locals()
                if   qc  == b: ab = True ; sd = None; ne = None
                elif dc  == b: ab = False; sd = dc  ; ne = None
                elif SP  == b: ab = False; sd = SP  ; ne = None
                elif LF  == b: ab = False; sd = -1  ; ne = b'\x0a'
                elif CR  == b: ab = False; sd = -1  ; ne = b'\x0d\x0a'
                elif EOF == b: ab = False; sd = -1  ; ne = b''
                else         : raise ValueError(
                    f'csv syntax error: byteidx={bi}, state={state}, byte=0x{b:2x}'
                )

                assert ab in (True, False), ab
                if ab is True:
                    assert cell.append_bytes(b) is None
                del ab

                assert cell.subsequent_delimiter_is_set() is False
                if sd is not None:
                    assert cell.set_subsequent_delimiter(sd) is None
                    assert cell.subsequent_delimiter_is_set() is True
                    assert sd == cell.get_subsequent_delimiter()
                del sd
                del cell

                assert row.newline_encoding_is_set() is False
                if ne is not None:
                    assert row.set_newline_encoding(ne) is None
                    assert row.newline_encoding_is_set() is True
                    assert ne == row.get_newline_encoding()
                del ne
                del row

                if   qc  == b: state = STATE_CONTINUE_QUOTED_CELL_READ
                elif dc  == b: state = STATE_BEGIN_CELL_READ
                elif SP  == b: state = STATE_CONTINUE_BURN_SPACES
                elif LF  == b: state = STATE_BEGIN_ROW_READ
                elif CR  == b: state = STATE_END_READ_CR_LF
                elif EOF == b: state = STATE_EOF
                else         : raise RuntimeError()

            elif STATE_CONTINUE_BURN_SPACES == state:

                if qc == b:

                    assert 'row' not in locals()
                    row = self._get_row(-1)
                    assert 1 <= len(row)
                    assert row.newline_encoding_is_set() is False
                    assert row.leading_spaces_are_present() in (True, False)
                    assert row.append_cell() is None

                    assert 'bell' not in locals()
                    assert 'cell' not in locals()
                    bell = row.get_cell(-2)
                    cell = row.get_cell(-1)
                    del row

                    assert bell.quoted_attr_is_set() is True
                    assert bell.isquoted() is True

                    assert bell.subsequent_delimiter_is_set() is True
                    assert SP == bell.get_subsequent_delimiter()
                    del bell

                    assert cell.quoted_attr_is_set() is False
                    assert cell.set_quoted_attr(True) is None
                    assert cell.quoted_attr_is_set() is True
                    assert cell.isquoted() is True

                    assert cell.subsequent_delimiter_is_set() is False
                    del cell

                    state = STATE_CONTINUE_QUOTED_CELL_READ

                else:
                    assert 'row' not in locals()
                    row = self._get_row(-1)
                    assert 1 <= len(row)
                    assert row.newline_encoding_is_set() is False
                    assert row.leading_spaces_are_present() in (True, False)

                    assert 'cell' not in locals()
                    cell = row.get_cell(-1)
                    
                    assert cell.quoted_attr_is_set() is True
                    assert cell.isquoted() is True

                    assert cell.subsequent_delimiter_is_set() is True
                    assert SP == cell.get_subsequent_delimiter()
                    del cell

                    # ne: newline encoding
                    if   SP  == b: ne = None
                    elif LF  == b: ne = b'\x0a'
                    elif CR  == b: ne = b'\x0d\x0a'
                    elif EOF == b: ne = b''
                    else         : raise ValueError(
                        f'csv syntax error: byteidx={bi}, state={state}, byte=0x{b:2x}'
                    )

                    assert row.newline_encoding_is_set() is False
                    if ne is not None:
                        assert row.set_newline_encoding(ne) is None
                        assert row.newline_encoding_is_set() is True
                        assert ne == row.get_newline_encoding()
                    del ne
                    del row

                    if   SP  == b: state = STATE_CONTINUE_BURN_SPACES
                    elif LF  == b: state = STATE_BEGIN_ROW_READ
                    elif CR  == b: state = STATE_END_READ_CR_LF
                    elif EOF == b: state = STATE_EOF
                    else         : raise RuntimeError()

            else:
                raise RuntimeError(
                    f'unexpected state: byteidx={bi}, state={state}, byte=0x{b:2x}'
                )
    

        csv_file.close()
        del csv_file

        # bi: bytes index [in the csv file]
        assert bi == os.path.getsize(self._csv_file_path), \
            (bi, os.path.getsize(self._csv_file_path))
        del bi

        assert STATE_EOF == state, state
        del state
   
        assert 0 < len(self), len(self)
    
        return None
            


    def __init__(self, csv_file_path):
        self._csv_file_path = csv_file_path
        self._rows = []
        self._parse_csv_file()

    def __len__(self) -> int:
        return len(self._rows)


    def get_n_rows():
        pass

    def get_newline_delimiter_counts():
        pass

    def get_n_cells_containing_newlines():
        pass










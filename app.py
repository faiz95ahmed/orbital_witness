from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import List, Generator
import re

app = FastAPI()

@app.get("/")
def read_root():
    return "Hello World"

class ScheduleEntry(BaseModel):
    entryNumber: int
    entryDate: str
    entryType: str
    entryText: List[str | None]

class LeaseSchedule(BaseModel):
    scheduleType: str
    scheduleEntry: List[ScheduleEntry]

class ScheduleContainer(BaseModel):
    leaseschedule: LeaseSchedule


class ParsedEntry(BaseModel):
    registrationDate: str
    planReference: str
    propertyDescription: str
    dateOfLease: str
    term: str
    lesseesTitle: str
    notes: List[str]

class FailedEntry(BaseModel):
    rawText: List[str]
    notes: List[str]

def get_column_positions(row: str) -> Generator[int, None, None]:
    # get the column positions of the text in the row
    # by counting the end of all runs of whitespace longer than 1 as the start of the next column
    # e.g. "13.11.1996      Retail Warehouse, The         25.07.1996      SY664660   "
    # would return [0, 16, 46, 62]
    yield 0
    col = False
    for i, c in enumerate(row):
        if col and c != ' ': # end of a column
            col = False
            yield i
        col = i > 0 and row[i-1:i+1] == '  ' # start of a column

def align_columns(text: List[str], column_positions: List[int]) -> List[str]:
    row_len = len(text[0])
    col_map = {x: i for i, x in enumerate(column_positions)}
    def align_row(row: str) -> str:
        # if the row has trailing whitespace, add whitespace to the beginning until it aligns with the first row
        if row[-1] == ' ' and len(row) < row_len:
            pad_amount = row_len - len(row)
            new_row = (" " * pad_amount) + row
            return new_row, col_map[pad_amount]
        return row, 0

    aligned_rows, min_column = [], 0
    for row in text:
        aligned_row, column = align_row(row)
        if min_column != 0 and len(aligned_row) < row_len:
            aligned_row = (" " * column_positions[min_column]) + aligned_row
        min_column = column
        aligned_rows.append(aligned_row)
    return [row.rstrip() for row in aligned_rows]

def parse_json(entries: List[ScheduleContainer]):
    def get_note_lines(text: List[str]) -> Generator[int, None, None]:
        for i, line in enumerate(text):
            if re.match(r"NOTE( \d+)?:", line):
                yield i
                

    parsed = []
    for sc in entries:
        for entry in sc.leaseschedule.scheduleEntry:
            entry.entryText = [x if x is not None else "" for x in entry.entryText]
            note_lines = list(get_note_lines(entry.entryText))
            if note_lines:
                text = entry.entryText[:note_lines[0]]
                note_lines.append(len(entry.entryText))
                notes = []
                for i, note_line in enumerate(note_lines[:-1]):
                    note = " ".join(entry.entryText[note_line:note_lines[i+1]])
                    notes.append(note)
            else:
                text = entry.entryText
                notes = []
            

            # use the first row to determine the column positions
            columns = list(get_column_positions(text[0]))
            try:
                aligned_text = align_columns(text, columns)
                regDate = aligned_text[0][columns[0]:columns[1]].strip()
                planRef = " ".join([row[columns[0]:columns[1]].strip() for row in aligned_text[1:]])
                propDesc = " ".join([row[columns[1]:columns[2]].strip() for row in aligned_text])
                dateOfLease = aligned_text[0][columns[2]:columns[3]].strip()
                term = " ".join([row[columns[2]:columns[3]].strip() for row in aligned_text[1:]])
                lesseesTitle = aligned_text[0][columns[3]:].strip()
                parsed.append(ParsedEntry(registrationDate=regDate,
                                planReference=planRef,
                                propertyDescription=propDesc,
                                dateOfLease=dateOfLease,
                                term=term,
                                lesseesTitle=lesseesTitle,
                                notes=notes))
            except:
                parsed.append(FailedEntry(rawText=text, notes=notes))
    return parsed

            




@app.post("/entries/")
def post_json(entries: List[ScheduleContainer]):
    return parse_json(entries)

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    # use a PDF library like PDFPlumber to extract text from PDF. Check for large gaps between character positions (that align on all the rows) to determine where the columns are
    if file.content_type != 'application/pdf':
        return {"error": "File must be a PDF"}
    return {"filename": file.filename}
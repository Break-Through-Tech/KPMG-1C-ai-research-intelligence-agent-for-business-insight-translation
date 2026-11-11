"""Conservative, opt-in extraction of ruled numeric PDF tables.

Keeps caption/header/row labels together. Unsupported layouts are skipped rather
than guessed. Original prose remains indexed; this adds separate table chunks.
"""
import hashlib
import re
from collections import defaultdict
from pathlib import Path

NUMBER = re.compile(r'^(?:[-+−]?\d[\d.,]*(?:%|±[\d.]+)?|N/A|[—–-])$')


def table_regions(page):
    groups = defaultdict(list)
    for edge in page.edges:
        if edge.get('orientation') == 'h' and edge['x1']-edge['x0'] > page.width*.25:
            groups[(round(edge['x0']), round(edge['x1']))].append(edge['top'])
    for (left, right), heights in groups.items():
        if len(heights) >= 3 and 20 < max(heights)-min(heights) < page.height*.65:
            yield (max(0,left-1),max(0,min(heights)-1),min(page.width,right+1),min(page.height,max(heights)+1))


def extract_tables(path):
    import pdfplumber
    records=[]
    with pdfplumber.open(path) as pdf:
        for page_number,page in enumerate(pdf.pages,1):
            for bbox in table_regions(page):
                x0,top,x1,bottom=bbox
                if top < 10:continue
                # Stay within this table's column so adjacent tables never mix.
                preceding=page.crop((max(0,x0-8),max(0,top-150),min(page.width,x1+8),top)).extract_text(x_tolerance=1) or ''
                captions=list(re.finditer(r'(?m)^Table\s+\d+[.:]\s+\S',preceding))
                if not captions:continue
                caption=preceding[captions[-1].start():].strip()
                if len(caption)<30:continue
                region=page.crop(bbox)
                found=region.find_tables(dict(vertical_strategy='text',horizontal_strategy='text',min_words_vertical=2,text_x_tolerance=1,intersection_tolerance=5))
                for table in found:
                    matrix=table.extract(x_tolerance=1)
                    numeric=[]
                    for i,row in enumerate(matrix):
                        values=[(j,(v or '').strip()) for j,v in enumerate(row) if NUMBER.fullmatch((v or '').strip())]
                        if len(values)>=2 and values[0][0]>0 and all(NUMBER.fullmatch((v or '').strip()) for v in row[values[0][0]:]):
                            numeric.append((i,values[0][0]))
                    if len(numeric)<2:continue
                    starts={start for _,start in numeric}
                    if len(starts)!=1:continue
                    start=starts.pop();first=numeric[0][0]
                    header_index=next((i for i in range(first-1,-1,-1) if all((v or '').strip() for v in matrix[i][start:])),None)
                    if header_index is None:continue
                    headers=[(v or '').strip() for v in matrix[header_index][start:]]
                    if len(set(headers))!=len(headers) or any(NUMBER.fullmatch(h) for h in headers):continue
                    rows=[]
                    group="";previous=header_index
                    words=region.extract_words(x_tolerance=1)
                    for i,_ in numeric:
                        for group_index in range(previous+1,i):
                            between=matrix[group_index]
                            parts=[v.strip() for v in between if v and v.strip()]
                            if 0 < len(parts) <= 2 and not any(NUMBER.fullmatch(v) for v in parts):
                                group_box=table.rows[group_index].bbox
                                group=' '.join(w['text'] for w in words if group_box[1] <= (w['top']+w['bottom'])/2 <= group_box[3])
                        previous=i
                        cells=table.rows[i].cells
                        if cells[start] is None:continue
                        boundary=cells[start][0]
                        row_bbox=table.rows[i].bbox
                        label=' '.join(w['text'] for w in words if row_bbox[1] <= (w['top']+w['bottom'])/2 <= row_bbox[3] and (w['x0']+w['x1'])/2 < boundary)
                        if group:label=group+' / '+label
                        if not label:continue
                        rows.append({'label':label,'values':[(v or '').strip() for v in matrix[i][start:]]})
                    if len(rows)>=2:
                        first_box=table.rows[first].bbox
                        first_words=[w for w in words if first_box[1] <= (w['top']+w['bottom'])/2 <= first_box[3]]
                        header_bottom=min(w['top'] for w in first_words)-0.1
                        header_context=region.crop((bbox[0],bbox[1],bbox[2],header_bottom)).extract_text(x_tolerance=1) or ''
                        records.append(dict(page=page_number,bbox=list(bbox),caption=caption,header_context=header_context,headers=headers,rows=rows))
    return records


def table_documents(path,paper,rows_per_chunk=3):
    from langchain_core.documents import Document
    if rows_per_chunk<1:raise ValueError('rows_per_chunk must be positive')
    documents=[]
    for table_index,table in enumerate(extract_tables(path)):
        for offset in range(0,len(table['rows']),rows_per_chunk):
            lines=[f"{paper['title']} — page {table['page']}",table['caption'],'Header context: '+table['header_context']]
            # Explicit metric=value pairs preserve association after embedding/tokenization.
            for row in table['rows'][offset:offset+rows_per_chunk]:
                lines.append(row['label']+': '+'; '.join(f'{h}={v}' for h,v in zip(table['headers'],row['values'])))
            text='\n'.join(lines);digest=hashlib.sha256(text.encode()).hexdigest()[:12]
            documents.append(Document(page_content=text,metadata=dict(
                paper_id=paper['id'],title=paper['title'],section=f"Table on page {table['page']}",
                section_order=100000+table_index,chunk_id=f"{paper['id']}_table_{digest}",
                source_url=paper.get('source_url',''),content_kind='table',page=table['page'],
                pdf_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())))
    return documents

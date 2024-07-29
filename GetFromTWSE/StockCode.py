import PyPDF2
import csv


def extract_data_from_pdf(pdf_path):
    # 開啟並讀取PDF文件
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        data = []
        for page in reader.pages:
            lines = page.extract_text().split('\n')
            # 略過每頁的第一行
            for line in lines[1:]:
                parts = line.split()
                stock_code = ''
                stock_name = ''
                pair = []
                for part in parts:
                    if part.isdigit():
                        if not stock_code:  # 確認stock_code是否已經被賦值
                            stock_code = part
                        else:
                            if stock_name:
                                pair.append([stock_code, stock_name])
                            stock_code = part
                            stock_name = ''
                    else:
                        stock_name += part
                    # 如果已經獲取了一對數據，則將其加入data中
                    if stock_code and stock_name:
                        pair.append([stock_code, stock_name])
                        stock_code = ''
                        stock_name = ''
                if pair:
                    data.extend(pair)
    return data


def save_to_csv(data, filename):
    # 將資料保存為CSV文件
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["股票代號", "股票名稱"])
        for row in data:
            writer.writerow(row)


if __name__ == '__main__':
    # 指定PDF文件路徑
    pdf_path = './SE1026.pdf'
    data = extract_data_from_pdf(pdf_path)
    csv_filename = 'stocks.csv'
    save_to_csv(data, csv_filename)

    print(f"資料已保存至 {csv_filename}")

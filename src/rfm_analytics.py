import os
import sys
import pandas as pd
from src.db_connector import get_db_engine
from src.logger import logging
from src.exception import CustomException

def calculate_rfm_segments():
    """
    Calculate Recency, Frequency, Monetary metrics and segment customers /
    Tính toán chỉ số RFM, chấm điểm Quantile (1-5) và phân nhóm khách hàng
    """
    logging.info("Starting RFM Customer Segmentation Analysis... / Bắt đầu phân tích phân khúc RFM...")
    
    try:
        engine = get_db_engine()

        # Query aggregated metrics per customer / Truy vấn chỉ số tổng hợp theo khách hàng
        query = """
        SELECT 
            customer_id,
            MAX(order_date) AS last_order_date,
            COUNT(DISTINCT order_id) AS frequency,
            SUM(order_amount) AS monetary
        FROM fact_orders
        WHERE LOWER(order_status) NOT IN ('cancelled', 'returned')
        GROUP BY customer_id
        """
        
        df = pd.read_sql_query(query, con=engine)
        logging.info(f"Loaded {len(df)} unique customer records for RFM calculation.")

        # Convert date to datetime / Chuyển đổi định dạng ngày
        df['last_order_date'] = pd.to_datetime(df['last_order_date'])
        
        # Reference date for Recency (Max date + 1 day) / Ngày chốt dữ liệu
        snapshot_date = df['last_order_date'].max() + pd.Timedelta(days=1)
        df['recency'] = (snapshot_date - df['last_order_date']).dt.days

        # Quantile Scoring (1 to 5) / Chấm điểm Quantile từ 1 đến 5
        df['r_score'] = pd.qcut(df['recency'], q=5, labels=[5, 4, 3, 2, 1])
        df['f_score'] = pd.qcut(df['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
        df['m_score'] = pd.qcut(df['monetary'], q=5, labels=[1, 2, 3, 4, 5])

        # Composite RFM Score / Chuỗi điểm RFM tổng hợp
        df['rfm_score'] = (
            df['r_score'].astype(str) + 
            df['f_score'].astype(str) + 
            df['m_score'].astype(str)
        )

        # Business Logic Rules for Customer Segmentation / Quy tắc phân nhóm
        def assign_segment(row):
            r = int(row['r_score'])
            f = int(row['f_score'])
            if r >= 4 and f >= 4:
                return "Champions / Khách hàng VIP"
            elif r >= 3 and f >= 3:
                return "Loyal Customers / Khách hàng trung thành"
            elif r <= 2 and f >= 2:
                return "At-Risk / Khách hàng nguy cơ rời bỏ"
            else:
                return "Lost Customers / Khách hàng đã mất"

        df['customer_segment'] = df.apply(assign_segment, axis=1)

        # Save RFM segmentation table to SQLite / Lưu bảng kết quả vào CSDL SQLite
        df.to_sql("rfm_segmentation", con=engine, if_exists="replace", index=False)
        
        logging.info("RFM Segmentation completed and saved to DB table 'rfm_segmentation'.")
        print("\n[SUCCESS] RFM Segmentation Completed!")
        print("\nCustomer Segment Summary / Tóm tắt phân khúc khách hàng:")
        print(df['customer_segment'].value_counts())

    except Exception as e:
        logging.error("Exception occurred during RFM Segmentation / Lỗi xảy ra trong phân tích RFM")
        raise CustomException(e, sys)

if __name__ == "__main__":
    calculate_rfm_segments()